#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления переводов в папках ammoloader и clothing.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Пути
LOCALE_DIR = Path(r"G:\Monolith_Forge\Resources\Locale\ru-RU\ss14-ru\prototypes\_Mono\entities")
PROTOTYPES_DIR = Path(r"G:\Monolith_Forge\Resources\Prototypes\_Mono\Entities")

# Целевые папки
TARGET_FOLDERS = ['ammoloader', 'clothing']

# Словарь переводов
TRANSLATIONS = {
    # AmmoLoader
    "ammo loader": "загрузчик боеприпасов",
    "small ammo loader": "малый загрузчик боеприпасов",
    "A pneumatic ammunition loading system manufactured by Erebus HI. Link it to ship artillery with a multitool to transfer ammunition. This model supports 8 guns.": 
        "Пневматическая система загрузки боеприпасов производства Erebus HI. Подключите её к корабельной артиллерии мультитулом для передачи боеприпасов. Эта модель поддерживает 8 орудий.",
    "A pneumatic ammunition loading system manufactured by Erebus HI. Link it to ship artillery with a multitool to transfer ammunition. This model supports only 2 guns, but is more durable.": 
        "Пневматическая система загрузки боеприпасов производства Erebus HI. Подключите её к корабельной артиллерии мультитулом для передачи боеприпасов. Эта модель поддерживает только 2 орудия, но более прочная.",
    
    # Clothing - общие фразы
    "An experimental exosuit designed for the future of warfare. Despite not having any head covering, the utilization of new nanomachine technology allows it to protect the wearer from the pressure and cold of space.":
        "Экспериментальный экзокостюм, разработанный для будущего войны. Несмотря на отсутствие защиты головы, использование новой технологии наномашин позволяет защитить носителя от давления и холода космоса.",
    "A lightweight protective plate made from advanced durathread fibers. Initially manufactured by Aether, but the process has long been reverse-engineered.":
        "Лёгкая защитная пластина из продвинутых волокон дураткани. Изначально производилась Aether, но процесс давно был обратно спроектирован.",
    "A medium-weight ceramic composite plate manufactured with a material process proprietary to Aether.":
        "Средняя керамическая композитная пластина, изготовленная по запатентованному процессу Aether.",
    "A heavy-duty plasteel plate manufactured by a layered cold-stamping process proprietary to Aether.":
        "Тяжёлая пластиновая пластина из пластали, изготовленная по запатентованному процессу многослойной холодной штамповки Aether.",
    "An advanced plastitanium composite plate manufactured by Aether.":
        "Продвинутая композитная пластина из пластитания производства Aether.",
    
    # Combat uniforms
    "A combat uniform in TSF Type-45U urban camouflage. Its outfitted with a blue TSF flag armband.":
        "Боевая форма в городском камуфляже TSF Type-45U. Оснащена синей нарукавной повязкой с флагом TSF.",
    "A combat uniform in TSF Type-47D desert camouflage. Its outfitted with a blue TSF flag armband.":
        "Боевая форма в пустынном камуфляже TSF Type-47D. Оснащена синей нарукавной повязкой с флагом TSF.",
    "A heavy protective suit. It'll slow you down a bit, but it'll make sure nothing you don't want gets in your body. Be the bane of all Chimeras.":
        "Тяжёлый защитный костюм. Немного замедлит вас, но гарантирует, что ничего нежелательного не попадёт в ваше тело. Будьте проклятием всех Химер.",
    "A heavily modified protective suit. It'll slow you down a bit, but it'll make sure nothing you don't want gets in your body. Also comes with the bonus of flame resistance! Be the bane of all borers!":
        "Сильно модифицированный защитный костюм. Немного замедлит вас, но гарантирует, что ничего нежелательного не попадёт в ваше тело. Также имеет бонус огнестойкости! Будьте проклятием всех бурильщиков!",
    "A combat uniform in TSF Type-45U urban camouflage. It has high-vis markings for engineers.":
        "Боевая форма в городском камуфляже TSF Type-45U. Имеет яркие маркировки для инженеров.",
    "A military dress uniform for special occasions, complete with stripes and rank insignia.":
        "Военная парадная форма для особых случаев, с нашивками и знаками различия.",
    "Standard fatigues of the USSP military.":
        "Стандартная полевая форма военных USSP.",
    "A matte black tactical outfit worn by independent agents working on contracts. The red armband marks affiliation—loose as it may be.":
        "Матово-чёрный тактический костюм, носимый независимыми агентами, работающими по контрактам. Красная нарукавная повязка отмечает принадлежность — сколь бы свободной она ни была.",
    "A matte black tactical outfit worn by independent agents working on contracts. The red ar- wait it's just the pants?":
        "Матово-чёрный тактический костюм, носимый независимыми агентами, работающими по контрактам. Красная нарукавная повязка... стоп, это просто штаны?",
    "A matte black shirt paired with jeans. Worn by independent agents who prefer fieldwork with a bit more flexibility. The red armband still signals uncertain allegiance.":
        "Матово-чёрная рубашка в паре с джинсами. Носится независимыми агентами, предпочитающими полевую работу с большей гибкостью. Красная нарукавная повязка всё ещё сигнализирует о неопределённой принадлежности.",
    "A matte black tactical top combined with durable brown cargo pants, suited for terrain-heavy contracts. Independent agents favor this blend of function and subtle defiance. The red armband stays—barely.":
        "Матово-чёрная тактическая верхняя часть в сочетании с прочными коричневыми штанами карго, подходящими для контрактов на сложной местности. Независимые агенты предпочитают это сочетание функциональности и тонкого неповиновения. Красная нарукавная повязка остаётся — едва ли.",
    "A heavily insulated variant of the rogue field suit, lined for extreme environments. Built for survival without compromise.":
        "Сильно утеплённый вариант полевого костюма разбойника, подбитый для экстремальных условий. Построен для выживания без компромиссов.",
    "Standard fatigues of the Armed Trauma Unit.":
        "Стандартная полевая форма Вооружённого отряда травматологии.",
    "Durable overalls with zippers here and there. It bears the colors of Drake Industries.":
        "Прочные комбинезоны с молниями тут и там. Имеет цвета Drake Industries.",
    "This one has pocket for your smokes. Oh wait, no, it's a false pocket. Well, at least it's fashionable. It bears the colors of Drake Industries.":
        "У этого есть карман для ваших сигарет. О, подождите, нет, это фальшивый карман. Ну, по крайней мере, это модно. Имеет цвета Drake Industries.",
    "A sleek tracksuit designed to have decent camouflage in dark spaces. It bears the colors of Drake Industries.":
        "Стильный спортивный костюм, разработанный для хорошей маскировки в тёмных пространствах. Имеет цвета Drake Industries.",
    "Woodland CCE camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Лесной боевой костюм в камуфляже CCE. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Woodland CCE camouflaged combat suit. Camo in space... This one has been used quite a lot and has darkenned over time.":
        "Лесной боевой костюм в камуфляже CCE. Камуфляж в космосе... Этот был довольно много использован и потемнел со временем.",
    "Woodland CCE camouflaged combat suit. Camo in space... This one has been bleached for some reasons.":
        "Лесной боевой костюм в камуфляже CCE. Камуфляж в космосе... Этот был отбелен по каким-то причинам.",
    "Desert CCE camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Пустынный боевой костюм в камуфляже CCE. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Grassland camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в степном камуфляже. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Mudland camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в болотном камуфляже. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Misko camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже Misko. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Lampart camouflaged combat suit with some odd flag stitched to it. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже Lampart с какой-то странной нашивкой флага. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Lampart camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже Lampart. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Summer flora camouflaged combat suit with some odd flag stitched to it. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже летней флоры с какой-то странной нашивкой флага. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Summer flora camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже летней флоры. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Misko camouflaged combat suit. Camo in space... This one has been lightly used and retain its original camo.":
        "Боевой костюм в камуфляже Misko. Камуфляж в космосе... Этот был слегка использован и сохранил свой оригинальный камуфляж.",
    "Digital camouflaged combat suit. Camo in space...":
        "Боевой костюм в цифровом камуфляже. Камуфляж в космосе...",
    
    # Названия
    "TSFMC type-45U combat uniform": "боевая форма TSFMC type-45U",
    "TSFMC type-47D combat uniform": "боевая форма TSFMC type-47D",
    "TSFMC type-49C MOPP suit": "защитный костюм TSFMC type-49C MOPP",
    "CBURN Type B Protective Suit": "защитный костюм CBURN Type B",
    "TSFMC engineer uniform": "инженерная форма TSFMC",
    "TSFMC dress uniform": "парадная форма TSFMC",
    "USSP uniform": "форма USSP",
    "rogue field suit": "полевой костюм разбойника",
    "rogue field pants": "полевые штаны разбойника",
    "rogue field suit (jeans)": "полевой костюм разбойника (джинсы)",
    "rogue field suit (cargos)": "полевой костюм разбойника (карго)",
    "rogue warm field suit": "утеплённый полевой костюм разбойника",
    "armed trauma unit jumpsuit": "комбинезон вооружённого отряда травматологии",
    "hauler jumpsuit": "комбинезон грузчика",
    "Military": "военная форма",
    "CCE combat uniform (basic)": "боевая форма CCE (базовая)",
    "CCE combat uniform (worn)": "боевая форма CCE (изношенная)",
    "CCE combat uniform (bleached)": "боевая форма CCE (отбелённая)",
    "CCE combat uniform (desert)": "боевая форма CCE (пустынная)",
    "Grassland combat uniform": "боевая форма степная",
    "Mudland combat uniform": "боевая форма болотная",
    "Misko combat uniform": "боевая форма Misko",
    "Lampart combat uniform": "боевая форма Lampart",
    "Summer flora combat uniform": "боевая форма летняя флора",
    "white urban combat uniform": "белая городская боевая форма",
    "black digital combat uniform": "чёрная цифровая боевая форма",
    "blue digital combat uniform": "синяя цифровая боевая форма",
    "red digital combat uniform": "красная цифровая боевая форма",
    "green and tan digital combat uniform": "зелёно-коричневая цифровая боевая форма",
    
    # Armor plates
    "durathread plate": "пластина из дураткани",
    "ceramic plate": "керамическая пластина",
    "plasteel plate": "пластина из пластали",
    "plastitanium plate": "пластина из пластитания",
    "Light": "лёгкая",
    "Medium": "средняя",
    "Tactical": "тактическая",
    "Admeme": "пластитаниевая",
    "SelfUnremovable": "экзокостюм Аврора",
}

