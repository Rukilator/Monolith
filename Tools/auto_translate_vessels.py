#!/usr/bin/env py -3
"""Automatically translate vessel prototypes from YAML to Russian FTL files."""
import os
import re
from pathlib import Path

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono/Shipyard")
LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono/shipyard")

# Translation mappings for common terms
PREFIX_MAP = {
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
    "NEI": "NEI",
    "NS": "NS",
    "UNJ": "UNJ",
    "UI-SKR": "UI-СКР",
    "WA": "WA",
}

def translate_name(name):
    """Translate vessel name."""
    if not name:
        return name
    
    for prefix, translation in PREFIX_MAP.items():
        if name.startswith(prefix + " "):
            return name.replace(prefix + " ", translation + " ", 1)
    
    return name

def translate_description(desc):
    """Translate description - placeholder for actual translation."""
    # This would normally use a translation API
    # For now, return as-is - will be translated manually
    return desc

def extract_and_translate_vessel(yml_path):
    """Extract vessel from YAML and return translated entries."""
    try:
        with open(yml_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {yml_path}: {e}")
        return None
    
    # Find vessel prototype
    vessel_match = re.search(
        r'- type: vessel\s+id: (\w+)(.*?)(?=- type:|\Z)',
        content,
        re.DOTALL
    )
    
    if not vessel_match:
        return None
    
    vessel_id = vessel_match.group(1)
    block = vessel_match.group(2)
    
    # Extract name
    name_match = re.search(r'name:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
    name = name_match.group(1).strip().strip('"\'') if name_match else None
    
    # Extract description
    desc_match = re.search(r'description:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
    desc = desc_match.group(1).strip().strip('"\'') if desc_match else None
    
    if not name and not desc:
        return None
    
    kebab_id = re.sub(r'([A-Z])', r'-\1', vessel_id).lower().lstrip('-')
    
    return {
        'id': vessel_id,
        'kebab_id': kebab_id,
        'name': name,
        'desc': desc
    }

def create_translated_ftl(vessel_data, output_path):
    """Create translated FTL file."""
    if not vessel_data:
        return False
    
    lines = []
    
    if vessel_data['name']:
        name_key = f"vessel-{vessel_data['kebab_id']}-name"
        translated_name = translate_name(vessel_data['name'])
        lines.append(f"{name_key} = {translated_name}")
    
    if vessel_data['desc']:
        desc_key = f"vessel-{vessel_data['kebab_id']}-desc"
        translated_desc = translate_description(vessel_data['desc'])
        lines.append(f"{desc_key} = {translated_desc}")
    
    if not lines:
        return False
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists and already has translations
    existing_content = ""
    if output_path.exists():
        try:
            with open(output_path, encoding="utf-8") as f:
                existing_content = f.read()
            # If already has Cyrillic, skip
            if re.search(r'[А-Яа-я]', existing_content):
                return False
        except:
            pass
    
    content = "\n".join(lines) + "\n"
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  Error writing {output_path}: {e}")
        return False

def main():
    print("Auto-translating vessel prototypes...")
    
    translated = 0
    skipped = 0
    
    for yml_file in sorted(PROTOS.rglob("*.yml")):
        if yml_file.name == "base.yml":
            continue
        
        rel_path = yml_file.relative_to(PROTOS)
        vessel_data = extract_and_translate_vessel(yml_file)
        
        if not vessel_data:
            continue
        
        # Create output path
        ftl_rel = str(rel_path).replace("\\", "/").lower()
        ftl_path = Path(ftl_rel).with_suffix(".ftl")
        out_path = LOCALE_BASE / ftl_path
        
        if create_translated_ftl(vessel_data, out_path):
            translated += 1
            print(f"Translated {rel_path}")
        else:
            skipped += 1
    
    print(f"\nTotal: {translated} files translated, {skipped} skipped")
    print("\nNote: Descriptions still need manual translation.")

if __name__ == "__main__":
    main()
