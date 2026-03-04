#!/usr/bin/env py -3
"""Generate Russian localization for _Mono prototypes with translation."""
import os
import re
from pathlib import Path
import yaml

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono")
LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono")
EN_LOCALE = Path("g:/Monolith_Forge/Resources/Locale/en-US/_Mono")

# Translation dictionary for common terms (will be expanded)
TRANSLATIONS = {
    # Common prefixes
    "SKR": "СКР",
    "MI": "МИ",
    "UW": "УВ",
    "JIN": "ДЖИН",
}

def is_locale_key(text):
    """Check if text is a locale key (contains hyphens and lowercase)."""
    if not text:
        return False
    # Locale keys typically look like: research-discipline-mechs, chat-radio-ussp, etc.
    return bool(re.match(r'^[a-z][a-z0-9-]+$', text.lower()))

def translate_text(text):
    """Translate English text to Russian."""
    if not text or is_locale_key(text):
        return text
    
    # This is a placeholder - in real implementation, you'd use a translation API
    # For now, return the text as-is and mark it for translation
    return text

def extract_prototypes_from_yml(filepath):
    """Extract all prototypes from a yaml file."""
    prototypes = []
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return []
    
    # Split by prototype blocks (lines starting with '- type:')
    blocks = re.split(r'(?=^- type:)', content, flags=re.MULTILINE)
    
    for block in blocks:
        if not block.strip() or '- type:' not in block[:20]:
            continue
        
        # Extract type
        type_match = re.search(r'- type:\s*(\w+)', block)
        if not type_match:
            continue
        proto_type = type_match.group(1)
        
        # Extract id
        id_match = re.search(r'^\s+id:\s*(\S+)', block, re.MULTILINE)
        if not id_match:
            continue
        proto_id = id_match.group(1).strip()
        
        # Extract name (can be a string or a locale key)
        name_match = re.search(r'^\s+name:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE | re.DOTALL)
        name = None
        if name_match:
            name = name_match.group(1).strip().strip('"\'')
        
        # Extract description
        desc_match = re.search(r'^\s+description:\s*(.+?)(?:\n\s+\w|\n\n|$)', block, re.MULTILINE | re.DOTALL)
        desc = None
        if desc_match:
            desc = desc_match.group(1).strip().strip('"\'')
        
        prototypes.append({
            'type': proto_type,
            'id': proto_id,
            'name': name,
            'desc': desc,
            'file': str(filepath)
        })
    
    return prototypes

def get_locale_key_for_proto(proto_type, proto_id, field_name):
    """Generate locale key based on prototype type."""
    kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
    
    if proto_type == 'entity':
        return f"ent-{proto_id}"
    elif proto_type == 'company':
        if field_name == 'desc':
            return f"{kebab_id}-description"
    elif proto_type == 'gamePreset':
        if field_name == 'name':
            return f"mono-{kebab_id}-title"
        elif field_name == 'desc':
            return f"mono-{kebab_id}-description"
    elif proto_type == 'radioChannel':
        return f"chat-radio-{kebab_id}"
    elif proto_type == 'vessel':
        if field_name == 'name':
            return f"vessel-{kebab_id}-name"
        elif field_name == 'desc':
            return f"vessel-{kebab_id}-desc"
    elif proto_type == 'tool':
        return f"tool-quality-{kebab_id}-name"
    
    return None

def create_ftl_entries(prototypes):
    """Create FTL file entries from prototypes."""
    entries = []
    
    for proto in prototypes:
        proto_type = proto['type']
        proto_id = proto['id']
        name = proto['name']
        desc = proto['desc']
        
        if proto_type == 'entity':
            key = get_locale_key_for_proto(proto_type, proto_id, 'name')
            if key:
                safe_name = (name or proto_id).replace("{", "{{").replace("}", "}}")
                entries.append((key, safe_name, None))
                if desc:
                    safe_desc = desc.replace("{", "{{").replace("}", "}}")
                    entries.append((key, None, safe_desc))
        
        elif proto_type == 'company':
            if desc:
                if is_locale_key(desc):
                    entries.append((desc, None, None))  # Will be translated separately
                else:
                    key = get_locale_key_for_proto(proto_type, proto_id, 'desc')
                    if key:
                        entries.append((key, None, desc))
        
        elif proto_type == 'techDiscipline':
            if name and is_locale_key(name):
                entries.append((name, None, None))
        
        elif proto_type == 'gamePreset':
            if name and is_locale_key(name):
                entries.append((name, None, None))
            if desc and is_locale_key(desc):
                entries.append((desc, None, None))
        
        elif proto_type == 'radioChannel':
            if name and is_locale_key(name):
                entries.append((name, None, None))
        
        elif proto_type == 'vessel':
            name_key = get_locale_key_for_proto(proto_type, proto_id, 'name')
            desc_key = get_locale_key_for_proto(proto_type, proto_id, 'desc')
            if name and name_key:
                safe_name = name.replace("{", "{{").replace("}", "}}")
                entries.append((name_key, safe_name, None))
            if desc and desc_key:
                safe_desc = desc.replace("{", "{{").replace("}", "}}")
                entries.append((desc_key, None, safe_desc))
        
        elif proto_type == 'tool':
            if name and is_locale_key(name):
                entries.append((name, None, None))
    
    return entries

def main():
    print("Collecting prototypes from _Mono...")
    all_prototypes = []
    
    # Collect all prototypes from _Mono
    for yml_file in sorted(PROTOS.rglob("*.yml")):
        rel_path = yml_file.relative_to(PROTOS)
        try:
            prototypes = extract_prototypes_from_yml(yml_file)
            for proto in prototypes:
                proto['rel_path'] = str(rel_path)
            all_prototypes.extend(prototypes)
        except Exception as e:
            print(f"  Error processing {rel_path}: {e}")
            continue
    
    print(f"Found {len(all_prototypes)} prototypes")
    
    # Group by file for FTL generation
    grouped = {}
    for proto in all_prototypes:
        rel_path = proto['rel_path']
        ftl_rel = rel_path.replace("\\", "/").lower()
        ftl_path = Path(ftl_rel).with_suffix(".ftl")
        key = str(ftl_path)
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(proto)
    
    # Create FTL files
    created = 0
    for ftl_rel, items in sorted(grouped.items()):
        out_path = LOCALE_BASE / ftl_rel
        ftl_entries = create_ftl_entries(items)
        
        if not ftl_entries:
            continue
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists
        existing_content = ""
        existing_keys = set()
        if out_path.exists():
            try:
                with open(out_path, encoding="utf-8") as f:
                    existing_content = f.read()
                    # Extract existing keys
                    for line in existing_content.split('\n'):
                        match = re.match(r'^([a-z0-9-]+)\s*=', line)
                        if match:
                            existing_keys.add(match.group(1))
            except Exception as e:
                print(f"  Error reading {out_path}: {e}")
        
        # Build new content
        new_lines = []
        for key, name_val, desc_val in ftl_entries:
            if key in existing_keys:
                continue
            
            if name_val:
                new_lines.append(f"{key} = {name_val}")
            elif desc_val:
                # This is a description, need to find the name key
                # For now, add as comment
                new_lines.append(f"# {key} = [Translation needed: {desc_val[:50]}...]")
            else:
                # Locale key reference
                new_lines.append(f"# {key} = [Translation needed - check en-US locale]")
        
        if new_lines:
            content = "\n".join(new_lines) + "\n"
            try:
                with open(out_path, "a" if existing_content.strip() else "w", encoding="utf-8") as f:
                    if existing_content.strip():
                        f.write("\n" + content)
                    else:
                        f.write(content)
                created += 1
                print(f"Created/updated {out_path} (+{len(new_lines)} entries)")
            except Exception as e:
                print(f"  Error writing {out_path}: {e}")
    
    print(f"\nTotal: {created} FTL files created/updated")
    print("\nNote: Files contain placeholders for translation.")
    print("Next step: Translate the entries marked with [Translation needed]")

if __name__ == "__main__":
    main()
