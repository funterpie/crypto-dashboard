# Crypto Dashboard — Deploy to GitHub + Streamlit

Quick steps to publish this project to GitHub and deploy on Streamlit Community Cloud.

1) Prepare local repo

```bash
# from project root
git init
git add .
git commit -m "Initial commit"
# add remote (replace with your repo)
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

2) Ensure secrets are not committed

- `.env` is already in `.gitignore`. Keep your real credentials in `.env` locally.
- Commit `.env.example` so others know which vars to set.

3) Install dependencies locally

```bash
python -m pip install -r requirements.txt
# run locally
streamlit run dashboard.py
```

4) Deploy on Streamlit Community Cloud

- Sign in at https://share.streamlit.io using your GitHub account.
- Click "New app" → choose your repo, branch (`main`) and the file `dashboard.py`.
- Before deploy, set environment variables in the app settings:
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  Alternatively you can set Streamlit Secrets (`st.secrets`) in the app settings — `config.py` will prefer `st.secrets` when available.
- Deploy the app. Streamlit will build the environment using `requirements.txt`.

Notes

- If your DB is not publicly accessible, use a managed Postgres (Render/Railway) and set the host accordingly.

Docker Compose (local or VPS)

You can run Postgres + the Streamlit app + the background ETL fetcher locally using Docker Compose.

```bash
# build and start all three services
docker compose up --build -d

# view logs for the ETL pipeline
docker compose logs -f etl

# view logs for the dashboard
docker compose logs -f app

# stop all containers
docker compose down
```

The app will be available at http://localhost:8501, and Postgres will be exposed at port 5432 on the host. The ETL pipeline will continuously run in the background.

Make sure `.env` contains correct DB credentials (the compose file maps those into the Postgres container).

Streamlit secrets

- Locally you can create `.streamlit/secrets.toml` with the DB values (example provided at `.streamlit/secrets.toml`).
- On Streamlit Community Cloud add these keys under *App settings → Secrets* and they will be available via `st.secrets`.
- `config.py` prefers `st.secrets` when present and falls back to environment variables or `.env`.

If you want, I can push these files to a new GitHub repo for you (if you provide remote URL), or add a CI deploy pipeline.
