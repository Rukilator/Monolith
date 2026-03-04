#!/usr/bin/env py -3
"""Fix translations in alerts, Body, and catalogs folders."""
import os
import re
from pathlib import Path

LOCALE_BASE = Path("g:/Monolith_Forge/Resources/Locale/ru-RU/ss14-ru/prototypes/_Mono")
PROTOS_BASE = Path("g:/Monolith_Forge/Resources/Prototypes/_Mono")

# Translation dictionaries
TRANSLATIONS = {
    # Body parts
    "protogen body part": "часть тела протогена",
    "protogen torso": "торс протогена",
    "protogen head": "голова протогена",
    "left protogen arm": "левая рука протогена",
    "right protogen arm": "правая рука протогена",
    "left protogen hand": "левая кисть протогена",
    "right protogen hand": "правая кисть протогена",
    "left Protogen leg": "левая нога протогена",
    "right protogen leg": "правая нога протогена",
    "left protogen foot": "левая стопа протогена",
    "right protogen foot": "правая стопа протогена",
    "asakim body part": "часть тела асакима",
    "asakim torso": "торс асакима",
    "asakim head": "голова асакима",
    "left asakim arm": "левая рука асакима",
    "right asakim arm": "правая рука асакима",
    "left asakim hand": "левая кисть асакима",
    "right asakim hand": "правая кисть асакима",
    "left asakim leg": "левая нога асакима",
    "right asakim leg": "правая нога асакима",
    "left asakim foot": "левая стопа асакима",
    "right asakim foot": "правая стопа асакима",
    "chimera endoskeleton body part": "часть тела эндоскелета химеры",
    "chimera endoskeleton torso": "торс эндоскелета химеры",
    "chimera endoskeleton skull": "череп эндоскелета химеры",
    "left chimera endoskeleton arm": "левая рука эндоскелета химеры",
    "right chimera endoskeleton arm": "правая рука эндоскелета химеры",
    "left chimera endoskeleton hand": "левая кисть эндоскелета химеры",
    "right chimera endoskeleton hand": "правая кисть эндоскелета химеры",
    "left chimera endoskeleton leg": "левая нога эндоскелета химеры",
    "right chimera endoskeleton leg": "правая нога эндоскелета химеры",
    "left chimera endoskeleton foot": "левая стопа эндоскелета химеры",
    "right chimera endoskeleton foot": "правая стопа эндоскелета химеры",
    
    # Organs
    "brain": "мозг",
    "eyes": "глаза",
    "tongue": "язык",
    "appendix": "аппендикс",
    "ears": "уши",
    "lungs": "легкие",
    "heart": "сердце",
    "stomach": "желудок",
    "liver": "печень",
    "kidneys": "почки",
    "hydrakin organ": "орган гидракина",
    "hydrakin stomach": "желудок гидракина",
    "hydrakin brain": "мозг гидракина",
    "hydrakin liver": "печень гидракина",
    "hydrakin heart": "сердце гидракина",
    "hydrakin lungs": "легкие гидракина",
    "chimera organ": "орган химеры",
    "chimera stomach": "желудок химеры",
    "chimera brain": "мозг химеры",
    "chimera spike gland": "железа шипов химеры",
    "chimera heart": "сердце химеры",
    "chimera pheropod": "феропод химеры",
    
    # Descriptions
    "The source of incredible, unending intelligence. 01001000 01101111 01101110 01101011 00101110": "Источник невероятного, бесконечного интеллекта. 01001000 01101111 01101110 01101011 00101110",
    "Emits LED lights to resemble eyes.": "Излучает светодиодный свет, чтобы напоминать глаза.",
    "A fleshy muscle located within a Protogen's mouth, wherever that is.": "Мясистая мышца, расположенная во рту протогена, где бы он ни находился.",
    "Lets a Protogen process audio. And listen to their favorite techno hits.": "Позволяет протогену обрабатывать аудио. И слушать свои любимые техно-хиты.",
    "Filters oxygen from an atmosphere, which is then sent into the bloodstream to be used as an electron carrier. God knows how a Protogen breathes at all.": "Фильтрует кислород из атмосферы, который затем отправляется в кровоток для использования в качестве переносчика электронов. Бог знает, как протоген вообще дышит.",
    "Even the most stone-cold, technology-based heart was alive once.": "Даже самое холодное, технологическое сердце когда-то было живым.",
    "Gross. This is hard to stomach.": "Отвратительно. Это трудно переварить.",
    "Pairing suggestion: fermented RAM sticks and CPU drives.": "Предложение по сочетанию: ферментированные планки RAM и диски CPU.",
    "Filters toxins and computer viruses from the bloodstream.": "Фильтрует токсины и компьютерные вирусы из кровотока.",
    "Hydrakin lungs, capable of processing any gas without negative effects.": "Легкие гидракина, способные обрабатывать любой газ без негативных эффектов.",
    "A strange organ that serves as the center for the metabolism of a Chimera.": "Странный орган, служащий центром метаболизма химеры.",
    "The heart of a chimera growth.": "Сердце роста химеры.",
    "Takes the location of the liver in the body, and repurposes them to be used as a gland for growing bone spikes instead.": "Занимает место печени в теле и перепрофилирует их для использования в качестве железы для выращивания костных шипов.",
    "Distributes pheromones allowing for hivemind communication with other Chimeras. Serves as the lungs for the parasite as well.": "Распределяет феромоны, позволяя общаться через коллективный разум с другими химерами. Также служит легкими для паразита.",
    "Alas poor Yorick...": "Увы, бедный Йорик...",
    
    # Catalogs
    "How 2 Make Tea 4 Dorks": "Как заварить чай для чайников",
    "A quick guide to tea preparation.": "Краткое руководство по приготовлению чая.",
    "BaristaVend Restock Crate": "Ящик пополнения BaristaVend",
    "Contains a restock box for the BaristaVend.": "Содержит коробку пополнения для BaristaVend.",
}

