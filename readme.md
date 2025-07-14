
# who_BOT – The Reddit Persona Profiler



who_BOT is an intelligent Python bot that scrapes a Reddit user's comments and posts and uses an LLM to generate a detailed, human-like user persona with citations.

"Find the human behind the handle."



FEATURES

- Extracts personality traits, interests, tone, and activity patterns

- Uses Reddit comments + posts as raw data

- Generates insights using a Hugging Face-hosted LLM (e.g., DeepSeek)

- Cites original Reddit links in each trait

- Outputs results in clean .txt files

SETUP INSTRUCTIONS

Clone the repository:
```


git clone https://github.com/voltrix-225/who_BOT.git
cd who_BOT
```

Install dependencies:

```
bash
pip install -r requirements.txt 


Create a .env file in the root of the project:

CLIENT_ID=your_reddit_app_id
CLIENT_SECRET=your_reddit_app_secret

HF_API=your_huggingface_token
```



# USAGE

To generate a persona:
```
bash

python who_BOT.py https://www.reddit.com/user/user/
```

This will:

- Scrape the user’s comments and posts

- Build a structured prompt

- Call the LLM via Hugging Face

Save the output to:
- data/user.json
- personas/persona_user.txt

PROJECT STRUCTURE

who_BOT/\
├── who_BOT.py\
├── persona_builder.py\
├── .env.example\
├── .gitignore\
├── README.md\
├── requirements.txt\
├── data/\
└── personas/

EXAMPLE OUTPUT (Persona)

Username: user

\>>>Personality Traits:

Skeptical and assertive [based on: Reddit link]

Dry humor, often sarcastic [based on: Reddit link]

\>>>Interests:

Star Wars lore, conspiracy debunking, history

\>>Activity Pattern:

Active mostly late night UTC



# POWERED BY

PRAW (Python Reddit API Wrapper)

Hugging Face Inference API - MISTRAL AI
