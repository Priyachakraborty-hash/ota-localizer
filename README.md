#  OTA Release Notes Localizer

A Python automation tool that tracks software release notes from GitHub and translates them into 10+ languages, exports them in **XLIFF format** for professional localization workflows, and serves everything via a REST API and with built-in health monitoring.

> Built to demonstrate automation, i18n (internationalization), REST APIs, database management, and localization workflows.

---

#  The Problem It Solves

Software teams ship updates globally but release notes are often only in English. This tool automates the full pipeline:
GitHub Releases → Fetch → Translate → Store → Export (XLIFF) → Serve via API


## Tech Stack

 Layer and Technology

 Language: Python 3 
 Release Fetching :  GitHub REST API + `requests` 
 Translation :  `deep-translator` (Google Translate) 
 Localization Format :  **XLIFF 1.2** 
 Database :  SQLite (`sqlite3`) 
 Others :    REST API | Flask |
Logging & Monitoring :  Python `logging` + health log DB table 



##  Features

-  **Fetch** release notes from any public GitHub repository
-  **Translate** into 10 languages (ES, FR, DE, ZH, JA, KO, PT, AR, HI, IT)
-  **Export to XLIFF** — the industry-standard format for software localization
-  **Validate XLIFF** — detect missing or untranslated strings automatically
-  **Store** in SQLite with deduplication
-  **Monitor** automation health via a built-in health log
-  **Mock data fallback** for offline testing

---

##  Installation


git clone git clone https://github.com/Priyachakraborty-hash/ota-localizer.git
cd ota-localizer
pip install -r requirements.txt
python app.py


# API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Project info |
| POST | `/fetch` | Fetch & store releases from a GitHub repo |
| GET | `/localize?repo=microsoft/vscode&lang=fr` | Fetch + translate releases |
| GET | `/releases?lang=es` | Get stored releases by language |
| GET | `/export/xliff?lang=es` | Download XLIFF localization file |
| GET | `/validate/xliff?lang=es` | Check XLIFF for missing translations |
| GET | `/languages` | Supported languages |
| GET | `/health` | Automation health log |
| GET | `/stats` | Summary statistics |



# Example: Fetch & Localize

```bash
# Fetch releases for VS Code
curl -X POST http://localhost:5000/fetch \
  -H "Content-Type: application/json" \
  -d '{"owner": "microsoft", "repo": "vscode", "limit": 5}'

# Translate them to Japanese
curl "http://localhost:5000/localize?repo=microsoft/vscode&lang=ja"

# Download the XLIFF file
curl "http://localhost:5000/export/xliff?lang=ja" -o releases_ja.xliff

# Validate the XLIFF
curl "http://localhost:5000/validate/xliff?lang=ja"
```

---

##  Sample XLIFF Output

```xml
<?xml version="1.0" encoding="utf-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file original="https://github.com/microsoft/vscode/releases/tag/1.95.0"
        source-language="en"
        target-language="ja"
        datatype="plaintext"
        product-name="microsoft/vscode"
        product-version="1.95.0">
    <body>
      <trans-unit id="microsoft_vscode_1.95.0_content">
        <source>Performance improvements: Reduced startup time by 40%.</source>
        <target>パフォーマンスの改善：起動時間を40％短縮しました。</target>
      </trans-unit>
    </body>
  </file>
</xliff>
```

---

#  Project Structure


```
ota-localizer/
├── app.py            # Flask REST API
├── fetcher.py        # GitHub API release fetcher
├── translator.py     # i18n translation module
├── xliff_handler.py  # XLIFF export, parse & validation
├── database.py       # SQLite layer + health logging
├── requirements.txt  # Dependencies
└── README.md         # Project documentation
```


---

##  Future Improvements

- Schedule auto-fetch with `APScheduler` (cron-style)
- Add XLIFF 2.0 support
- Webhook support — trigger pipeline when a new GitHub release is published
- Frontend dashboard for monitoring translation status
- PostgreSQL support for production scale



Built by Priya | Python automation + i18n localization pipeline project
