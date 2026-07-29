import os
import importlib.util
import sys

# Attempt to find and load the google.ads.google_ads.client module
GADS_AVAILABLE = False
GOOGLE_ADS_CLIENT = None
GOOGLE_ADS_EXCEPTION = None

# Get the path to the site-packages directory within the hermes venv
site_packages_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'venv', 'Lib', 'site-packages'))

# Add site-packages to sys.path if not already present
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

try:
    # Try to find the module spec
    spec = importlib.util.find_spec("google.ads.google_ads.client", [site_packages_path])
    if spec:
        # Load the module
        module = spec.loader.load_module()
        _GoogleAdsClient = module.GoogleAdsClient
        
        # Find and load GoogleAdsException
        errors_spec = importlib.util.find_spec("google.ads.google_ads.errors", [site_packages_path])
        if errors_spec:
            errors_module = errors_spec.loader.load_module()
            GOOGLE_ADS_EXCEPTION = errors_module.GoogleAdsException
        else:
            print("Warning: google.ads.google_ads.errors module not found.")
            class GoogleAdsException(Exception): pass # Placeholder
            GOOGLE_ADS_EXCEPTION = GoogleAdsException
            
        GADS_AVAILABLE = True
        print("Successfully loaded Google Ads client library.")
    else:
        print("Warning: google.ads.google_ads.client module spec not found in site-packages.")

except (ImportError, AttributeError, ModuleNotFoundError) as e:
    print(f"Warning: Could not load Google Ads client library: {e}")
    # Define placeholder classes if import fails
    class GoogleAdsClientPlaceholder:
        def __init__(self):
            raise ModuleNotFoundError("Google Ads client is not available. Please ensure 'google-ads' is installed correctly.")
        def _init_client(self):
            raise ModuleNotFoundError("Google Ads client is not available.")
        def list_campaigns(self):
            raise ModuleNotFoundError("Google Ads client is not available.")
        # ... other methods similarly raising errors

    _GoogleAdsClient = GoogleAdsClientPlaceholder
    GOOGLE_ADS_EXCEPTION = type('GoogleAdsException', (Exception,), {})
    print("Using placeholder for Google Ads client.")

class GoogleAdsClient:
    def __init__(self):
        self._client = None
        self._customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")

    def _init_client(self):
        if not GADS_AVAILABLE:
            raise ModuleNotFoundError("Google Ads client library is not available. Please ensure 'google-ads' is installed correctly.")

        if self._client is None:
            conn = None
            try:
                from marketing_agent.db import get_conn
                conn = get_conn()
                row = conn.execute("SELECT * FROM integrations WHERE platform = ?", ('google_ads',)).fetchone()
                
                client_config = {}
                if row and row['refresh_token']:
                    client_config = {
                        "developer_token": row['developer_token'],
                        "client_id": row['client_id'],
                        "client_secret": row['client_secret'],
                        "refresh_token": row['refresh_token'],
                        "login_customer_id": row['customer_id']
                    }
                    self._customer_id = row['customer_id']
                else:
                    # Fallback to .env if not found in DB or if DB is unavailable
                    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
                    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
                    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
                    refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN")
                    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
                    
                    if client_id and client_secret and developer_token and refresh_token and customer_id:
                         client_config = {
                            "developer_token": developer_token,
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "refresh_token": refresh_token,
                            "login_customer_id": customer_id
                        }
                         self._customer_id = customer_id
                    else:
                        raise Exception("Google Ads credentials not found in DB or .env.")

                if not self._customer_id:
                    raise Exception("GOOGLE_ADS_CUSTOMER_ID is missing.")
                
                self._client = _GoogleAdsClient.load_from_dict(client_config, version="v16")

            except Exception as e:
                raise Exception(f"Failed to initialize Google Ads client: {e}")
            finally:
                if conn:
                    conn.close()
        return self._client

    def list_campaigns(self):
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
        except GOOGLE_ADS_EXCEPTION as ex:
            print(f"Request with ID \"{ex.request_id}\" failed with status \"{ex.error.code().name}\" and includes the following errors:")
            for error in ex.errors:
                print(f"\tError with message \"{error.message}\".")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"\t\tOn field: {field_path_element.field_name}")
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
