#!/usr/bin/env py -3
"""Fix corrupted translations in SpaceArtillery folder."""
import os
import re
from pathlib import Path

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono/Entities/SpaceArtillery")
LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono/entities/SpaceArtillery")

def extract_entities_from_yml(yml_path):
    """Extract entity prototypes from YAML file."""
    entities = []
    try:
        with open(yml_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {yml_path}: {e}")
        return []
    
    # Find all entity prototypes
    entity_pattern = r'- type: entity\s+id: (\w+)(.*?)(?=- type:|\Z)'
    for match in re.finditer(entity_pattern, content, re.DOTALL):
        entity_id = match.group(1)
        block = match.group(2)
        
        # Extract name
        name_match = re.search(r'name:\s*"?(.+?)"?\s*(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
        name = name_match.group(1).strip().strip('"\'') if name_match else None
        
        # Extract description
        desc_match = re.search(r'description:\s*"?(.+?)"?\s*(?:\n\s+\w|\n\n|$)', block, re.MULTILINE)
        desc = desc_match.group(1).strip().strip('"\'') if desc_match else None
        
        if name or desc:
            entities.append({
                'id': entity_id,
                'name': name,
                'desc': desc
            })
    
    return entities

def translate_text(text):
    """Translate English text to Russian."""
    if not text:
        return text
    
    # Translation dictionary for common terms
    translations = {
        "ammo loader": "загрузчик боеприпасов",
        "ammunition loader": "загрузчик боеприпасов",
        "containing infinite": "содержащий бесконечные",
        "Usable by vessel-mounted artillery pieces": "Используется корабельными артиллерийскими орудиями",
        "cartridge": "патрон",
        "solid": "цельные",
        "high-explosive": "осколочно-фугасные",
        "HE": "ОФ",
        "AP": "бронебойный",
        "rounds": "патроны",
        "Solid": "цельный",
    }
    
    # Apply translations
    translated = text
    for eng, rus in translations.items():
        translated = translated.replace(eng, rus)
    
    # Handle specific patterns
    translated = re.sub(r'(\d+)mm', r'\1мм', translated)
    translated = re.sub(r'(\d+)x(\d+)mm', r'\1x\2мм', translated)
    
    return translated

def create_ftl_content(entities):
    """Create FTL file content from entities."""
    lines = []
    
    for entity in entities:
        entity_id = entity['id']
        name = entity['name']
        desc = entity['desc']
        
        key = f"ent-{entity_id}"
        
        if name:
            translated_name = translate_text(name)
            safe_name = translated_name.replace("{", "{{").replace("}", "}}")
            lines.append(f"{key} = {safe_name}")
        
        if desc:
            translated_desc = translate_text(desc)
            safe_desc = translated_desc.replace("{", "{{").replace("}", "}}")
            lines.append(f"    .desc = {safe_desc}")
    
    return "\n".join(lines) + "\n" if lines else ""

def main():
    print("Fixing SpaceArtillery translations...")
    
    fixed_count = 0
    
    # Process all YAML files
    for yml_file in sorted(PROTOS.rglob("*.yml")):
        rel_path = yml_file.relative_to(PROTOS)
        entities = extract_entities_from_yml(yml_file)
        
        if not entities:
            continue
        
        # Create corresponding FTL path
        ftl_rel = str(rel_path).replace("\\", "/").lower()
        ftl_path = Path(ftl_rel).with_suffix(".ftl")
        out_path = LOCALE_BASE / ftl_path
        
        ftl_content = create_ftl_content(entities)
        
        if ftl_content.strip():
            out_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(ftl_content)
                fixed_count += 1
                print(f"Fixed {rel_path}")
            except Exception as e:
                print(f"  Error writing {out_path}: {e}")
    
    print(f"\nTotal: {fixed_count} files fixed")

if __name__ == "__main__":
    main()
