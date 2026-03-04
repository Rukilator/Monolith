#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для полной перегенерации переводов в папке entities из YAML файлов.
Исправляет все проблемы с Mojibake и английским текстом.
"""

import os
import re
from pathlib import Path

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
                    'suffix': suffix
                })
        
        return entities
    except Exception as e:
        print(f"  Ошибка при чтении {yml_path}: {e}")
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

def generate_ftl_content(entities_list):
    """Генерирует содержимое FTL файла из списка сущностей"""
    lines = []
    seen_ids = set()
    
    for entity in entities_list:
        entity_id = entity['id']
        if entity_id in seen_ids:
            continue
        seen_ids.add(entity_id)
        
        # Используем suffix или name для перевода
        name_source = entity.get('suffix') or entity.get('name') or ''
        if name_source:
            name_translated = translate_text(name_source, TRANSLATIONS)
            lines.append(f"ent-{entity_id} = {name_translated}\n")
            
            # Добавляем описание если есть
            if entity.get('description'):
                desc_translated = translate_text(entity['description'], TRANSLATIONS)
                lines.append(f"    .desc = {desc_translated}\n")
    
    return lines

def process_yml_file(yml_path, locale_dir, proto_dir):
    """Обрабатывает YAML файл и создает/обновляет соответствующий FTL файл"""
    # Вычисляем относительный путь
    rel_path = yml_path.relative_to(proto_dir)
    
    # Преобразуем путь: Objects/consumable/drinks/drinks.yml -> entities/objects/consumable/drinks/drinks.ftl
    ftl_rel = str(rel_path).replace('Entities', 'entities').replace('.yml', '.ftl')
    ftl_path = locale_dir / ftl_rel
    
    # Извлекаем сущности
    entities_list = extract_entities_from_yml(yml_path)
    
    if not entities_list:
        return False
    
    # Генерируем содержимое FTL
    ftl_content = generate_ftl_content(entities_list)
    
    if not ftl_content:
        return False
    
    # Создаем директорию если нужно
    ftl_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Записываем файл
    try:
        with open(ftl_path, 'w', encoding='utf-8') as f:
            f.writelines(ftl_content)
        return True
    except Exception as e:
        print(f"  Ошибка при записи {ftl_path}: {e}")
        return False

def main():
    """Основная функция"""
    print("Перегенерация переводов в папке entities из YAML файлов...")
    print(f"Папка локализации: {LOCALE_DIR}")
    print(f"Папка прототипов: {PROTOTYPES_DIR}")
    print()
    
    if not PROTOTYPES_DIR.exists():
        print(f"Ошибка: папка {PROTOTYPES_DIR} не найдена!")
        return
    
    processed_count = 0
    
    # Проходим по всем YAML файлам
    for yml_file in PROTOTYPES_DIR.rglob('*.yml'):
        rel_path = yml_file.relative_to(PROTOTYPES_DIR)
        print(f"Обработка: {rel_path}")
        
        if process_yml_file(yml_file, LOCALE_DIR, PROTOTYPES_DIR):
            processed_count += 1
            print(f"  [OK] Создан/обновлен FTL файл")
        else:
            print(f"  [SKIP] Нет сущностей или ошибка")
    
    print()
    print(f"Готово!")
    print(f"Обработано файлов: {processed_count}")

if __name__ == "__main__":
    main()
