#!/usr/bin/env py -3
"""Improve all translations in SpaceArtillery folder - fix English words and improve quality."""
import os
import re
from pathlib import Path

LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono/entities/SpaceArtillery")

# Dictionary for common translations
TRANSLATIONS = {
    "A ": "",
    "An ": "",
    "shell": "снаряд",
    "projectile": "снаряд",
    "cartridge": "патрон",
    "slug": "снаряд",
    "ammo loader": "загрузчик боеприпасов",
    "ammunition loader": "загрузчик боеприпасов",
    "containing": "содержащий",
    "infinite": "бесконечные",
    "Usable by": "Используется",
    "vessel-mounted": "корабельными",
    "artillery pieces": "артиллерийскими орудиями",
    "chemically-propelled": "химически-приводимый",
    "for": "для",
    "cannons": "пушек",
    "used in": "используемый в",
    "such as": "таких как",
    "Nothing fancy": "Ничего особенного",
    "all-in-one package": "комплектный пакет",
    "plasma gas accelerant": "плазменный газовый ускоритель",
    "high-density tungsten": "вольфрамовый высокой плотности",
    "Cheap": "Дешевый",
    "devastating": "разрушительный",
    "long ranged": "дальнобойный",
    "low-yield fission warhead": "низкобюджетная ядерная боеголовка деления",
    "May cause": "Может вызвать",
    "public outcry": "общественный резонанс",
    "but you": "но вам",
    "had": "пришлось",
    "to use this": "это использовать",
    "right": "верно",
    "NUCLEAR": "ЯДЕРНЫЙ",
    "CARNAGE": "РЕЗНЯ",
    "Once the genie is out of the bottle": "Когда джинн вылетел из бутылки",
    "there's no putting it back inside": "его уже не вернуть обратно",
    "tarkhan": "тархан",
    "Its not very good": "Он не очень хорош",
    "as most": "так как большинство",
    "are optimized for": "оптимизированы для",
    "Its a crude method": "Это грубый метод",
    "and it certainly wouldn't pass": "и он определенно не прошел бы",
    "inspection": "проверку",
}

def fix_translation(text):
    """Fix translation by removing English words and improving quality."""
    if not text:
        return text
    
    # Remove common English articles and words
    fixed = text
    
    # Apply translations
    for eng, rus in TRANSLATIONS.items():
        fixed = fixed.replace(eng, rus)
    
    # Fix common patterns
    fixed = re.sub(r'\s+', ' ', fixed)  # Multiple spaces
    fixed = fixed.strip()
    
    # Capitalize first letter
    if fixed:
        fixed = fixed[0].upper() + fixed[1:] if len(fixed) > 1 else fixed.upper()
    
    return fixed

def process_ftl_file(ftl_path):
    """Process and fix a single FTL file."""
    if not ftl_path.exists():
        return False
    
    try:
        with open(ftl_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {ftl_path}: {e}")
        return False
    
    # Check if already has proper Russian (no English words like "A ", "An ", "shell", etc.)
    has_english = bool(re.search(r'\b(A|An|shell|projectile|cartridge)\s+', content, re.IGNORECASE))
    
    if not has_english:
        return False  # Already fixed
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Match FTL entries
        name_match = re.match(r'^(ent-\w+)\s*=\s*(.+)$', line)
        desc_match = re.match(r'^(\s+\.desc\s*=\s*)(.+)$', line)
        
        if name_match:
            key, value = name_match.groups()
            fixed_value = fix_translation(value)
            fixed_lines.append(f"{key} = {fixed_value}")
        elif desc_match:
            prefix, value = desc_match.groups()
            fixed_value = fix_translation(value)
            fixed_lines.append(f"{prefix}{fixed_value}")
        else:
            fixed_lines.append(line)
    
    new_content = "\n".join(fixed_lines)
    
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
    print("Improving SpaceArtillery translations...")
    
    fixed_count = 0
    
    for ftl_file in sorted(LOCALE_BASE.rglob("*.ftl")):
        rel_path = ftl_file.relative_to(LOCALE_BASE)
        if process_ftl_file(ftl_file):
            fixed_count += 1
            print(f"Fixed {rel_path}")
    
    print(f"\nTotal: {fixed_count} files improved")

if __name__ == "__main__":
    main()
