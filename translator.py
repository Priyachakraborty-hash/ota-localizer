import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh-CN": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ar": "Arabic",
    "hi": "Hindi",
    "it": "Italian",
}


def translate_text(text, target_lang="es"):
    """Translate a single text string."""
    if not text or not text.strip():
        return text
    try:
        result = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return result
    except Exception as e:
        logger.error(f"Translation error [{target_lang}]: {e}")
        return text  # Graceful fallback


def localize_releases(releases, target_lang="es"):
    """
    Translate a list of release note dicts.
    Adds translated_name and translated_content fields.
    """
    localized = []
    for release in releases:
        loc = dict(release)
        loc["translated_name"] = translate_text(release["name"], target_lang)
        loc["translated_content"] = translate_text(release["content"], target_lang)
        loc["target_language"] = target_lang
        localized.append(loc)
        logger.info(f"Localized: {release['version']} → {target_lang}")
    return localized


def get_supported_languages():
    return SUPPORTED_LANGUAGES
