#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки и исправления переводов в папке entities.
Исправляет Mojibake, английский текст и улучшает качество переводов.
"""

import os
import re
from pathlib import Path

# Пути
LOCALE_DIR = Path(r"G:\Monolith_Forge\Resources\Locale\ru-RU\ss14-ru\prototypes\_Mono\entities")
PROTOTYPES_DIR = Path(r"G:\Monolith_Forge\Resources\Prototypes\_Mono\Entities")

# Словарь переводов для исправления английских фраз
TRANSLATIONS = {
    # Общие фразы
    "Can be remotely activated": "Может быть активирована дистанционно",
    "or linked up to a GCS": "или подключена к GCS",
    "or linked to a GCS": "или подключена к GCS",
    "Can be remotely activated or linked to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "Can be remotely activated, or linked up to a GCS": "Может быть активирована дистанционно или подключена к GCS",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки",
    "This model is powered by an autoloader somewhere nearby and does not require manual reloading.": "Эта модель питается от автозагрузчика где-то поблизости и не требует ручной перезарядки.",
    
    # Напитки
    "chamomile tea": "ромашковый чай",
    "berry tea": "ягодный чай",
    "fruit tea": "фруктовый чай",
    "Yorkshire tea": "йоркширский чай",
    "decaf black tea": "чёрный чай без кофеина",
    "syndie tea": "чай Синдиката",
    "decaf coffee": "кофе без кофеина",
    
    # Оружие
    "Registered": "ЧВК",
    
    # Технические термины (оставляем как есть, но можем добавить пояснения)
    "GCS": "GCS",  # Оставляем аббревиатуру
    "ADS": "ADS",  # Оставляем аббревиатуру
    "EMP": "ЭМИ",
    "TSF": "TSF",  # Оставляем аббревиатуру
    "GPOL": "GPOL",  # Оставляем аббревиатуру
}

def detect_mojibake(text):
    """Определяет, содержит ли текст Mojibake (испорченную кириллицу)"""
    # Паттерны Mojibake: последовательности типа РјР°РіР°Р·РёРЅ
    mojibake_pattern = re.compile(r'[РЎРўРЈР¤РҐР¦Р§РЁРЄРЅР®РЇ][Р°Р±РІРіРґРµРёР№РєР»РјРЅРѕРїСЂСЃС‚СѓС„С…С†С‡С€С‰СЉС‹СЊСЌСЋСЏ]')
    return bool(mojibake_pattern.search(text))

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
            
            # Ищем id, name, description, suffix
            id_match = re.search(r'^\s*id:\s*(\S+)', block, re.MULTILINE)
            name_match = re.search(r'^\s*name:\s*(.+)', block, re.MULTILINE)
            desc_match = re.search(r'^\s*description:\s*(.+)', block, re.MULTILINE)
            suffix_match = re.search(r'^\s*suffix:\s*(.+)', block, re.MULTILINE)
            
            entity_id = id_match.group(1) if id_match else None
            name = name_match.group(1).strip() if name_match else None
            description = desc_match.group(1).strip() if desc_match else None
            suffix = suffix_match.group(1).strip() if suffix_match else None
            
            # Убираем кавычки если есть
            for field in [name, description, suffix]:
                if field and field.startswith('"') and field.endswith('"'):
                    field = field[1:-1]
            
            if entity_id:
                entities.append({
                    'id': entity_id,
                    'name': name,
                    'description': description,
                    'suffix': suffix
                })
        
        return entities
    except Exception as e:
        print(f"Ошибка при чтении {yml_path}: {e}")
        return []

def translate_text(text, translations_dict):
    """Переводит текст используя словарь"""
    if not text:
        return text
    
    translated = text
    # Применяем переводы в порядке длины (сначала длинные фразы)
    for eng, rus in sorted(translations_dict.items(), key=lambda x: -len(x[0])):
        translated = translated.replace(eng, rus)
    
    return translated

def fix_ftl_file(ftl_path, proto_dir):
    """Исправляет FTL файл"""
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
        print(f"  Ошибка: не удалось прочитать файл {ftl_path}")
        return False, False, False
    
    has_mojibake = False
    has_english = False
    fixed_lines = []
    seen_keys = set()
    
    # Находим соответствующий YAML файл
    rel_path = ftl_path.relative_to(LOCALE_DIR)
    proto_rel = str(rel_path).replace('entities/', '').replace('.ftl', '.yml')
    proto_path = proto_dir / proto_rel
    
    entities_map = {}
    if proto_path.exists():
        entities_list = extract_entities_from_yml(proto_path)
        for entity in entities_list:
            entities_map[entity['id']] = entity
    
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
                    
                    if entity_id in entities_map:
                        entity_data = entities_map[entity_id]
                        # Используем suffix или name для перевода
                        name_source = entity_data.get('suffix') or entity_data.get('name') or ''
                        if name_source:
                            name_translated = translate_text(name_source, TRANSLATIONS)
                            line = f"{entity_key} = {name_translated}\n"
                        else:
                            # Если нет suffix/name, оставляем ключ как есть, но убираем Mojibake из значения
                            # Пытаемся восстановить из Mojibake (это сложно, лучше использовать YAML)
                            pass
                    
                    # Проверяем следующую строку на описание
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('.desc'):
                        desc_line = lines[i + 1]
                        if detect_mojibake(desc_line):
                            if entity_id in entities_map:
                                entity_data = entities_map[entity_id]
                                if entity_data.get('description'):
                                    desc_translated = translate_text(entity_data['description'], TRANSLATIONS)
                                    desc_line = f"    .desc = {desc_translated}\n"
                                    lines[i + 1] = desc_line
            else:
                # Если это не строка с ent-, но содержит Mojibake, пытаемся исправить
                # Это может быть описание или другой текст
                if i > 0 and lines[i-1].strip().startswith('ent-'):
                    # Это может быть описание предыдущей сущности
                    prev_key_match = re.match(r'^(\S+)\s*=', lines[i-1])
                    if prev_key_match:
                        entity_key = prev_key_match.group(1)
                        entity_id = entity_key.replace('ent-', '')
                        if entity_id in entities_map:
                            entity_data = entities_map[entity_id]
                            if entity_data.get('description'):
                                desc_translated = translate_text(entity_data['description'], TRANSLATIONS)
                                line = f"    .desc = {desc_translated}\n"
                                line_modified = True
        
        # Проверяем на английский текст (кроме имен собственных и аббревиатур)
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
                    continue  # Пропускаем дубликат
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
            print(f"  Ошибка при записи {ftl_path}: {e}")
            return False, False, False
    
    return False, False, False

def main():
    """Основная функция"""
    print("Проверка и исправление переводов в папке entities...")
    print(f"Папка локализации: {LOCALE_DIR}")
    print(f"Папка прототипов: {PROTOTYPES_DIR}")
    print()
    
    if not LOCALE_DIR.exists():
        print(f"Ошибка: папка {LOCALE_DIR} не найдена!")
        return
    
    if not PROTOTYPES_DIR.exists():
        print(f"Предупреждение: папка {PROTOTYPES_DIR} не найдена, некоторые исправления могут быть невозможны")
    
    fixed_count = 0
    mojibake_count = 0
    english_count = 0
    
    # Проходим по всем FTL файлам
    for ftl_file in LOCALE_DIR.rglob('*.ftl'):
        rel_path = ftl_file.relative_to(LOCALE_DIR)
        print(f"Проверка: {rel_path}")
        
        fixed, has_mojibake, has_english = fix_ftl_file(ftl_file, PROTOTYPES_DIR)
        
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
