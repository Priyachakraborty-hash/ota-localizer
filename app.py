from flask import Flask, jsonify, request, send_file
from fetcher import fetch_releases, get_mock_releases, fetch_all_default_repos
from translator import localize_releases, get_supported_languages
from xliff_handler import export_to_xliff, validate_xliff
from database import init_db, save_releases, get_releases, log_health, get_health_log, get_stats
import logging
import os

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


# ─── Root ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({
        "project": "OTA Release Notes Localizer",
        "description": "Fetches software release notes from GitHub, translates them into multiple languages, and exports to XLIFF for localization workflows.",
        "endpoints": 
        {
            "GET /releases?lang=en": "Get stored releases (filter by language)",
            "GET /releases?lang=es&repo=microsoft/vscode": "Filter by repo too",
            "POST /fetch": "Fetch & store releases for a GitHub repo",
            "GET /localize?repo=microsoft/vscode&lang=fr": "Fetch + translate a repo's releases",
            "GET /export/xliff?lang=es": "Export releases to XLIFF file",
            "GET /validate/xliff?lang=es": "Validate XLIFF for missing translations",
            "GET /languages": "Supported languages",
            "GET /health": "Automation health log",
            "GET /stats": "Summary stats"
        }
    })


# ─── Fetch & Store ───────────────────────────────────────────────────────────

@app.route("/fetch", methods=["POST"])
def fetch():
    """Fetch release notes for a given GitHub repo and store in DB."""
    data = request.get_json(silent=True) or {}
    owner = data.get("owner", "microsoft")
    repo = data.get("repo", "vscode")
    limit = int(data.get("limit", 5))

    releases = fetch_releases(owner, repo, limit=limit)
    count = save_releases(releases, language="en")
    log_health("fetch", "success", f"Fetched {len(releases)} releases for {owner}/{repo}")

    return jsonify({
        "status": "success",
        "repo": f"{owner}/{repo}",
        "fetched": len(releases),
        "new_saved": count,
        "releases": releases
    })


# ─── Localize ────────────────────────────────────────────────────────────────

@app.route("/localize")
def localize():
    """Fetch, translate, and store releases for a repo in the target language."""
    repo_full = request.args.get("repo", "microsoft/vscode")
    lang = request.args.get("lang", "es")

    try:
        owner, repo = repo_full.split("/")
    except ValueError:
        return jsonify({"error": "Invalid repo format. Use owner/repo"}), 400

    releases = fetch_releases(owner, repo, limit=5)
    localized = localize_releases(releases, target_lang=lang)
    count = save_releases(localized, language=lang)
    log_health("localize", "success", f"Localized {repo_full} to {lang}")

    return jsonify({
        "status": "success",
        "repo": repo_full,
        "language": lang,
        "count": len(localized),
        "releases": localized
    })


# ─── Retrieve ────────────────────────────────────────────────────────────────

@app.route("/releases")
def releases():
    lang = request.args.get("lang", "en")
    repo = request.args.get("repo", None)
    data = get_releases(language=lang, repo=repo)

    if not data:
        # Auto-seed with mock data if empty
        mock = get_mock_releases()
        save_releases(mock, language="en")
        data = get_releases(language="en")

    return jsonify({
        "language": lang,
        "count": len(data),
        "releases": data
    })


# ─── XLIFF Export & Validation ───────────────────────────────────────────────

@app.route("/export/xliff")
def export_xliff():
    """Export stored releases to XLIFF localization format."""
    lang = request.args.get("lang", "es")
    releases_data = get_releases(language=lang)

    if not releases_data:
        return jsonify({"error": f"No releases found for language '{lang}'. Run /localize first."}), 404

    # Map DB fields to XLIFF handler format
    formatted = []
    for r in releases_data:
        formatted.append({
            "repo": r["repo"],
            "version": r["version"],
            "name": r["name"],
            "content": r["content"],
            "translated_name": r.get("translated_name", r["name"]),
            "translated_content": r.get("translated_content", r["content"]),
            "url": r.get("url", ""),
        })

    filepath = export_to_xliff(formatted, source_lang="en", target_lang=lang)
    log_health("xliff_export", "success", f"Exported {len(formatted)} units to {filepath}")

    return send_file(filepath, as_attachment=True, mimetype="application/xliff+xml")


@app.route("/validate/xliff")
def validate():
    """Validate XLIFF file for missing or untranslated targets."""
    lang = request.args.get("lang", "es")
    filepath = f"xliff_exports/release_notes_en_to_{lang}.xliff"

    if not os.path.exists(filepath):
        return jsonify({"error": f"No XLIFF file found for lang={lang}. Run /export/xliff first."}), 404

    issues = validate_xliff(filepath)
    return jsonify({
        "file": filepath,
        "valid": len(issues) == 0,
        "issues_found": len(issues),
        "issues": issues
    })


# ─── Monitoring ──────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "log": get_health_log()
    })


@app.route("/stats")
def stats():
    return jsonify(get_stats())


@app.route("/languages")
def languages():
    return jsonify(get_supported_languages())


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # Seed with mock data so the API works immediately
    from fetcher import get_mock_releases
    mock = get_mock_releases()
    save_releases(mock, language="en")
    log_health("startup", "success", "App started, mock data seeded.")
    app.run(debug=True, port=5000)
