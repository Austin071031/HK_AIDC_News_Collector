import os

def main():
    print("=== API Keys Setup ===")
    firecrawl_key = input("Enter your Firecrawl API Key: ").strip()
    deepseek_key = input("Enter your Deepseek LLM API Key: ").strip()
    
    env_content = f"""APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/hk_aidc_news
FIRECRAWL_API_KEY={firecrawl_key}
FIRECRAWL_BASE_URL=https://api.firecrawl.dev
LLM_API_KEY={deepseek_key}
LLM_MODEL=deepseek-v4-pro
DEFAULT_QUERY_LIMIT=25
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
        
    print("\n✅ Successfully saved API keys to .env file!")
    print("The app will load these keys directly next time it starts.")

if __name__ == "__main__":
    main()
