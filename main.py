import click
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from marketing_agent.campaign_manager import CampaignManager
from marketing_agent.crm_manager import CRMManager
from marketing_agent.llm_client import llm_chat
from marketing_agent.data_analyzer import data_analyzer
from marketing_agent.skill_manager import SkillManager
from marketing_agent.report_generator import report_generator
from marketing_agent.google_ads_client import google_ads_client # Import Google Ads client

@click.group()
def cli():
    """Main CLI for Marketing Agent."""
    pass

# --- Campaign Management Commands ---
@cli.command()
@click.option('--name', required=True, help='Name of the campaign.')
@click.option('--objective', required=True, help='Objective of the campaign (e.g., Conversion, Brand Awareness).')
@click.option('--audience', required=True, help='Target audience description.')
@click.option('--budget', required=True, type=float, help='Budget for the campaign.')
def plan_campaign(name, objective, audience, budget):
    """Plans a new marketing campaign."""
    cm = CampaignManager()
    campaign_id = cm.plan_campaign(name, objective, audience, budget)
    click.echo(f"Campaign planned: ID={campaign_id}, Name={name}, Objective={objective}, Budget=${budget:.2f}")

@cli.command()
@click.option('--campaign-id', required=True, help='ID of the campaign to execute.')
def execute_campaign(campaign_id):
    """Executes a planned marketing campaign."""
    cm = CampaignManager()
    result = cm.execute_campaign(campaign_id)
    click.echo(result)

# --- CRM Commands ---
@cli.command()
@click.option('--name', required=True, help='Name of the lead.')
@click.option('--email', required=True, help='Email of the lead.')
@click.option('--source', required=True, help='Source of the lead (e.g., Web, Referral).')
def add_lead(name, email, source):
    """Adds a new lead to the CRM."""
    crm = CRMManager()
    lead_id = crm.add_lead(name, email, source)
    click.echo(f"Lead added: ID={lead_id}, Name={name}, Email={email}, Source={source}")

# --- LLM Generation Commands ---
@cli.command()
@click.option('--product', required=True, help='Product or service for the ad.')
@click.option('--platform', required=True, help='Marketing platform (e.g., google, meta, tiktok, X).')
@click.option('--audience', required=True, help='Target audience description.')
@click.option('--tone', help='Tone of the ad copy (e.g., Professional, Casual, Urgent).')
@click.option('--budget-range', help='Budget range for context (e.g., 1000, 5000).')
def generate_ad_copy(product, platform, audience, tone=None, budget_range=None):
    """Generates ad copy for a given product and platform."""
    copy_generator = ad_copy_generator
    ad_variants = copy_generator.generate_ad_copy(product, platform, audience, tone, budget_range)
    for variant in ad_variants:
        click.echo(f"---")
        click.echo(f"Platform: {variant['platform']}")
        for key, value in variant.items():
            if key != 'platform':
                click.echo(f"{key}: {value}")
        click.echo("---")

@cli.command()
@click.option('--subject', required=True, help='Subject of the email.')
@click.argument('body', required=True)
def generate_email(subject, body):
    """Generates marketing email content."""
    email_content = llm_chat(prompt=f"Generate a marketing email with subject: {subject}\nBody: {body}")
    click.echo("--- Email Content ---")
    click.echo(f"Subject: {subject}")
    click.echo(email_content)
    click.echo("---------------------")

# --- Analysis Commands ---
@cli.command()
@click.argument('keywords', nargs=-1, required=True)
def analyze_keywords(keywords):
    """Analyzes keywords for marketing insights."""
    results = data_analyzer.analyze_keywords(keywords)
    click.echo("--- Keyword Analysis Results ---")
    for keyword, data in results.items():
        click.echo(f"Keyword: {keyword}")
        for key, value in data.items():
            click.echo(f"  {key}: {value}")
    click.echo("------------------------------")

# --- Reporting Command ---
@cli.command()
def generate_report():
    """Generates an HTML performance report."""
    path = report_generator.save_html()
    click.echo(f"Report saved to: {path}")

# --- Skill Execution Command ---
@cli.command()
@click.argument('skill_name', required=True)
@click.argument('method_name', required=True)
@click.argument('method_args', nargs=-1, required=False)
def run_skill(skill_name, method_name, method_args):
    """Runs a specific method from a registered skill."""
    sm = SkillManager()
    skill = sm.get_skill(skill_name)
    if not skill:
        click.echo(f"Error: Skill '{skill_name}' not found.")
        return

    method = getattr(skill, method_name, None)
    if not method:
        click.echo(f"Error: Method '{method_name}' not found in skill '{skill_name}'.")
        return

    try:
        result = method(*method_args)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error running skill method: {e}")

# --- Google Ads Commands ---
@cli.group()
def google_ads():
    """Manage Google Ads operations."""
    pass

@google_ads.command()
def init_auth():
    """Initiates Google Ads OAuth flow to get a refresh token."""
    try:
        # Ensure google_ads_client is imported and available
        if google_ads_client is None:
            raise ImportError("Google Ads client library is not available.")

        # This will trigger the browser-based OAuth flow if credentials are not set
        # It might require user input for Client ID, Secret, etc.
        # The actual token generation flow is handled within the client library or needs explicit implementation here.
        # For now, we guide the user to run the standalone script if needed.
        click.echo("To initialize Google Ads connection, please ensure your .env file is set up correctly.")
        click.echo("If needed, run the python script: scripts/get_google_ads_refresh_token.py")
        click.echo("After obtaining credentials, add them to your .env file.")
        click.echo("Then, try listing campaigns via: python main.py google-ads list-campaigns")

    except ImportError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")

@google_ads.command()
def list_campaigns():
    """Lists all Google Ads campaigns."""
    try:
        if google_ads_client is None:
            raise ImportError("Google Ads client library is not available.")

        campaigns = google_ads_client.list_campaigns()
        if campaigns:
            click.echo("--- Google Ads Campaigns ---")
            for camp in campaigns:
                click.echo(f"ID: {camp['id']}, Name: {camp['name']}, Status: {camp['status']}, Budget: ${camp['budget']:.2f}")
        else:
            click.echo("No Google Ads campaigns found or client not initialized properly.")
    except Exception as e:
        click.echo(f"Error listing Google Ads campaigns: {e}")

# --- Main execution ---
if __name__ == '__main__':
    cli()
