import random
from .llm_client import llm_chat

class ContentGenerator:
    def generate_social_post(self, topic, platform):
        result = llm_chat(f"Write a short, engaging social media post about '{topic}' for {platform}. Include relevant hashtags.")
        if result:
            return result
        # fallback mock
        return f"Check out this new content on {topic} for {platform}! #Marketing #AI"

    def generate_email(self, subject, body_context):
        result = llm_chat(f"Write a marketing email with subject: '{subject}'. Context: {body_context}")
        if result:
            return result
        return f"Subject: {subject}\n\n{body_context}"

    def generate_ad_copy(self, product, target_audience):
        result = llm_chat(f"Write a compelling ad copy for '{product}' targeting {target_audience}. Keep it under 100 words.")
        if result:
            return result
        return f"Try {product} today — built for {target_audience}. Limited offer!"

content_generator = ContentGenerator()
