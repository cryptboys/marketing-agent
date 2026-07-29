import json
import re
from collections import Counter

data = json.loads(open('vault/research/copycat/samples/NenkMonica.json', encoding='utf-8').read())

# Basic stats
total = len(data)
print(f"Total tweets analyzed: {total}\n")

# Lengths
lengths = [len(t) for t in data]
avg_len = sum(lengths) / total
print(f"Average length: {avg_len:.1f} chars")
print(f"Min length: {min(lengths)}")
print(f"Max length: {max(lengths)}\n")

# Emoji usage
emoji_tweets = [t for t in data if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U0000FE00-\U0000FE0F\U0000200D]', t)]
print(f"Emoji usage: {len(emoji_tweets)}/{total} ({len(emoji_tweets)/total*100:.1f}%)")

# Hashtags
hashtag_tweets = [t for t in data if '#' in t]
print(f"Hashtag usage: {len(hashtag_tweets)}/{total} ({len(hashtag_tweets)/total*100:.1f}%)")

# Mentions
mention_tweets = [t for t in data if '@' in t]
print(f"Mention usage: {len(mention_tweets)}/{total} ({len(mention_tweets)/total*100:.1f}%)")

# Links
link_tweets = [t for t in data if 'http' in t]
print(f"Link usage: {len(link_tweets)}/{total} ({len(link_tweets)/total*100:.1f}%)")

# Question hooks
question_tweets = [t for t in data if t.strip().endswith('?')]
print(f"Question hooks: {len(question_tweets)}/{total} ({len(question_tweets)/total*100:.1f}%)")

# ALL CAPS words
caps_words = []
for t in data:
    words = re.findall(r'\b[A-Z]{2,}\b', t)
    caps_words.extend(words)
top_caps = Counter(caps_words).most_common(10)
print(f"\nTop ALL CAPS words: {top_caps}")

# Opening patterns
opening_words = []
for t in data:
    first_word = t.split()[0] if t.split() else ''
    opening_words.append(first_word)
top_openings = Counter(opening_words).most_common(10)
print(f"Top opening words: {top_openings}")

# Patterns with emojis at end
emoji_end = [t for t in data if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF\U0000FE00-\U0000FE0F\U0000200D]$', t.strip())]
print(f"\nEmoji at end: {len(emoji_end)}/{total} ({len(emoji_end)/total*100:.1f}%)")

# Threads (tweets with line breaks)
thread_tweets = [t for t in data if '\n' in t]
print(f"Thread-style (line breaks): {len(thread_tweets)}/{total} ({len(thread_tweets)/total*100:.1f}%)")

# Sample of high-engagement looking (long, with hashtags, questions, caps)
print("\n--- Sample high-engagement patterns ---")
for t in data[:10]:
    print(f"- {t[:150]}...")
