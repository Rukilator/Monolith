#!/usr/bin/env py -3
"""Generate Russian localization for _Mono prototypes."""
import os
import re
from pathlib import Path

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono")
LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono")

def extract_prototypes_from_yml(filepath):
    """Extract all prototypes from a yaml file."""
    prototypes = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
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

def translate_to_russian(text):
    """Translate English text to Russian."""
    if not text or text.startswith('ent-') or text.startswith('research-') or text.startswith('chat-') or text.startswith('mono-') or text.startswith('company-'):
        # Already a locale key, return as is
        return text
    
    # Simple translation mapping for common terms
    # In a real scenario, you'd use a translation API or service
    # For now, we'll return the text as-is and mark it for manual translation
    return text

def get_locale_key(proto_type, proto_id, field_name):
    """Generate locale key based on prototype type."""
    if proto_type == 'entity':
        return f"ent-{proto_id}"
    elif proto_type == 'company':
        if field_name == 'desc':
            # Company descriptions use kebab-case-id-description format
            kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
            return f"{kebab_id}-description"
        elif field_name == 'name':
            # Company names might use a key or be direct
            return None  # Companies usually have direct names
    elif proto_type == 'techDiscipline':
        # Uses the name field as-is (already a locale key)
        return None
    elif proto_type == 'gamePreset':
        if field_name == 'name':
            kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
            return f"mono-{kebab_id}-title"
        elif field_name == 'desc':
            kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
            return f"mono-{kebab_id}-description"
    elif proto_type == 'radioChannel':
        # Radio channels use chat-radio-{id} format
        kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
        return f"chat-radio-{kebab_id}"
    elif proto_type == 'tool':
        # Tool qualities use tool-quality-{id}-name format
        kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
        return f"tool-quality-{kebab_id}-name"
    
    # Default: use proto-type-id format
    kebab_id = re.sub(r'([A-Z])', r'-\1', proto_id).lower().lstrip('-')
    return f"{proto_type.lower()}-{kebab_id}"

def create_ftl_content(prototypes):
    """Create FTL file content from prototypes."""
    lines = []
    
    for proto in prototypes:
        proto_type = proto['type']
        proto_id = proto['id']
        name = proto['name']
        desc = proto['desc']
        
        if proto_type == 'entity':
            key = get_locale_key(proto_type, proto_id, 'name')
            if key:
                safe_name = (name or proto_id).replace("{", "{{").replace("}", "}}")
                lines.append(f"{key} = {safe_name}")
                if desc:
                    safe_desc = desc.replace("{", "{{").replace("}", "}}")
                    lines.append(f"    .desc = {safe_desc}")
        
        elif proto_type == 'company':
            # Companies: description uses locale key
            if desc and not desc.startswith('company-') and not desc.endswith('-description'):
                # It's a locale key reference
                key = desc
                # We'll add translation later
                lines.append(f"# {key} = [Translation needed]")
            elif desc:
                key = desc
                lines.append(f"# {key} = [Translation needed]")
        
        elif proto_type == 'techDiscipline':
            # Name is already a locale key, just add comment
            if name:
                lines.append(f"# {name} = [Translation needed]")
        
        elif proto_type == 'gamePreset':
            name_key = get_locale_key(proto_type, proto_id, 'name')
            desc_key = get_locale_key(proto_type, proto_id, 'desc')
            if name_key:
                lines.append(f"# {name_key} = [Translation needed]")
            if desc_key:
                lines.append(f"# {desc_key} = [Translation needed]")
        
        elif proto_type == 'radioChannel':
            if name:
                key = name  # Already a locale key
                lines.append(f"# {key} = [Translation needed]")
        
        elif proto_type == 'tool':
            if name:
                key = name  # Already a locale key
                lines.append(f"# {key} = [Translation needed]")
    
    return "\n".join(lines) + "\n" if lines else ""

def main():
    all_prototypes = []
    
    # Collect all prototypes from _Mono
    for yml_file in PROTOS.rglob("*.yml"):
        rel_path = yml_file.relative_to(PROTOS)
        print(f"Processing {rel_path}...")
        
        try:
            prototypes = extract_prototypes_from_yml(yml_file)
            for proto in prototypes:
                proto['rel_path'] = str(rel_path)
            all_prototypes.extend(prototypes)
        except Exception as e:
            print(f"  Error processing {rel_path}: {e}")
            continue
    
    print(f"\nFound {len(all_prototypes)} prototypes")
    
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
        ftl_content = create_ftl_content(items)
        
        if not ftl_content.strip():
            continue
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists
        existing_content = ""
        if out_path.exists():
            try:
                with open(out_path, encoding="utf-8") as f:
                    existing_content = f.read()
            except Exception as e:
                print(f"  Error reading {out_path}: {e}")
        
        # Write new content
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                if existing_content.strip():
                    f.write(existing_content + "\n" + ftl_content)
                else:
                    f.write(ftl_content)
            created += 1
            print(f"Created/updated {out_path}")
        except Exception as e:
            print(f"  Error writing {out_path}: {e}")
    
    print(f"\nTotal: {created} FTL files created/updated")

if __name__ == "__main__":
    main()
