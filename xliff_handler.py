import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import logging

logger = logging.getLogger(__name__)

XLIFF_DIR = "xliff_exports"


def export_to_xliff(notes, source_lang="en", target_lang="es"):
    """
    Export release notes to XLIFF 1.2 format.
    XLIFF (XML Localization Interchange File Format) is the industry
    standard for software localization workflows.
    """
    os.makedirs(XLIFF_DIR, exist_ok=True)

    # XLIFF root
    xliff = ET.Element("xliff", attrib={
        "version": "1.2",
        "xmlns": "urn:oasis:names:tc:xliff:document:1.2"
    })

    for note in notes:
        repo_safe = note["repo"].replace("/", "_")
        file_elem = ET.SubElement(xliff, "file", attrib={
            "original": note.get("url", "unknown"),
            "source-language": source_lang,
            "target-language": target_lang,
            "datatype": "plaintext",
            "product-name": note["repo"],
            "product-version": note["version"],
        })

        body = ET.SubElement(file_elem, "body")

        # Version as a translation unit
        tu_version = ET.SubElement(body, "trans-unit", attrib={
            "id": f"{repo_safe}_{note['version']}_title"
        })
        ET.SubElement(tu_version, "source").text = note["name"]
        ET.SubElement(tu_version, "target").text = note.get("translated_name", note["name"])

        # Content as a translation unit
        tu_content = ET.SubElement(body, "trans-unit", attrib={
            "id": f"{repo_safe}_{note['version']}_content"
        })
        ET.SubElement(tu_content, "source").text = note["content"]
        ET.SubElement(tu_content, "target").text = note.get("translated_content", note["content"])

    # Pretty-print XML
    raw_xml = ET.tostring(xliff, encoding="unicode")
    pretty_xml = minidom.parseString(raw_xml).toprettyxml(indent="  ")

    filename = f"{XLIFF_DIR}/release_notes_{source_lang}_to_{target_lang}.xliff"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    logger.info(f"Exported {len(notes)} notes to {filename}")
    return filename


def parse_xliff(filepath):
    """Parse an existing XLIFF file and return translation units."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"x": "urn:oasis:names:tc:xliff:document:1.2"}

    units = []
    for file_elem in root.findall("x:file", ns):
        for tu in file_elem.findall(".//x:trans-unit", ns):
            source = tu.find("x:source", ns)
            target = tu.find("x:target", ns)
            units.append({
                "id": tu.get("id"),
                "source": source.text if source is not None else "",
                "target": target.text if target is not None else "",
            })
    return units


def validate_xliff(filepath):
    """
    Validate an XLIFF file — check for missing targets.
    Returns list of issues found.
    """
    units = parse_xliff(filepath)
    issues = []
    for unit in units:
        if not unit["target"] or unit["target"] == unit["source"]:
            issues.append(f"Missing/untranslated target for unit: {unit['id']}")

    if issues:
        logger.warning(f"Validation found {len(issues)} issues in {filepath}")
    else:
        logger.info(f"Validation passed for {filepath}")

    return issues
