import os
import importlib.util

# Try to load the GoogleAdsClient dynamically to avoid import issues
GADS_AVAILABLE = False
try:
    site_packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'venv', 'Lib', 'site-packages'))
    if os.path.exists(site_packages_path):
        spec = importlib.util.find_spec("google.ads.google_ads.client", [site_packages_path])
    else:
        spec = importlib.util.find_spec("google.ads.google_ads.client")
    
    if spec:
        _GoogleAdsClient = spec.loader.load_module().GoogleAdsClient
        _GoogleAdsErrors = importlib.util.find_spec("google.ads.google_ads.errors").loader.load_module()
        GoogleAdsException = _GoogleAdsErrors.GoogleAdsException
        GADS_AVAILABLE = True
except (ImportError, AttributeError, ModuleNotFoundError) as e:
    print(f"Warning: Could not load Google Ads client: {e}")
    # Create placeholder class
    class GoogleAdsException(Exception):
        pass

class GoogleAdsClient:
    def __init__(self):
        self._client = None
        self._customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")

    def _init_client(self):
        if self._client is None and GADS_AVAILABLE:
            conn = None
            try:
                from marketing_agent.db import get_conn
                conn = get_conn()
                row = conn.execute("SELECT * FROM integrations WHERE platform = ?", ('google_ads',)).fetchone()
                
                if row and row['refresh_token']:
                    self._client = _GoogleAdsClient.load_from_dict({
                        "developer_token": row['developer_token'],
                        "client_id": row['client_id'],
                        "client_secret": row['client_secret'],
                        "refresh_token": row['refresh_token'],
                        "login_customer_id": row['customer_id']
                    }, version="v16")
                    self._customer_id = row['customer_id']
                else:
                    self._client = _GoogleAdsClient.load_from_storage(version="v16")
                    self._customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")

                if not self._customer_id:
                    raise Exception("GOOGLE_ADS_CUSTOMER_ID not set in .env or DB.")

            except Exception as e:
                raise Exception(f"Failed to initialize Google Ads client: {e}")
            finally:
                if conn:
                    conn.close()
        return self._client

    def list_campaigns(self):
        if not GADS_AVAILABLE:
            raise Exception("Google Ads library not available. Please install google-ads.")
        client = self._init_client()
        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.budget.amount_micros
            FROM
                campaign
            ORDER BY
                campaign.id
        """

        campaigns = []
        try:
            stream = ga_service.search_stream(customer_id=self._customer_id, query=query)
            for batch in stream:
                for row in batch.results:
                    campaigns.append({
                        "id": row.campaign.id,
                        "name": row.campaign.name,
                        "status": row.campaign.status.name,
                        "budget": row.campaign.budget.amount_micros / 1_000_000
                    })
        except GoogleAdsException as ex:
            print(f"Request with ID \"{ex.request_id}\" failed with status \"{ex.error.code().name}\"")
            for error in ex.errors:
                print(f"\tError with message \"{error.message}\".")
            raise
        return campaigns

    def create_campaign(self, name, budget, start_date=None, end_date=None):
        return f"Campaign {name} created on Google Ads (placeholder)"

    def create_ad_group(self, campaign_id, name):
        return f"Ad Group {name} created under campaign {campaign_id} (placeholder)"

    def create_text_ad(self, ad_group_id, headlines, descriptions):
        return f"Text ad created for ad group {ad_group_id} (placeholder)"

    def add_keywords(self, ad_group_id, keywords):
        return f"Keywords added to ad group {ad_group_id} (placeholder)"

    def get_campaign_performance(self, campaign_id, metrics):
        return {"clicks": 0, "impressions": 0, "cost": 0}

google_ads_client = GoogleAdsClient()
