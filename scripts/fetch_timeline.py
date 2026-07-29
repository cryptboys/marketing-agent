import json
import requests
import re

def get_auth_headers(cookie_path):
    with open(cookie_path, 'r') as f:
        cookies_list = json.load(f)
    
    cookies_dict = {c['name']: c['value'] for c in cookies_list}
    
    # Ambil ct0 (csrf token) dari cookies
    csrf_token = cookies_dict.get('ct0', '')
    
    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejfCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA', # default X web client bearer
        'x-csrf-token': csrf_token,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-twitter-active-user': 'yes',
        'x-twitter-auth-type': 'OAuth2Session',
        'x-twitter-client-language': 'en',
    }
    
    return headers, cookies_dict

def get_user_id(username, headers, cookies):
    # Dapatkan User ID berdasarkan username
    url = f"https://x.com/i/api/graphql/sfb4LsXpt6t_q73QZ6OqEA/UserByScreenName"
    variables = {"screen_name": username, "withSafetyModeUserFields": True}
    features = {"hidden_profile_likes_enabled": True, "hidden_profile_subscriptions_enabled": True, "responsive_web_graphql_exclude_directive_enabled": True, "verified_phone_label_enabled": False, "subscriptions_verification_info_is_identity_verified_enabled": True, "subscriptions_verification_info_verified_since_enabled": True, "cantire_interaction_education_single_line_posts": True, "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False, "responsive_web_graphql_timeline_navigation_enabled": True}
    
    params = {
        'variables': json.dumps(variables),
        'features': json.dumps(features)
    }
    
    r = requests.get(url, headers=headers, cookies=cookies, params=params)
    data = r.json()
    user_id = data['data']['user']['result']['rest_id']
    return user_id

def get_user_tweets(user_id, headers, cookies):
    url = "https://x.com/i/api/graphql/W34ED7exwK5gqf57EwXF3A/UserTweets"
    variables = {"userId": user_id, "count": 10, "includePromotedContent": False, "withQuickPromoteEligibilityDoubleEvaluate": True, "withVoice": True, "withV2Timeline": True}
    features = {"responsive_web_graphql_exclude_directive_enabled": True, "verified_phone_label_enabled": False, "creator_subscriptions_tweet_preview_api_enabled": True, "responsive_web_graphql_timeline_navigation_enabled": True, "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False, "tweetypie_unmention_optimization_enabled": True, "responsive_web_edit_tweet_api_enabled": True, "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True, "view_counts_everywhere_api_enabled": True, "longform_notetweets_consumption_enabled": True, "responsive_web_twitter_article_tweet_consumption_enabled": True, "tweet_awards_web_tipping_enabled": False, "freedom_of_speech_not_reach_fetch_enabled": True, "standardized_nudges_misinfo": True, "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True, "rweb_video_timestamps_enabled": True, "longform_notetweets_rich_text_read_enabled": True, "longform_notetweets_inline_media_enabled": True, "responsive_web_enhance_cards_enabled": False}
    
    params = {
        'variables': json.dumps(variables),
        'features': json.dumps(features)
    }
    
    r = requests.get(url, headers=headers, cookies=cookies, params=params)
    return r.json()

def extract_tweets(tweets_json):
    tweets = []
    try:
        instructions = tweets_json['data']['user']['result']['timeline_v2']['timeline']['instructions']
        for inst in instructions:
            if inst.get('type') == 'TimelineAddEntries':
                for entry in inst.get('entries', []):
                    if entry['entryId'].startswith('tweet-'):
                        tweet_data = entry['content']['itemContent']['tweet_results']['result']
                        legacy = tweet_data.get('legacy')
                        if legacy:
                            tweets.append(legacy.get('full_text', ''))
    except Exception as e:
        print(f"Error extracting: {e}")
    return tweets

if __name__ == '__main__':
    headers, cookies = get_auth_headers('secrets/twitter_cookies.json')
    for username in ["NenkMonica", "LambeSahamjja"]:
        try:
            print(f"Fetching ID for {username}...")
            uid = get_user_id(username, headers, cookies)
            print(f"User ID: {uid}")
            tweets_data = get_user_tweets(uid, headers, cookies)
            tweets = extract_tweets(tweets_data)
            print(f"Latest tweets from @{username}:")
            for i, t in enumerate(tweets[:3]):
                print(f"{i+1}. {t}\n")
        except Exception as e:
            print(f"Failed to fetch {username}: {e}")
