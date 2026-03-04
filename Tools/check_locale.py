#!/usr/bin/env py -3
"""Find entity prototypes missing ru-RU localization."""
import os
import re
from pathlib import Path

PROTOS = Path("g:/Monolith_Forge/Resources/Prototypes")
LOCALE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU")

def get_entity_ids_from_yml(filepath):
    """Extract entity prototype IDs from a yaml file."""
    ids = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    # Match 'id: SomeId' at start of entity block (after 'type: entity')
    for m in re.finditer(r'- type: entity\s+id: (\w+)', content):
        ids.append(m.group(1))
    # Also match standalone id in entity-like context
    for m in re.finditer(r'^  id: (\w+)\s*$', content, re.MULTILINE):
        ids.append(m.group(1))
    return ids

def get_localized_ent_keys():
    """Get all ent-* keys from ru-RU ftl files."""
    keys = set()
    for ftl in LOCALE.rglob("*.ftl"):
        try:
            with open(ftl, encoding="utf-8") as f:
                for line in f:
                    m = re.match(r'^(ent-[a-zA-Z0-9_]+)\s*=', line)
                    if m:
                        keys.add(m.group(1))
                    m2 = re.match(r'^([a-zA-Z0-9_-]+)\s*=', line)
                    if m2 and m2.group(1).startswith("ent-"):
                        keys.add(m2.group(1))
        except (PermissionError, OSError):
            pass
    return keys

def extract_name_desc(text, eid):
    """Extract name and description for entity id from yaml text."""
    name, desc = eid, ""
    # Find block containing this id (block = from - type: to next - type: or end)
    pat = rf'id:\s*{re.escape(eid)}\s*(?:\n|$)'
    m = re.search(pat, text)
    if m:
        start = max(0, m.start() - 200)
        block = text[start:m.end() + 500]
        nm = re.search(r'name:\s*(.+?)(?:\n\s*\w|\n\n|$)', block)
        dm = re.search(r'description:\s*(.+?)(?:\n\s*\w|\n\n|$)', block)
        if nm:
            name = nm.group(1).strip().strip('"\'')
        if dm:
            desc = dm.group(1).strip().strip('"\'')
    return name, desc

def get_prototype_info(proto_path):
    """Get id, name, description from prototype yml. Returns dict id->{name,desc,file}."""
    result = {}
    with open(proto_path, encoding="utf-8") as f:
        content = f.read()
    # Split by --- or - type: entity
    blocks = re.split(r'(?=^- type: entity)', content)
    for block in blocks:
        if 'type: entity' not in block[:20]:
            continue
        mid = re.search(r'id:\s*(\w+)', block)
        mname = re.search(r'name:\s*(.+)', block)
        mdesc = re.search(r'description:\s*(.+)', block)
        if mid:
            info = {
                "name": mname.group(1).strip() if mname else mid.group(1),
                "desc": mdesc.group(1).strip() if mdesc else "",
                "file": str(proto_path)
            }
            result[mid.group(1)] = info
    return result

def main():
    localized = get_localized_ent_keys()
    print(f"Found {len(localized)} localized ent- keys in ru-RU")

    missing = []  # (proto_path, id, name, desc)
    for yml in PROTOS.rglob("*.yml"):
        rel = yml.relative_to(PROTOS)
        # Focus on _Forge and _NF (custom) prototypes
        relstr = str(rel)
        if "_Forge" not in relstr and "_NF" not in relstr:
            continue
        with open(yml, encoding="utf-8") as f:
            text = f.read()
        if "type: entity" not in text:
            continue
        # Get entity IDs
        ids = set()
        for m in re.finditer(r'^\s+id:\s+(\w+)\s*$', text, re.MULTILINE):
            ids.add(m.group(1))
        for eid in ids:
            key = f"ent-{eid}"
            if key not in localized:
                name, desc = extract_name_desc(text, eid)
                missing.append((str(rel), eid, name, desc))

    # Dedupe by id (keep first)
    seen = set()
    unique = []
    for p, i, n, d in missing:
        if i not in seen:
            seen.add(i)
            unique.append((p, i, n, d))

    print(f"Missing localization: {len(unique)} entity prototypes")
    for rel, eid, name, desc in sorted(unique, key=lambda x: x[0])[:80]:
        print(f"  {rel} -> ent-{eid} | name={name[:40] if len(name)<40 else name[:37]+'...'}")

    # Create FTL files
    BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes")
    grouped = {}
    for rel, eid, name, desc in unique:
        ftl_rel = rel.replace("\\", "/").lower()
        ftl_path = Path(ftl_rel).with_suffix(".ftl")
        key = str(ftl_path)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((eid, name, desc))

    created = 0
    for ftl_rel, items in sorted(grouped.items()):
        out_path = BASE / ftl_rel
        new_entries = []
        for eid, name, desc in items:
            key = f"ent-{eid}"
            safe_name = (name or eid).replace("{", "{{").replace("}", "}}")
            safe_desc = (desc or "").replace("{", "{{").replace("}", "}}")
            new_entries.append((key, safe_name, safe_desc))
        if not new_entries:
            continue
        out_path.parent.mkdir(parents=True, exist_ok=True)
        existing_content = ""
        if out_path.exists():
            try:
                with open(out_path, encoding="utf-8") as f:
                    existing_content = f.read()
            except (PermissionError, OSError):
                pass
        existing_keys = set(re.findall(r'^(ent-\w+)\s*=', existing_content, re.MULTILINE))
        lines_to_add = []
        for key, safe_name, safe_desc in new_entries:
            if key in existing_keys:
                continue
            lines_to_add.append(f"{key} = {safe_name}")
            if safe_desc:
                lines_to_add.append(f"    .desc = {safe_desc}")
        if lines_to_add:
            content = "\n".join(lines_to_add) + "\n"
            with open(out_path, "a" if existing_content.strip() else "w", encoding="utf-8") as f:
                if existing_content.strip():
                    f.write("\n" + content)
                else:
                    f.write(content)
            created += 1
            n_ent = sum(1 for l in lines_to_add if not l.strip().startswith("."))
            print(f"Created/updated {out_path} (+{n_ent} entries)")
    print(f"Total: {created} FTL files created/updated")

if __name__ == "__main__":
    main()
