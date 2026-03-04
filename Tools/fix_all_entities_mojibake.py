#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления всех файлов с Mojibake в папке entities.
Обрабатывает существующие FTL файлы и исправляет их на основе YAML файлов.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Пути
LOCALE_DIR = Path(r"G:\Monolith_Forge\Resources\Locale\ru-RU\ss14-ru\prototypes\_Mono\entities")
PROTOTYPES_DIR = Path(r"G:\Monolith_Forge\Resources\Prototypes\_Mono\Entities")

# Словарь переводов
TRANSLATIONS = {
    "chamomile tea": "ромашковый чай",
    "berry tea": "ягодный чай",
    "fruit tea": "фруктовый чай",
    "Yorkshire tea": "йоркширский чай",
    "decaf black tea": "чёрный чай без кофеина",
    "syndie tea": "чай Синдиката",
    "decaf coffee": "кофе без кофеина",
    "Registered": "ЧВК",
    "Can be remotely activated": "Может быть активирована дистанционно",
    "or linked up to a GCS": "или подключена к GCS",
    "or linked to a GCS": "или подключена к GCS",
    "Can be remotely activated or linked to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "Can be remotely activated, or linked up to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading.": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки.",
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
                # Убираем кавычки и скобки
                parent = parent.strip()
                if parent.startswith('['):
                    # Список родителей
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

def get_parent_name(entity_id):
    """Получает имя родительской сущности"""
    if entity_id not in entities_cache:
        return None
    
    entity = entities_cache[entity_id]
    if entity.get('name'):
        return entity['name']
    
    # Если у родителя нет имени, проверяем его родителей
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
        print(f"  Ошибка: не удалось прочитать файл")
        return False, False
    
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
            
            # Пытаемся найти соответствующую сущность
            if line.strip().startswith('ent-'):
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    entity_key = key_match.group(1)
                    entity_id = entity_key.replace('ent-', '')
                    
                    if entity_id in entities_cache:
                        entity = entities_cache[entity_id]
                        
                        # Используем suffix или name для перевода
                        name_source = entity.get('suffix') or entity.get('name') or ''
                        
                        # Если есть только suffix и есть родитель, пытаемся получить имя родителя
                        if not name_source and entity.get('parent'):
                            parent_name = get_parent_name(entity['parent'])
                            if parent_name:
                                # Комбинируем имя родителя с suffix
                                suffix = entity.get('suffix') or ''
                                if suffix:
                                    name_source = f"{parent_name} {suffix}"
                                else:
                                    name_source = parent_name
                        
                        if name_source:
                            name_translated = translate_text(name_source, TRANSLATIONS)
                            line = f"{entity_key} = {name_translated}\n"
                    
                    # Проверяем следующую строку на описание
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('.desc'):
                        desc_line = lines[i + 1]
                        if detect_mojibake(desc_line):
                            if entity_id in entities_cache:
                                entity = entities_cache[entity_id]
                                if entity.get('description'):
                                    desc_translated = translate_text(entity['description'], TRANSLATIONS)
                                    desc_line = f"    .desc = {desc_translated}\n"
                                    lines[i + 1] = desc_line
        
        # Проверяем на английский текст
        english_pattern = re.compile(r'\b(Can be|or linked|This model|is powered|does not require|manual reloading|remotely activated|chamomile tea|berry tea|fruit tea|Yorkshire tea|decaf|syndie tea|Registered)\b', re.IGNORECASE)
        if english_pattern.search(line) and not line.strip().startswith('#'):
            has_english = True
            line = translate_text(line, TRANSLATIONS)
            line_modified = True
        
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
            print(f"  Ошибка при записи: {e}")
            return False, False, False
    
    return False, False, False

def main():
    """Основная функция"""
    print("Исправление всех файлов с Mojibake в папке entities...")
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
        print(f"Проверка: {rel_path}")
        
        fixed, has_mojibake, has_english = fix_ftl_file(ftl_file)
        
        if fixed:
            fixed_count += 1
            if has_mojibake:
                mojibake_count += 1
                print(f"  [OK] Исправлен Mojibake")
            if has_english:
                english_count += 1
                print(f"  [OK] Исправлен английский текст")
        else:
            print(f"  [OK]")
    
    print()
    print(f"Готово!")
    print(f"Исправлено файлов: {fixed_count}")
    print(f"  - с Mojibake: {mojibake_count}")
    print(f"  - с английским текстом: {english_count}")

if __name__ == "__main__":
    main()