def translate_text(text):
    """Translate English text to Russian."""
    if not text:
        return text
    
    # Apply direct translations
    for eng, rus in TRANSLATIONS.items():
        if text == eng:
            return rus
    
    # If no direct match, return original
    return text

def fix_ftl_file(ftl_path, proto_path=None):
    """Fix a single FTL file."""
    if not ftl_path.exists():
        return False
    
    try:
        with open(ftl_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  Error reading {ftl_path}: {e}")
        return False
    
    # Check if file has English text
    has_english = False
    lines = content.split('\n')
    fixed_lines = []
    seen_keys = set()
    
    for line in lines:
        # Skip comments and empty lines
        if not line.strip() or line.strip().startswith('#'):
            fixed_lines.append(line)
            continue
        
        # Match FTL entries
        name_match = re.match(r'^(ent-\w+)\s*=\s*(.+)$', line)
        desc_match = re.match(r'^(\s+\.desc\s*=\s*)(.+)$', line)
        
        if name_match:
            key, value = name_match.groups()
            # Skip duplicates
            if key in seen_keys:
                continue
            seen_keys.add(key)
            
            # Check if English
            if any(word in value.lower() for word in ['protogen', 'asakim', 'chimera', 'hydrakin', 'body part', 'torso', 'head', 'arm', 'hand', 'leg', 'foot', 'brain', 'eyes', 'tongue', 'appendix', 'ears', 'lungs', 'heart', 'stomach', 'liver', 'kidneys', 'organ', 'endoskeleton', 'skull', 'pheropod', 'spike gland', 'how 2', 'baristavend', 'restock', 'crate', 'contains']):
                has_english = True
                translated = translate_text(value)
                fixed_lines.append(f"{key} = {translated}")
            else:
                fixed_lines.append(line)
                
        elif desc_match:
            prefix, value = desc_match.groups()
            translated = translate_text(value)
            if translated != value:
                has_english = True
            fixed_lines.append(f"{prefix}{translated}")
        else:
            fixed_lines.append(line)
    
    # Remove duplicates at the end
    final_lines = []
    seen_keys_final = set()
    for line in fixed_lines:
        name_match = re.match(r'^(ent-\w+)\s*=', line)
        if name_match:
            key = name_match.group(1)
            if key in seen_keys_final:
                continue
            seen_keys_final.add(key)
        final_lines.append(line)
    
    new_content = "\n".join(final_lines)
    
    if new_content != content or has_english:
        try:
            with open(ftl_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        except Exception as e:
            print(f"  Error writing {ftl_path}: {e}")
            return False
    
    return False

def main():
    print("Fixing translations in alerts, Body, and catalogs...")
    
    folders = [
        "alerts",
        "Body",
        "catalogs"
    ]
    
    fixed_count = 0
    
    for folder in folders:
        folder_path = LOCALE_BASE / folder
        if not folder_path.exists():
            print(f"Folder {folder} does not exist, skipping...")
            continue
        
        print(f"\nProcessing {folder}...")
        for ftl_file in sorted(folder_path.rglob("*.ftl")):
            rel_path = ftl_file.relative_to(LOCALE_BASE)
            if fix_ftl_file(ftl_file):
                fixed_count += 1
                print(f"Fixed {rel_path}")
    
    print(f"\nTotal: {fixed_count} files fixed")

if __name__ == "__main__":
    main()
