# Marketing Agent CLI

This is a CLI tool for a Marketing Agent, built using Python.

## Features

*   **Content Generation:** Create social media posts and emails.
*   **Data Analysis:** Analyze keywords and campaign performance.
*   **Campaign Management:** Plan and execute marketing campaigns.
*   **CRM:** Manage leads.
*   **Governance:** Basic budget management and audit tracing.

## Installation

```bash
pip install .
```

## Usage

```bash
marketing-agent generate-social-post --topic "AI in Marketing" --platform Twitter
marketing-agent analyze-keywords AI marketing automation CRM social media
marketing-agent plan-campaign "Summer Sale" --objective "Increase Sales" --budget 5000
marketing-agent execute-campaign cmp_1234
marketing-agent add-lead "John Doe" john.doe@example.com Website
```

## Development

Run `python -m marketing_agent.cli` for development.
