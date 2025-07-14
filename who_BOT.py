import praw
import prawcore
import json
import os
import re
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ───────────── CONFIG ──────────────
CLIENT_ID     = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USER_AGENT    = "script:reddit_persona_builder:v1.0 (by u/Flashy-Guest6138)"
HF_TOKEN      = os.getenv("HF_API")  # set: export HF_TOKEN=hf_...
ROUTER_URL    = "https://router.huggingface.co/novita/v3/openai/chat/completions"
MODEL_NAME    = "mistralai/mistral-7b-instruct"
DATA_DIR      = Path("data")
OUTPUT_DIR    = Path("personas")
TIMEOUT       = 90
# ───────────────────────────────────

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def extract_username(profile_url):
    match = re.search(r'reddit\.com/user/([\w-]+)/?', profile_url)
    return match.group(1) if match else None

def user_exists(username):
    try:
        _ = reddit.redditor(username).id
        return True
    except (prawcore.exceptions.NotFound, prawcore.exceptions.Forbidden, AttributeError):
        return False

def scrape_user_data(username, limit=75):
    user = reddit.redditor(username)
    comments, posts = [], []

    print(f">>>Scraping up to {limit} comments and posts from u/{username}...")

    for c in user.comments.new(limit=limit):
        comments.append({
            "id": c.id,
            "subreddit": c.subreddit.display_name,
            "created_utc": c.created_utc,
            "score": c.score,
            "permalink": f"https://www.reddit.com{c.permalink}",
            "body": c.body
        })

    for p in user.submissions.new(limit=limit):
        posts.append({
            "id": p.id,
            "title": p.title,
            "subreddit": p.subreddit.display_name,
            "created_utc": p.created_utc,
            "score": p.score,
            "permalink": f"https://www.reddit.com{p.permalink}",
            "selftext": p.selftext
        })

    return {"username": username, "comments": comments, "posts": posts}

def build_prompt(data, sample_limit=40):
    intro = f"""You are an expert analyst tasked with building a user persona from Reddit activity.

Return the output in this structure:

Username: <username>

>>> Personality Traits:
- <trait> [based on: <permalink>]

>>> Interests:
- ...

>>> Activity Pattern:
- ...

Include a citation (permalink) for every insight.

Now here are up to {sample_limit} raw posts and comments from u/{data['username']}:
------------------------------------------------
"""
    snippets = []

    for c in data["comments"][: sample_limit // 2]:
        snippets.append(
            f"Comment on r/{c['subreddit']} (score {c['score']}):\n\"{c['body']}\"\n[Link: {c['permalink']}]\n"
        )
    for p in data["posts"][: sample_limit // 2]:
        body = p['selftext'] or "(no self-text)"
        snippets.append(
            f"Post on r/{p['subreddit']} (score {p['score']}):\n\"{p['title']}\"\n{body}\n[Link: {p['permalink']}]\n"
        )

    return intro + "\n---\n".join(snippets)

def call_hf_router(prompt):
    if not HF_TOKEN:
        sys.exit("HF_TOKEN environment variable not set.")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that creates user personas from Reddit data."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(ROUTER_URL, headers=headers, json=payload, timeout=TIMEOUT)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        print(f"Router error {response.status_code}: {response.text}")
        sys.exit(1)

def save_output(username, raw_data, persona):
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Save raw JSON
    json_path = DATA_DIR / f"{username}_raw.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    # Save persona
    txt_path = OUTPUT_DIR / f"persona_{username}.txt"
    txt_path.write_text(persona, encoding="utf-8")

    print(f">>>Saved raw data to {json_path}")
    print(f">>>Saved persona to {txt_path}")

# ───────────── MAIN ──────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python who_BOT.py <Reddit user profile URL>")
        sys.exit(1)

    logo = r"""

          _              ____   ___ _____ 
__      _| |__   ___    | __ ) / _ \_   _|
\ \ /\ / / '_ \ / _ \   |  _ \| | | || |  
 \ V  V /| | | | (_) |  | |_) | |_| || |  
  \_/\_/ |_| |_|\___/___|____/ \___/ |_|  
                   |_____|                

"""

    print(logo)
    profile_url = sys.argv[1]
    username = extract_username(profile_url)

    if not username:
        print("Invalid Reddit profile URL format.")
        sys.exit(1)

    if not user_exists(username):
        print(f"Reddit user '{username}' not found or suspended.")
        sys.exit(1)

    raw_data = scrape_user_data(username)
    prompt = build_prompt(raw_data)
    persona = call_hf_router(prompt)
    save_output(username, raw_data, persona)
