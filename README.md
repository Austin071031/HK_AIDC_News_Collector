# HK AIDC News Collector

An AI-integrated news collector designed for telecom product teams to monitor AI data center market intelligence across Hong Kong, Mainland China, and Southeast Asia. The system focuses on daily collection, high-quality deduplication, and LLM-powered summarization, providing a clean dashboard for weekly market-intelligence sharing.

## System Architecture

The application is built on a deterministic ingestion pipeline coupled with LLM enrichment and clustering.

- **Frontend (Web Dashboard)**: Built with Next.js and React. Provides a split-view cluster feed, filtering options, analyst review tools (hide, favorite, manual tagging, notes), and a DB-driven visual config editor.
- **Backend (API & Worker)**: Python-based backend using FastAPI. It exposes REST APIs for the dashboard and runs asynchronous pipeline workers for daily data collection.
- **Database**: PostgreSQL (or SQLite for local development) using SQLAlchemy ORM.

### Pipeline Data Flow
1. **Discovery**: Uses a hybrid source strategy, combining curated RSS feeds/sitemaps and query-driven discovery via Firecrawl for comprehensive coverage.
2. **Extraction**: Discovered URLs are fetched and normalized into raw documents. Deterministic extraction is preferred, with Firecrawl acting as a fallback for complex pages.
3. **Prefilter**: Cheap deterministic checks (domain, language, length) are applied to filter out noise before involving the LLM.
4. **LLM Enrichment**: An OpenAI-compatible LLM (e.g., Deepseek, GPT-4) classifies relevance, extracts entities, tags topics, standardizes terminology across Chinese and English, and generates concise summaries.
5. **Deduplication & Clustering**: Groups related articles into unified event clusters based on canonical URLs, text similarity, and LLM semantic hints, ensuring the dashboard feed remains low-noise.

## Deployment Method

The project is structured into a Python backend and a Next.js frontend. Follow these steps for local development and deployment.

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Valid API keys for Firecrawl and an OpenAI-compatible LLM (e.g., Deepseek)

### 1. Backend & Database Setup

1. **Install Dependencies**:
   Navigate to the project root and install the required Python packages.
   ```bash
   pip install -e .[dev]
   ```

2. **Configure Environment Variables**:
   Run the interactive setup script to configure your `.env` file with API keys and database URL.
   ```bash
   python setup_keys.py
   ```
   *(Note: Ensure your `OPENAI_API_KEY` is correctly set in the `.env` file if you are using a different model provider. The `DATABASE_URL` defaults to PostgreSQL but can be changed to SQLite `sqlite+pysqlite:///./app.db` for local testing.)*

3. **Initialize the Database**:
   Create the database tables using SQLAlchemy. Ensure your database server (e.g., PostgreSQL) is running if you aren't using SQLite. *Note: This script will also automatically seed the database with initial sources and keywords if the tables are empty.*
   ```bash
   export PYTHONPATH=src
   python scripts/migrate_db.py
   ```

4. **Start the FastAPI Server**:
   Start the backend API on port 8000.
   ```bash
   export PYTHONPATH=src
   uvicorn hk_aidc_news.app:create_app --factory --reload --port 8000
   ```

### 2. Frontend Setup

1. **Install Dependencies**:
   Navigate to the `web` directory.
   ```bash
   cd web
   npm install
   ```

2. **Start the Next.js Development Server**:
   Run the frontend locally. It will proxy API requests to `http://localhost:8000`.
   ```bash
   npm run dev
   ```

3. **Access the Application**:
   Open [http://localhost:3000](http://localhost:3000) in your browser. The unified UI includes:
   - **News Feed (`/`)**: View the split-view cluster feed and perform analyst actions.
   - **Pipeline Manager (`/pipeline`)**: Trigger the daily discovery/ingestion pipeline and view real-time log streaming.
   - **Settings (`/settings`)**: Visual configuration editor to manage discovery sources and keywords directly in the database.

### 3. Production Deployment Notes
- **Database**: Switch the `DATABASE_URL` in your environment variables from SQLite to PostgreSQL (`postgresql+psycopg://...`).
- **Backend**: Run the FastAPI application using a production ASGI server like `uvicorn` with `gunicorn` workers. Schedule the daily worker script using `cron` or a job scheduler.
- **Frontend**: Build the Next.js application using `npm run build` and deploy it to a platform like Vercel, or serve it using `npm run start` behind a reverse proxy.
