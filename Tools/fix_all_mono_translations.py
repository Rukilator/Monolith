#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный скрипт для исправления всех переводов в папке _Mono.
Исправляет Mojibake, переводит английский текст, использует кэш YAML файлов.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Пути
LOCALE_DIR = Path(r"G:\Monolith_Forge\Resources\Locale\ru-RU\ss14-ru\prototypes\_Mono")
PROTOTYPES_DIR = Path(r"G:\Monolith_Forge\Resources\Prototypes\_Mono")

# Расширенный словарь переводов
TRANSLATIONS = {
    # Shipyard
    "A truck stop diner ship designed to resemble a semi-truck, complete with a EVA accessable dining room and a small cargo bay.":
        "Корабль-закусочная на трассе, разработанный наподобие полуприцепа, с доступной из EVA столовой и небольшим грузовым отсеком.",
    "A extremely compact medical ship that packs a punch.":
        "Крайне компактный медицинский корабль, который наносит удар.",
    "An armored light transport fitted with minimal medical equipment. Cramped, but nimble and tough like a dog.":
        "Бронированный лёгкий транспорт с минимальным медицинским оборудованием. Тесный, но проворный и крепкий, как пёс.",
    
    # Общие фразы
    "Can be remotely activated": "Может быть активирована дистанционно",
    "or linked up to a GCS": "или подключена к GCS",
    "or linked to a GCS": "или подключена к GCS",
    "Can be remotely activated or linked to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "Can be remotely activated, or linked up to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading.": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки.",
    
    # Entities - общие термины
    "spawner": "спаунер",
    "random poster": "случайный постер",
    "random painting": "случайная картина",
    "NT T1 clothing": "одежда NT T1",
    "servicing borg": "обслуживающий борг",
    "AOS": "АОС",
    "fire group commander": "командир огневой группы",
    "MARSOF": "МАРСОФ",
    "Asakim warrior": "воин асаким",
    "Urist McHarddrive": "Урист МакХарддрайв",
    "Urist McAsakim": "Урист МакАсаким",
    "factional cyborg chassis": "фракционное шасси киборга",
    "AI module Monolith": "модуль ИИ Монолит",
    "base cyborg chassis": "базовое шасси киборга",
    "[REDACTED]": "[ЗАСЕКРЕЧЕНО]",
    "AI module": "модуль ИИ",
    "TSFMC AI module": "модуль ИИ ВСКМП",
    "PDV AI module": "модуль ИИ ФДА",
    "PDV base cyborg chassis": "базовое шасси киборга ФДА",
    "TSFMC base cyborg chassis": "базовое шасси киборга ВСКМП",
    "security AI module": "модуль ИИ охраны",
    "base monolithic entity spawner": "спаунер базовой монолитной сущности",
    "base docile ore crab": "базовый смирный рудный краб",
    "docile quartz crab": "смирный кварцевый краб",
    "docile iron crab": "смирный железный краб",
    "docile uranium crab": "смирный урановый краб",
    "docile silver crab": "смирный серебряный краб",
    "docile bananium crab": "смирный бананиумовый краб",
    "docile coal crab": "смирный угольный краб",
    "docile gold crab": "смирный золотой краб",
    "docile plasma crab": "смирный плазменный краб",
    "docile salt crab": "смирный солевой краб",
    "kangaroo": "кенгуру",
    "Large marsupial herbivore. Powerful hind legs with claw-like toes.":
        "Крупное сумчатое травоядное. Мощные задние ноги с когтеподобными пальцами.",
    "ramming core": "таранное ядро",
    "Whatever you're looking at this, it probably means it's not safe.":
        "То, на что вы смотрите, наверняка означает, что это небезопасно.",
    "bone spike letoferol": "костяной шип летоферола",
    "Shoots a short burst of bone spikes.":
        "Стреляет короткой очередью костяных шипов.",
    "chimera meat product": "мясной продукт химеры",
    "Horribly mutating something.":
        "Ужасно мутирующее нечто.",
    "chimera meat product horror": "мясной продукт химеры ужас",
    "paper bucket": "бумажное ведёрко",
    "Single-use paper insert for buckets with cooked food.":
        "Одноразовая бумажная вкладка для вёдер с приготовленной едой.",
    "Simple dry biscuit, ideal pair to tea or coffee.":
        "Простой сухой бисквит, идеальная пара к чаю или кофе.",
    "macaroni with cheese": "макароны с сыром",
    "Cheesy!": "Сырные!",
    "MRE baton": "батончик ИРП",
    "Garnish to your MRE.":
        "Гарнир к вашему ИРП.",
    "ice cream jug": "кувшин мороженого",
    "A jug full of sweet homemade ice cream.":
        "Кувшин, полный сладкого домашнего мороженого.",
    "scrap processor drum": "барабан утилизатора лома",
    "roll trunk": "барабан",
    "processor": "утилизатор",
    "scrap": "лом",
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

def get_parent_name(entity_id):
    """Получает имя родительской сущности"""
    if entity_id not in entities_cache:
        return None
    
    entity = entities_cache[entity_id]
    if entity.get('name'):
        return entity['name']
    
    if entity.get('parent'):
        return get_parent_name(entity['parent'])
    
    return None

def translate_text(text, translations_dict):
    """Переводит текст используя словарь"""
    if not text:
        return text
    
    translated = text
    # Применяем переводы в порядке длины (сначала длинные фразы)
    for eng, rus in sorted(translations_dict.items(), key=lambda x: -len(x[0])):
        translated = translated.replace(eng, rus)
    
    return translated

def detect_mojibake(text):
    """Определяет, содержит ли текст Mojibake"""
    mojibake_pattern = re.compile(r'[РЎРўРЈР¤РҐР¦Р§РЁРЄРЅР®РЇ][Р°Р±РІРіРґРµРёР№РєР»РјРЅРѕРїСЂСЃС‚СѓС„С…С†С‡С€С‰СЉС‹СЊСЌСЋСЏ]')
    return bool(mojibake_pattern.search(text))


def fix_mojibake_decode(text):
    """
    Исправляет классический Mojibake: UTF-8 был прочитан как CP1251 (или CP1252).
    Возвращает исправленный текст или None при ошибке.
    """
    # Символы, которых нет в CP1251 — заменяем на близкие, чтобы encode не падал
    replace_map = {'\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"', '\u00ab': '"', '\u00bb': '"'}
    for enc in ('cp1251', 'cp1252'):
        try:
            t = text
            for u, r in replace_map.items():
                t = t.replace(u, r)
            fixed = t.encode(enc).decode('utf-8')
            if '\ufffd' in fixed or (fixed and not re.search(r'[а-яА-ЯёЁ]', fixed)):
                continue
            return fixed
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    return None

def has_english_text(text):
    """Проверяет, содержит ли текст английские слова (кроме имен собственных)"""
    if not text:
        return False
    
    # Исключаем строки с только ссылками на другие ключи FTL
    if re.match(r'^\s*\{', text) or re.match(r'^\s*\.(desc|suffix|name)\s*=\s*\{', text):
        return False
    
    # Проверяем наличие кириллицы
    has_cyrillic = bool(re.search(r'[а-яА-Я]', text))
    
    # Если есть кириллица, но также есть английские слова - это смешанный текст
    if has_cyrillic:
        # Ищем английские слова (минимум 3 буквы)
        english_word_pattern = re.compile(r'\b([a-zA-Z]{3,})\b')
        matches = english_word_pattern.findall(text)
        excluded = {'USSP', 'TSF', 'TSFMC', 'UNSA', 'CCE', 'MOPP', 'CBURN', 'PDV', 'SCAF', 'EVA', 'U.I.', 'UI', 'MKI', 'MKII', 'MKIII', 'FMJ', 'AP', 'HE', 'EMP', 'HP', 'RIP', 'SAM', 'ACP', 'GCS', 'ADS', 'GPOL', 'LOSAT', 'ECM', 'ASM', 'ADMP', 'TPC', 'ADEX', 'NVG', 'HUD', 'Drake', 'Industries', 'Aether', 'Erebus', 'HI', 'Viper', 'Group', 'JACKAL', 'IMP', 'Voenkom', 'Felix', 'Ullman', 'Misko', 'Lampart', 'M86', 'M82', 'L-27', 'L-10', 'L-10-A', 'M-10', 'L-30', 'UF-16', 'VK-1', 'T-23', 'T-53', 'WL-01', 'CV-32', 'CV-53', 'CV-67', 'M-320X', 'AURORA', 'mk.II', 'mk.III', 'Type', 'B', 'MOPP', 'mk', 'II', 'III', 'OUTP', 'CA', 'diagonal', 'NT', 'T1', 'AOS', 'MARSOF', 'Asakim', 'McHarddrive', 'McAsakim', 'REDACTED', 'MRE', 'EVA'}
        for match in matches:
            if match not in excluded and match.lower() not in [w.lower() for w in excluded]:
                return True
        return False
    
    # Если нет кириллицы, проверяем наличие английских слов
    english_word_pattern = re.compile(r'\b([a-zA-Z]{2,})\b')
    matches = english_word_pattern.findall(text)
    if not matches:
        return False
    
    # Исключаем известные аббревиатуры и короткие слова
    excluded = {'USSP', 'TSF', 'TSFMC', 'UNSA', 'CCE', 'MOPP', 'CBURN', 'PDV', 'SCAF', 'EVA', 'U.I.', 'UI', 'MKI', 'MKII', 'MKIII', 'FMJ', 'AP', 'HE', 'EMP', 'HP', 'RIP', 'SAM', 'ACP', 'GCS', 'ADS', 'GPOL', 'LOSAT', 'ECM', 'ASM', 'ADMP', 'TPC', 'ADEX', 'NVG', 'HUD', 'Drake', 'Industries', 'Aether', 'Erebus', 'HI', 'Viper', 'Group', 'JACKAL', 'IMP', 'Voenkom', 'Felix', 'Ullman', 'Misko', 'Lampart', 'M86', 'M82', 'L-27', 'L-10', 'L-10-A', 'M-10', 'L-30', 'UF-16', 'VK-1', 'T-23', 'T-53', 'WL-01', 'CV-32', 'CV-53', 'CV-67', 'M-320X', 'AURORA', 'mk.II', 'mk.III', 'Type', 'B', 'MOPP', 'mk', 'II', 'III', 'OUTP', 'CA', 'diagonal', 'NT', 'T1', 'AOS', 'MARSOF', 'Asakim', 'McHarddrive', 'McAsakim', 'REDACTED', 'MRE', 'EVA', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should', 'may', 'might', 'must', 'shall'}
    
    # Проверяем, есть ли слова, которые не являются исключениями
    for match in matches:
        if match.lower() not in [w.lower() for w in excluded]:
            # Проверяем, не является ли это частью известной фразы из словаря переводов
            found_in_dict = False
            for key in TRANSLATIONS.keys():
                if match.lower() in key.lower() and len(key) > len(match):
                    found_in_dict = True
                    break
            if not found_in_dict:
                return True
    
    return False

def fix_ftl_file(ftl_path):
    """Исправляет FTL файл на основе данных из кэша"""
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
        return False, False, False
    
    has_mojibake = False
    has_english = False
    fixed_lines = []
    seen_keys = set()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        original_line = line
        line_modified = False
        
        # Проверяем на Mojibake
        if detect_mojibake(line):
            has_mojibake = True
            line_modified = True
            
            # Сначала пробуем исправить Mojibake перекодировкой (UTF-8 прочитан как CP1252)
            if re.match(r'^\s*\.desc\s*=', line):
                desc_m = re.match(r'^(\s*\.desc)\s*=\s*(.+)', line)
                if desc_m:
                    value = desc_m.group(2).strip()
                    decoded = fix_mojibake_decode(value)
                    if decoded is not None:
                        line = f"{desc_m.group(1)} = {decoded}\n"
            else:
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    prefix = key_match.group(1)
                    value = key_match.group(2).strip()
                    decoded = fix_mojibake_decode(value)
                    if decoded is not None:
                        line = f"{prefix} = {decoded}\n"
            
            if line.strip().startswith('ent-') and detect_mojibake(line):
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    entity_key = key_match.group(1)
                    entity_id = entity_key.replace('ent-', '')
                    
                    if entity_id in entities_cache:
                        entity = entities_cache[entity_id]
                        name_source = entity.get('suffix') or entity.get('name') or ''
                        
                        if not name_source and entity.get('parent'):
                            parent_name = get_parent_name(entity['parent'])
                            if parent_name:
                                suffix = entity.get('suffix') or ''
                                if suffix:
                                    name_source = f"{parent_name} {suffix}"
                                else:
                                    name_source = parent_name
                        
                        if name_source:
                            name_translated = translate_text(name_source, TRANSLATIONS)
                            line = f"{entity_key} = {name_translated}\n"
                    
                    if not line_modified or detect_mojibake(line):
                        value = key_match.group(2).strip()
                        decoded = fix_mojibake_decode(value)
                        if decoded is not None:
                            line = f"{entity_key} = {decoded}\n"
                    
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('.desc'):
                        desc_line = lines[i + 1]
                        if detect_mojibake(desc_line):
                            if entity_id in entities_cache:
                                entity = entities_cache[entity_id]
                                if entity.get('description'):
                                    desc_translated = translate_text(entity['description'], TRANSLATIONS)
                                    desc_line = f"    .desc = {desc_translated}\n"
                                    lines[i + 1] = desc_line
                            if detect_mojibake(desc_line):
                                desc_match = re.match(r'^\s*\.desc\s*=\s*(.+)', desc_line)
                                if desc_match:
                                    desc_val = desc_match.group(1).strip()
                                    desc_decoded = fix_mojibake_decode(desc_val)
                                    if desc_decoded is not None:
                                        lines[i + 1] = f"    .desc = {desc_decoded}\n"
        
        # Проверяем на английский текст
        if not line.strip().startswith('#'):
            # Проверяем строку с ключом
            if line.strip().startswith(('ent-', 'vessel-', 'mono-', 'research-', 'winter-', 'drake-', 'steel-', 'harmony-', 'midnight-', 'ussp-', 'dark-', 'aetherion-', 'horizon-', 'universal-', 'civil-', 'southern-', 'ullman-', 'nosske-', 'blackhawk-', 'zealots-', 'cult-', 'The-Hive-', 'paycheck-', 'cerberus-', 'viper-')):
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    entity_key = key_match.group(1)
                    entity_id = entity_key.replace('ent-', '').replace('vessel-', '').replace('mono-', '').replace('research-', '').replace('winter-', '').replace('drake-', '').replace('steel-', '').replace('harmony-', '').replace('midnight-', '').replace('ussp-', '').replace('dark-', '').replace('aetherion-', '').replace('horizon-', '').replace('universal-', '').replace('civil-', '').replace('southern-', '').replace('ullman-', '').replace('nosske-', '').replace('blackhawk-', '').replace('zealots-', '').replace('cult-', '').replace('The-Hive-', '').replace('paycheck-', '').replace('cerberus-', '').replace('viper-', '')
                    value = key_match.group(2).strip()
                    
                    # Проверяем, есть ли английский текст в значении
                    if has_english_text(value):
                        has_english = True
                        line_modified = True
                        if entity_id in entities_cache:
                            entity = entities_cache[entity_id]
                            name_source = entity.get('suffix') or entity.get('name') or ''
                            if not name_source and entity.get('parent'):
                                parent_name = get_parent_name(entity['parent'])
                                if parent_name:
                                    suffix = entity.get('suffix') or ''
                                    if suffix:
                                        name_source = f"{parent_name} {suffix}"
                                    else:
                                        name_source = parent_name
                            if name_source:
                                name_translated = translate_text(name_source, TRANSLATIONS)
                                line = f"{entity_key} = {name_translated}\n"
                            else:
                                line = f"{entity_key} = {translate_text(value, TRANSLATIONS)}\n"
                        else:
                            line = f"{entity_key} = {translate_text(value, TRANSLATIONS)}\n"
            
            # Проверяем строку с описанием
            elif line.strip().startswith('.desc'):
                desc_match = re.match(r'^\s*\.desc\s*=\s*(.+)', line)
                if desc_match:
                    desc_value = desc_match.group(1).strip()
                    # Исключаем ссылки на другие ключи
                    if not desc_value.startswith('{'):
                        if has_english_text(desc_value):
                            has_english = True
                            line_modified = True
                            if i > 0:
                                prev_key_match = re.match(r'^(\S+)\s*=', lines[i-1])
                                if prev_key_match:
                                    entity_key = prev_key_match.group(1)
                                    entity_id = entity_key.replace('ent-', '').replace('vessel-', '').replace('mono-', '').replace('research-', '').replace('winter-', '').replace('drake-', '').replace('steel-', '').replace('harmony-', '').replace('midnight-', '').replace('ussp-', '').replace('dark-', '').replace('aetherion-', '').replace('horizon-', '').replace('universal-', '').replace('civil-', '').replace('southern-', '').replace('ullman-', '').replace('nosske-', '').replace('blackhawk-', '').replace('zealots-', '').replace('cult-', '').replace('The-Hive-', '').replace('paycheck-', '').replace('cerberus-', '').replace('viper-', '')
                                    if entity_id in entities_cache:
                                        entity = entities_cache[entity_id]
                                        if entity.get('description'):
                                            # Используем полный перевод из YAML, а не частичный
                                            desc_translated = translate_text(entity['description'], TRANSLATIONS)
                                            line = f"    .desc = {desc_translated}\n"
                                        else:
                                            # Пробуем перевести напрямую
                                            desc_translated = translate_text(desc_value, TRANSLATIONS)
                                            line = f"    .desc = {desc_translated}\n"
                                    else:
                                        # Пробуем перевести напрямую
                                        desc_translated = translate_text(desc_value, TRANSLATIONS)
                                        line = f"    .desc = {desc_translated}\n"
        
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
    if has_mojibake or has_english:
        try:
            with open(ftl_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True, has_mojibake, has_english
        except Exception as e:
            return False, False, False
    
    return False, False, False

def main():
    """Основная функция"""
    print("Исправление всех переводов в папке _Mono...")
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
    mojibake_count = 0
    english_count = 0
    
    # Проходим по всем FTL файлам
    for ftl_file in LOCALE_DIR.rglob('*.ftl'):
        rel_path = ftl_file.relative_to(LOCALE_DIR)
        
        fixed, has_mojibake, has_english = fix_ftl_file(ftl_file)
        
        if fixed:
            fixed_count += 1
            if has_mojibake:
                mojibake_count += 1
            if has_english:
                english_count += 1
            print(f"[OK] {rel_path}")
    
    print()
    print(f"Готово!")
    print(f"Исправлено файлов: {fixed_count}")
    print(f"  - с Mojibake: {mojibake_count}")
    print(f"  - с английским текстом: {english_count}")

if __name__ == "__main__":
    main()
