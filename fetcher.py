import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}/releases"

# Track popular software projects with real release notes
DEFAULT_REPOS = [
    {"owner": "microsoft", "repo": "vscode"},
    {"owner": "flutter",   "repo": "flutter"},
    {"owner": "nodejs",    "repo": "node"},
    {"owner": "python",    "repo": "cpython"},
]


def fetch_releases(owner, repo, limit=5):
    """Fetch latest releases from GitHub API for any repo."""
    url = GITHUB_API.format(owner=owner, repo=repo)
    try:
        logger.info(f"Fetching releases for {owner}/{repo}...")
        response = requests.get(url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        response.raise_for_status()
        releases = response.json()[:limit]

        results = []
        for r in releases:
            body = r.get("body") or ""
            # Clean markdown artifacts
            body = body.replace("##", "").replace("**", "").replace("*", "").strip()
            if not body:
                continue
            results.append({
                "repo": f"{owner}/{repo}",
                "version": r.get("tag_name", "unknown"),
                "name": r.get("name") or r.get("tag_name", "Untitled"),
                "content": body[:500],  # cap for translation efficiency
                "url": r.get("html_url", ""),
                "published_at": r.get("published_at", ""),
            })

        logger.info(f"Got {len(results)} releases for {owner}/{repo}")
        return results

    except Exception as e:
        logger.error(f"Failed to fetch {owner}/{repo}: {e}")
        return get_mock_releases(owner, repo)


def get_mock_releases(owner="demo", repo="project"):
    """Fallback mock data for offline/testing use."""
    logger.info("Using mock release data.")
    return [
        {
            "repo": f"{owner}/{repo}",
            "version": "v3.2.0",
            "name": "v3.2.0 - Performance & Stability Release",
            "content": (
                "Performance improvements: Reduced startup time by 40%. "
                "Fixed critical bug causing crashes on low-memory devices. "
                "Added support for dark mode across all screens. "
                "Improved battery efficiency for background processes."
            ),
            "url": "https://github.com",
            "published_at": "2024-11-01T10:00:00Z",
        },
        {
            "repo": f"{owner}/{repo}",
            "version": "v3.1.5",
            "name": "v3.1.5 - Security Patch",
            "content": (
                "Security fix: Patched authentication vulnerability in OAuth2 flow. "
                "Updated dependency versions to address known CVEs. "
                "Improved input validation across API endpoints."
            ),
            "url": "https://github.com",
            "published_at": "2024-10-15T10:00:00Z",
        },
        {
            "repo": f"{owner}/{repo}",
            "version": "v3.1.0",
            "name": "v3.1.0 - New Features",
            "content": (
                "New feature: Real-time collaboration support added. "
                "Redesigned settings panel for easier navigation. "
                "Localization support expanded to 12 new languages."
            ),
            "url": "https://github.com",
            "published_at": "2024-09-20T10:00:00Z",
        },
    ]


def fetch_all_default_repos(limit=3):
    """Fetch releases from all default tracked repos."""
    all_releases = []
    for repo in DEFAULT_REPOS:
        releases = fetch_releases(repo["owner"], repo["repo"], limit=limit)
        all_releases.extend(releases)
    return all_releases
