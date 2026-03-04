#!/usr/bin/env py -3
"""Final script to translate _Mono prototypes to Russian."""
import os
import re
from pathlib import Path

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono")
LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono")
EN_LOCALE = Path("g:/Monolith_Forge/Resources/Locale/en-US/_Mono")

def is_locale_key(text):
    """Check if text is a locale key."""
    if not text:
        return False
    return bool(re.match(r'^[a-z][a-z0-9-]+$', text.lower()))

def kebab_case(text):
    """Convert text to kebab-case."""
    return re.sub(r'([A-Z])', r'-\1', text).lower().lstrip('-')

def extract_vessel_prototypes(filepath):
    """Extract vessel prototypes from yaml file."""
    vessels = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return []
    
    # Find all vessel prototypes
    vessel_pattern = r'- type: vessel\s+id: (\w+)(.*?)(?=- type:|\Z)'
    for match in re.finditer(vessel_pattern, content, re.DOTALL):
        vessel_id = match.group(1)
        block = match.group(2)
        
        # Extract name
        name_match = re.search(r'name:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
        name = name_match.group(1).strip().strip('"\'') if name_match else None
        
        # Extract description
        desc_match = re.search(r'description:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
        desc = desc_match.group(1).strip().strip('"\'') if desc_match else None
        
        if name or desc:
            vessels.append({
                'id': vessel_id,
                'name': name,
                'desc': desc
            })
    
    return vessels

def translate_vessel_text(text):
    """Translate vessel text to Russian."""
    if not text:
        return text
    
    # Simple translations for common terms
    translations = {
        "MI": "МИ",
        "UW": "УВ", 
        "JIN": "ДЖИН",
        "SKR": "СКР",
    }
    
    # Replace prefixes
    for eng, rus in translations.items():
        if text.startswith(eng + " "):
            text = text.replace(eng + " ", rus + " ", 1)
    
    # This is a placeholder - actual translation would happen here
    # For now, return as-is
    return text

def create_vessel_ftl(vessels, output_path):
    """Create FTL file for vessels."""
    lines = []
    
    for vessel in vessels:
        vessel_id = vessel['id']
        name = vessel['name']
        desc = vessel['desc']
        
        kebab_id = kebab_case(vessel_id)
        
        if name:
            name_key = f"vessel-{kebab_id}-name"
            # Translate name
            translated_name = translate_vessel_text(name)
            lines.append(f"{name_key} = {translated_name}")
        
        if desc:
            desc_key = f"vessel-{kebab_id}-desc"
            # Translate description
            translated_desc = translate_vessel_text(desc)
            lines.append(f"{desc_key} = {translated_desc}")
    
    if lines:
        content = "\n".join(lines) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return len(lines)
    return 0

def main():
    print("Processing vessel prototypes from _Mono/Shipyard...")
    
    shipyard_dir = PROTOS / "Shipyard"
    total_entries = 0
    
    for yml_file in sorted(shipyard_dir.rglob("*.yml")):
        if yml_file.name == "base.yml":
            continue  # Skip base vessel
        
        rel_path = yml_file.relative_to(PROTOS)
        vessels = extract_vessel_prototypes(yml_file)
        
        if not vessels:
            continue
        
        # Create FTL file path
        ftl_rel = str(rel_path).replace("\\", "/").lower()
        ftl_path = Path(ftl_rel).with_suffix(".ftl")
        out_path = LOCALE_BASE / ftl_path
        
        entries = create_vessel_ftl(vessels, out_path)
        if entries > 0:
            total_entries += entries
            print(f"Created {out_path} (+{entries} entries)")
    
    print(f"\nTotal: {total_entries} vessel entries created")
    print("\nNote: Names and descriptions need manual translation to Russian.")

if __name__ == "__main__":
    main()
