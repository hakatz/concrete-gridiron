# Concrete Gridiron 🏈

A modern historical record, analytics dashboard, and dossier hub for our Yahoo Fantasy Football league. Built with **Next.js 15**, **Tailwind CSS**, and a **Python ETL pipeline** that archives season data, calculates career standings, detects behavioral manager archetypes, and computes real draft value metrics.

---

## 🚀 Live Site & Automated Deployment

- **Repository**: [https://github.com/hakatz/concrete-gridiron](https://github.com/hakatz/concrete-gridiron)
- **Deployment**: Configured via GitHub Actions (`.github/workflows/deploy.yml`).
- Every push to the `main` branch automatically builds the static Next.js export and publishes the bundle to the `gh-pages` branch, updating the live site instantly.

---

## 📁 Repository Structure

```
concrete-gridiron/
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD automated deployment to GitHub Pages
├── backend/
│   ├── scrape_history.py         # Yahoo scraper & ETL ingestion pipeline
│   ├── analytics.py              # Statistical aggregations, archetypes, draft deltas
│   ├── write_pages.py            # Code-generation templates for dynamic dossier views
│   ├── db.py                     # SQLite schema definitions
│   └── auth_setup.py             # Yahoo OAuth interactive session setup
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main league dashboard & career standings
│   │   │   ├── drafts/page.tsx   # All-time draft archive & value delta board
│   │   │   ├── h2h/page.tsx      # Head-to-Head lifetime rivalries matrix
│   │   │   ├── rules/page.tsx    # League constitution & rules
│   │   │   └── managers/[id]/    # Manager dossiers with tendencies & radar charts
│   │   └── data/
│   │       └── league_analytics.json  # ⭐️ CORE DATA FILE powering the entire site
│   ├── package.json
│   ├── next.config.ts
│   └── tailwind.config.ts
├── .gitignore
└── README.md
```

---

## 📊 Where Data Files Live

The web application is decoupled from the raw SQLite database for high performance and zero-latency static hosting.

- **Primary Site Data**:
  [`frontend/src/data/league_analytics.json`](frontend/src/data/league_analytics.json)
  This single JSON file is ingested by all dashboard pages, dossiers, draft archives, and head-to-head views.
- **Raw Scrapes & Database (Local only)**:
  SQLite tables and cached HTML pages live under `backend/data/` and `backend/cache/` (kept out of git via `.gitignore`).
- **Auth Session (Local only)**:
  Yahoo session cookies live in `backend/session.json` (strictly git-ignored to prevent credential leakage).

---

## 🔄 How to Push Updates

### 1. Ingesting New Weekly / Season Data
When new weeks or seasons are completed:
1. Run the backend scraper / ETL:
   ```bash
   python backend/scrape_history.py --years 2025
   ```
2. Re-compute league statistics and archetypes (regenerates `frontend/src/data/league_analytics.json`):
   ```bash
   python backend/analytics.py
   ```
3. Update generated page templates if schema or metrics changed:
   ```bash
   python backend/write_pages.py
   ```

### 2. Testing Locally
To test changes before pushing:
```bash
cd frontend
npm run dev
```
To test static export generation:
```bash
cd frontend
npm run build
```

### 3. Committing and Pushing to GitHub
Once verified, push to `main` to trigger live deployment:
```bash
git add .
git commit -m "Update league analytics and weekly scores"
git push origin main
```
GitHub Actions will detect the push, compile the static bundle, and deploy to GitHub Pages automatically.

---

## ⚙️ Enabling GitHub Pages (One-Time Setup)

In the GitHub repository settings:
1. Go to **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, choose **Deploy from a branch**.
3. Select branch: **`gh-pages`** and folder: **`/ (root)`**.
4. Click **Save**.