# Кэш для хранения всех сущностей из YAML файлов
entities_cache = {}

def extract_entities_from_yml(yml_path):
    """Извлекает данные всех сущностей из YAML файла"""
    entities = []
    try:
        with open(yml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Разбиваем на блоки сущностей
        entity_blocks = re.split(r'(?=^- type: entity)', content, flags=re.MULTILINE)
        
        for block in entity_blocks:
            if not block.strip():
                continue
            
            # Ищем id, name, description, suffix, parent
            id_match = re.search(r'^\s*id:\s*(\S+)', block, re.MULTILINE)
            name_match = re.search(r'^\s*name:\s*(.+)', block, re.MULTILINE)
            desc_match = re.search(r'^\s*description:\s*(.+)', block, re.MULTILINE)
            suffix_match = re.search(r'^\s*suffix:\s*(.+)', block, re.MULTILINE)
            parent_match = re.search(r'^\s*parent:\s*(.+)', block, re.MULTILINE)
            
            entity_id = id_match.group(1) if id_match else None
            name = name_match.group(1).strip() if name_match else None
            description = desc_match.group(1).strip() if desc_match else None
            suffix = suffix_match.group(1).strip() if suffix_match else None
            parent = parent_match.group(1).strip() if parent_match else None
            
            # Обрабатываем parent (может быть список)
            parent_list = []
            if parent:
                parent = parent.strip()
                if parent.startswith('['):
                    parent = parent[1:-1].strip()
                    parent_list = [p.strip() for p in parent.split(',')]
                else:
                    parent_list = [parent]
            
            # Убираем кавычки если есть
            for field_name, field_value in [('name', name), ('description', description), ('suffix', suffix)]:
                if field_value and field_value.startswith('"') and field_value.endswith('"'):
                    if field_name == 'name':
                        name = field_value[1:-1]
                    elif field_name == 'description':
                        description = field_value[1:-1]
                    elif field_name == 'suffix':
                        suffix = field_value[1:-1]
            
            if entity_id:
                entities.append({
                    'id': entity_id,
                    'name': name,
                    'description': description,
                    'suffix': suffix,
                    'parent': parent_list[0] if parent_list else None,
                    'parents': parent_list
                })
        
        return entities
    except Exception as e:
        print(f"  Ошибка при чтении {yml_path}: {e}")
        return []

def build_entities_cache():
    """Строит кэш всех сущностей из YAML файлов"""
    print("Построение кэша сущностей из YAML файлов...")
    count = 0
    for yml_file in PROTOTYPES_DIR.rglob('*.yml'):
        entities = extract_entities_from_yml(yml_file)
        for entity in entities:
            entities_cache[entity['id']] = entity
            count += 1
    print(f"Загружено {count} сущностей в кэш")

def translate_text(text, translations_dict):
    """Переводит текст используя словарь"""
    if not text:
        return text
    
    translated = text
    # Применяем переводы в порядке длины (сначала длинные фразы)
    for eng, rus in sorted(translations_dict.items(), key=lambda x: -len(x[0])):
        translated = translated.replace(eng, rus)
    
    return translated

def fix_ftl_file(ftl_path):
    """Исправляет FTL файл на основе данных из кэша и словаря переводов"""
    # Пробуем разные кодировки для чтения
    lines = None
    for encoding in ['utf-8', 'cp1251', 'latin1']:
        try:
            with open(ftl_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if lines is None:
        print(f"  Ошибка: не удалось прочитать файл")
        return False, False
    
    has_english = False
    fixed_lines = []
    seen_keys = set()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line
        
        # Проверяем на английский текст
        if line.strip() and not line.strip().startswith('#'):
            # Проверяем строку с ключом
            if line.strip().startswith('ent-'):
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    entity_key = key_match.group(1)
                    entity_id = entity_key.replace('ent-', '')
                    value = key_match.group(2).strip()
                    
                    # Проверяем, есть ли английский текст
                    if re.search(r'[a-zA-Z]', value) and not re.search(r'[а-яА-Я]', value):
                        has_english = True
                        # Пытаемся найти в кэше
                        if entity_id in entities_cache:
                            entity = entities_cache[entity_id]
                            name_source = entity.get('suffix') or entity.get('name') or ''
                            if name_source:
                                name_translated = translate_text(name_source, TRANSLATIONS)
                                line = f"{entity_key} = {name_translated}\n"
                        else:
                            # Пробуем перевести напрямую
                            line = f"{entity_key} = {translate_text(value, TRANSLATIONS)}\n"
            
            # Проверяем строку с описанием
            elif line.strip().startswith('.desc'):
                desc_match = re.match(r'^\s*\.desc\s*=\s*(.+)', line)
                if desc_match:
                    desc_value = desc_match.group(1).strip()
                    # Проверяем, есть ли английский текст
                    if re.search(r'[a-zA-Z]', desc_value) and not re.search(r'[а-яА-Я]', desc_value):
                        has_english = True
                        # Пытаемся найти в кэше (используем предыдущую строку)
                        if i > 0:
                            prev_key_match = re.match(r'^(\S+)\s*=', lines[i-1])
                            if prev_key_match:
                                entity_key = prev_key_match.group(1)
                                entity_id = entity_key.replace('ent-', '')
                                if entity_id in entities_cache:
                                    entity = entities_cache[entity_id]
                                    if entity.get('description'):
                                        desc_translated = translate_text(entity['description'], TRANSLATIONS)
                                        line = f"    .desc = {desc_translated}\n"
                                else:
                                    # Пробуем перевести напрямую
                                    line = f"    .desc = {translate_text(desc_value, TRANSLATIONS)}\n"
        
        # Убираем дубликаты ключей
        if line.strip() and not line.strip().startswith('#'):
            key_match = re.match(r'^(\S+)\s*=', line)
            if key_match:
                key = key_match.group(1)
                if key in seen_keys:
                    i += 1
                    continue
                seen_keys.add(key)
        
        fixed_lines.append(line)
        i += 1
    
    # Записываем исправленный файл только если были изменения
    if has_english:
        try:
            with open(ftl_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True, has_english
        except Exception as e:
            print(f"  Ошибка при записи: {e}")
            return False, False
    
    return False, False

def main():
    """Основная функция"""
    print("Исправление переводов в папках ammoloader и clothing...")
    print(f"Папка локализации: {LOCALE_DIR}")
    print(f"Папка прототипов: {PROTOTYPES_DIR}")
    print()
    
    if not LOCALE_DIR.exists():
        print(f"Ошибка: папка {LOCALE_DIR} не найдена!")
        return
    
    if not PROTOTYPES_DIR.exists():
        print(f"Ошибка: папка {PROTOTYPES_DIR} не найдена!")
        return
    
    # Строим кэш сущностей
    build_entities_cache()
    print()
    
    fixed_count = 0
    english_count = 0
    
    # Проходим по целевым папкам
    for folder in TARGET_FOLDERS:
        folder_path = LOCALE_DIR / folder
        if not folder_path.exists():
            print(f"Папка {folder} не найдена, пропускаем")
            continue
        
        print(f"Обработка папки: {folder}")
        
        # Проходим по всем FTL файлам в папке
        for ftl_file in folder_path.rglob('*.ftl'):
            rel_path = ftl_file.relative_to(LOCALE_DIR)
            print(f"  Проверка: {rel_path}")
            
            fixed, has_english = fix_ftl_file(ftl_file)
            
            if fixed:
                fixed_count += 1
                if has_english:
                    english_count += 1
                    print(f"    [OK] Исправлен английский текст")
            else:
                print(f"    [OK]")
    
    print()
    print(f"Готово!")
    print(f"Исправлено файлов: {fixed_count}")
    print(f"  - с английским текстом: {english_count}")

if __name__ == "__main__":
    main()
