from marketing_agent.llm_client import llm_chat

class AdCopyGenerator:
    PLATFORMS = {
        'google': {
            'name': 'Google Ads',
            'constraints': 'Headlines max 30 chars each, Description max 90 chars. Up to 3 headlines + 2 descriptions.',
            'format': 'Headline 1: ...\nHeadline 2: ...\nHeadline 3: ...\nDescription 1: ...\nDescription 2: ...'
        },
        'meta': {
            'name': 'Meta/Facebook Ads',
            'constraints': 'Primary text max 125 chars (above fold). Headline max 40 chars. Description max 30 chars. CTA button.',
            'format': 'Primary Text: ...\nHeadline: ...\nDescription: ...\nCTA: ...'
        },
        'tiktok': {
            'name': 'TikTok Ads',
            'constraints': 'Ad text max 100 chars. Short, punchy, trend-aware. Hook in first 1-2 seconds.',
            'format': 'Hook: ...\nText: ...\nCTA: ...\nHashtags: ...'
        },
        'x': {
            'name': 'X/Twitter Ads',
            'constraints': 'Promoted post max 280 chars. Concise, attention-grabbing.',
            'format': 'Ad Copy: ...\nCTA: ...'
        }
    }

    def generate(self, product, platform, target_audience, tone, budget_range):
        if platform not in self.PLATFORMS:
            return f"Unsupported platform: {platform}. Use: {', '.join(self.PLATFORMS.keys())}"
        
        p = self.PLATFORMS[platform]
        
        prompt = f"""You are a world-class direct-response copywriter.
Generate ad copy for the following product/service.

Product/Service: {product}
Platform: {p['name']}
Target Audience: {target_audience}
Tone/Voice: {tone}
Budget Range: {budget_range}

Constraints: {p['constraints']}

Return in this format:
{p['format']}

Also include a brief "Strategy Note" explaining the angle taken and why it works for this audience.

Keep it sharp. No fluff."""
        
        return llm_chat(prompt, model='easy')

ad_copy_generator = AdCopyGenerator()
