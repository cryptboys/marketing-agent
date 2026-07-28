import click
import os
import importlib

from marketing_agent.content_generator import content_generator
from marketing_agent.data_analyzer import data_analyzer
from marketing_agent.campaign_manager import campaign_manager
from marketing_agent.crm_manager import crm_manager
from marketing_agent.governance import budget_manager, egress_validator, audit_tracer
from marketing_agent.skill_manager import skill_manager
from marketing_agent.dashboard import dashboard

@click.group()
def cli():
    """Marketing Agent CLI"""
    pass

# --- Content Generation Commands ---

@cli.command()
@click.option('--topic', default='AI Marketing', help='Topic for the social media post.')
@click.option('--platform', default='LinkedIn', help='Platform for the post (e.g., LinkedIn, Twitter).')
def generate_social_post(topic, platform):
    """Generates a social media post draft."""
    post = content_generator.generate_social_post(topic, platform)
    click.echo(post)
    audit_tracer.add_trace('generate_social_post', {'topic': topic, 'platform': platform})

@cli.command()
@click.option('--subject', required=True, help='Subject of the email.')
@click.argument('body_text', required=True)
def generate_email(subject, body_text):
    """Generates an email."""
    email = content_generator.generate_email(subject, body_text)
    click.echo(email)
    audit_tracer.add_trace('generate_email', {'subject': subject})

# --- Data Analysis Commands ---

@cli.command()
@click.argument('keywords', nargs=-1)
def analyze_keywords(keywords):
    """Analyzes a list of keywords."""
    if not keywords:
        click.echo("Please provide keywords to analyze.")
        return
    results = data_analyzer.analyze_keywords(keywords)
    click.echo("Keyword Analysis Results:")
    for kw, data in results.items():
        click.echo(f"  - {kw}: Volume={data['search_volume']}, Competition={data['competition']}")
    audit_tracer.add_trace('analyze_keywords', {'keywords': list(keywords)})

# --- Campaign Management Commands ---

@cli.command()
@click.argument('campaign_name', required=True)
@click.option('--objective', default='Brand Awareness', help='Campaign objective.')
@click.option('--audience', default='General Audience', help='Target audience.')
@click.option('--budget', type=float, required=True, help='Campaign budget.')
def plan_campaign(campaign_name, objective, audience, budget):
    """Plans a new marketing campaign."""
    if not budget_manager.consume_budget(budget):
        click.echo(f"Budget exceeded. Remaining budget: {budget_manager.get_remaining_budget()}")
        return
    campaign_id = campaign_manager.plan_campaign(campaign_name, objective, audience, budget)
    audit_tracer.add_trace('plan_campaign', {'campaign_id': campaign_id, 'name': campaign_name, 'budget': budget})
    click.echo(f"Campaign '{campaign_name}' planned with ID: {campaign_id}. Budget consumed: {budget}. Remaining budget: {budget_manager.get_remaining_budget()}")

@cli.command()
@click.argument('campaign_name', required=True)
def execute_campaign(campaign_name):
    """Executes a planned campaign."""
    result = campaign_manager.execute_campaign(campaign_name)
    audit_tracer.add_trace('execute_campaign', {'campaign_name': campaign_name, 'result': result})
    click.echo(result)

# --- CRM Commands ---

@cli.command()
@click.argument('name', required=True)
@click.argument('email', required=True)
@click.argument('source', required=True)
def add_lead(name, email, source):
    """Adds a new lead to the CRM."""
    lead_id = crm_manager.add_lead(name, email, source)
    audit_tracer.add_trace('add_lead', {'lead_id': lead_id, 'name': name, 'email': email, 'source': source})
    click.echo(f"Lead '{name}' added with ID: {lead_id}")

# --- Skill-based Commands ---

@cli.command()
@click.argument('skill_name', required=True)
@click.argument('method_name', required=True)
@click.argument('method_args', nargs=-1)
def run_skill(skill_name, method_name, method_args):
    """Runs a method from a loaded skill."""
    skill = skill_manager.get_skill_instance(skill_name)
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
        audit_tracer.add_trace('run_skill', {'skill': skill_name, 'method': method_name, 'args': list(method_args)})
    except Exception as e:
        click.echo(f"Error running skill method: {e}")

# --- Dashboard Command ---
@cli.command()
def dashboard_view():
    """Shows the marketing agent dashboard."""
    data = dashboard.get_overview()
    click.echo("=== Marketing Agent Dashboard ===")
    click.echo(f"Last updated: {data['last_updated']}")
    click.echo(f"Remaining Budget: {data['budget_remaining']}")
    click.echo(f"Audit log entries: {data['audit_log_count']}")
    click.echo("--- Campaign Summary ---")
    click.echo(f"Total Campaigns: {data['campaigns']['total_campaigns']}")
    click.echo(f"Planned: {data['campaigns']['planned']}")
    click.echo(f"Executing: {data['campaigns']['executing']}")
    click.echo(f"Completed: {data['campaigns']['completed']}")
    click.echo(f"Total Budget Allocated: {data['campaigns']['total_budget_allocated']}")

if __name__ == '__main__':
    cli()
