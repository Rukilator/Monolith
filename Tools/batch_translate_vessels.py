#!/usr/bin/env py -3
"""Batch translate vessel prototypes - reads existing FTL files and translates them."""
import os
import re
from pathlib import Path

LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono/shipyard")
PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono/Shipyard")

# Translation dictionary for common prefixes and terms
PREFIX_TRANSLATIONS = {
    "TSF-SKR": "TSF-СКР",
    "MI": "МИ",
    "UW": "УВ",
    "JIN": "ДЖИН",
    "HME": "HME",
    "DIS": "DIS",
    "SHS-DIS": "SHS-DIS",
    "PB": "ПБ",
    "ZOB": "ЗОБ",
    "MI-COR": "МИ-КОР",
    "HES": "HES",
    "Z-22": "Z-22",
}

def translate_vessel_name(name):
    """Translate vessel name preserving prefixes."""
    if not name:
        return name
    
    # Check for known prefixes
    for prefix, translation in PREFIX_TRANSLATIONS.items():
        if name.startswith(prefix + " "):
            return name.replace(prefix + " ", translation + " ", 1)
    
    return name

def translate_description(desc):
    """Translate description text."""
    if not desc:
        return desc
    
    # This is a placeholder - actual translation logic would go here
    # For now, return as-is
    return desc

def process_ftl_file(ftl_path):
    """Process a single FTL file and translate entries."""
    if not ftl_path.exists():
        return False
    
    try:
        with open(ftl_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {ftl_path}: {e}")
        return False
    
    # Check if already translated (contains Cyrillic)
    if re.search(r'[А-Яа-я]', content):
        return False  # Already translated
    
    lines = content.split('\n')
    translated_lines = []
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            translated_lines.append(line)
            continue
        
        # Match vessel-name or vessel-desc entries
        name_match = re.match(r'^(vessel-\w+-name)\s*=\s*(.+)$', line)
        desc_match = re.match(r'^(vessel-\w+-desc)\s*=\s*(.+)$', line)
        
        if name_match:
            key, value = name_match.groups()
            translated_value = translate_vessel_name(value)
            translated_lines.append(f"{key} = {translated_value}")
        elif desc_match:
            key, value = desc_match.groups()
            translated_value = translate_description(value)
            translated_lines.append(f"{key} = {translated_value}")
        else:
            translated_lines.append(line)
    
    new_content = "\n".join(translated_lines)
    if new_content != content:
        try:
            with open(ftl_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"  Error writing {ftl_path}: {e}")
            return False
    
    return False

def main():
    print("Processing vessel FTL files for translation...")
    
    translated_count = 0
    for ftl_file in sorted(LOCALE_BASE.rglob("*.ftl")):
        rel_path = ftl_file.relative_to(LOCALE_BASE)
        if process_ftl_file(ftl_file):
            translated_count += 1
            print(f"Translated {rel_path}")
    
    print(f"\nTotal: {translated_count} files processed")
    print("\nNote: This script only handles prefix translations.")
    print("Full descriptions need manual translation.")

if __name__ == "__main__":
    main()
