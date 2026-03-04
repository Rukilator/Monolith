#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный скрипт для завершения перевода всех файлов в папке entities.
Исправляет Mojibake, переводит английский текст, использует кэш YAML файлов.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Пути
LOCALE_DIR = Path(r"G:\Monolith_Forge\Resources\Locale\ru-RU\ss14-ru\prototypes\_Mono\entities")
PROTOTYPES_DIR = Path(r"G:\Monolith_Forge\Resources\Prototypes\_Mono\Entities")

# Расширенный словарь переводов
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
    
    # Оружие - общие термины
    "Registered": "ЧВК",
    "pistol": "пистолет",
    "rifle": "винтовка",
    "SMG": "ПП",
    "shotgun": "дробовик",
    "sniper": "снайперская винтовка",
    "magazine": "магазин",
    "cartridge": "патрон",
    "projectile": "снаряд",
    "ammo": "боеприпасы",
    "ammunition": "боеприпасы",
    "empty": "пустой",
    "pistol magazine": "пистолетный магазин",
    "SMG magazine": "магазин ПП",
    "machine pistol magazine": "магазин для пистолета-пулемёта",
    "top-mounted magazine": "магазин верхнего крепления",
    
    # AmmoLoader
    "ammo loader": "загрузчик боеприпасов",
    "small ammo loader": "малый загрузчик боеприпасов",
    "A pneumatic ammunition loading system manufactured by Erebus HI. Link it to ship artillery with a multitool to transfer ammunition. This model supports 8 guns.": 
        "Пневматическая система загрузки боеприпасов производства Erebus HI. Подключите её к корабельной артиллерии мультитулом для передачи боеприпасов. Эта модель поддерживает 8 орудий.",
    "A pneumatic ammunition loading system manufactured by Erebus HI. Link it to ship artillery with a multitool to transfer ammunition. This model supports only 2 guns, but is more durable.": 
        "Пневматическая система загрузки боеприпасов производства Erebus HI. Подключите её к корабельной артиллерии мультитулом для передачи боеприпасов. Эта модель поддерживает только 2 орудия, но более прочная.",
    
    # Clothing - шлемы
    "helmet": "шлем",
    "ballistic helmet": "баллистический шлем",
    "hardsuit helmet": "шлем скафандра",
    "combat helmet": "боевой шлем",
    "light ballistic helmet": "лёгкий баллистический шлем",
    "heavy helmet": "тяжёлый шлем",
    "M86 helmet": "шлем M86",
    "M82 helmet": "шлем M82",
    "USSP heavy helmet": "тяжёлый шлем USSP",
    "USSP officer cap": "фуражка офицера USSP",
    "USSP commisar cap": "фуражка комиссара USSP",
    "beer hat": "шапка с пивом",
    "JACKAL mk.II viper hardsuit helmet": "шлем скафандра JACKAL mk.II Viper",
    "IMP mk.III viper hardsuit helmet": "шлем скафандра IMP mk.III Viper",
    "USSP L-27 tacsuit helmet": "шлем тактического костюма USSP L-27",
    "USSP L-10 lightsuit helmet": "шлем лёгкого костюма USSP L-10",
    "USSP L-10-A lightsuit helmet": "шлем лёгкого костюма USSP L-10-A",
    "USSP M-10 scoutsuit helmet": "шлем разведывательного костюма USSP M-10",
    "USSP L-30 Commissar parade hardsuit tactical helmet": "тактический шлем парадного скафандра комиссара USSP L-30",
    "USSP UF-16 \"Voenkom\" commissar tacsuit helmet": "шлем тактического костюма комиссара USSP UF-16 \"Военком\"",
    "armored EVA helmet": "бронированный шлем EVA",
    "U.I. ENFORCER MKI helmet": "шлем U.I. ENFORCER MKI",
    "U.I. ENFORCER MKII Combat helmet": "боевой шлем U.I. ENFORCER MKII",
    "U.I. engineering helmet": "инженерный шлем U.I.",
    "U.I. pilot helmet": "шлем пилота U.I.",
    "U.I. VK-1 experimental helmet": "экспериментальный шлем U.I. VK-1",
    "armed trauma unit T-23 tacsuit helmet": "шлем тактического костюма вооружённого отряда травматологии T-23",
    "armed trauma unit T-53 tacsuit helmet": "шлем тактического костюма вооружённого отряда травматологии T-53",
    "PDV SCAF hardsuit helmet": "шлем скафандра PDV SCAF",
    "WL-01 helmet": "шлем WL-01",
    "PDV CV-32 combat tacsuit helmet": "шлем боевого тактического костюма PDV CV-32",
    "PDV CV-53 combat hardsuit helmet": "шлем боевого скафандра PDV CV-53",
    "PDV CV-67 combat hardsuit helmet": "шлем боевого скафандра PDV CV-67",
    "kasature-pattern combat harness helmet": "шлем боевого подвеса образца касатур",
    
    # Clothing - бронежилеты и пластины
    "bulletproof vest": "бронежилет",
    "kevlar vest": "кевларовый жилет",
    "armor plate": "бронепластина",
    "light bulletproof vest": "лёгкий бронежилет",
    "medium bulletproof vest": "средний бронежилет",
    "heavy bulletproof vest": "тяжёлый бронежилет",
    "polyvalent bulletproof vest": "универсальный бронежилет",
    "stabproof bulletproof vest": "антиколющий бронежилет",
    "A simple kevlar vest of unknown origin. This one is a simple bulletproof vest made to resist low caliber rounds.":
        "Простой кевларовый жилет неизвестного происхождения. Это простой бронежилет, предназначенный для защиты от патронов малого калибра.",
    "A simple kevlar vest of unknown origin. This one is more heavily reinforced against bullet at the cost of it being cumbersome.":
        "Простой кевларовый жилет неизвестного происхождения. Этот более усилен против пуль, но за счёт громоздкости.",
    "A simple kevlar vest of unknown origin. This juggernaut vest makes you practically a walking tank at, at the cose of heat protection and extreme bulk.":
        "Простой кевларовый жилет неизвестного происхождения. Этот жилет-джаггернаут делает вас практически ходячим танком, но за счёт защиты от тепла и крайней громоздкости.",
    "A simple kevlar vest of unknown origin. This one isn't made to protect against a specific type of threat.":
        "Простой кевларовый жилет неизвестного происхождения. Этот не предназначен для защиты от конкретного типа угрозы.",
    "A simple kevlar vest of unknown origin. This one is reinforced against stabbings.":
        "Простой кевларовый жилет неизвестного происхождения. Этот усилен против колющих ударов.",
    "durathread plate": "пластина из дураткани",
    "ceramic plate": "керамическая пластина",
    "plasteel plate": "пластина из пластали",
    "plastitanium plate": "пластина из пластитания",
    "Light": "лёгкая",
    "Medium": "средняя",
    "Tactical": "тактическая",
    "Admeme": "пластитаниевая",
    "A lightweight protective plate made from advanced durathread fibers. Initially manufactured by Aether, but the process has long been reverse-engineered.":
        "Лёгкая защитная пластина из продвинутых волокон дураткани. Изначально производилась Aether, но процесс давно был обратно спроектирован.",
    "A medium-weight ceramic composite plate manufactured with a material process proprietary to Aether.":
        "Средняя керамическая композитная пластина, изготовленная по запатентованному процессу Aether.",
    "A heavy-duty plasteel plate manufactured by a layered cold-stamping process proprietary to Aether.":
        "Тяжёлая пластиновая пластина из пластали, изготовленная по запатентованному процессу многослойной холодной штамповки Aether.",
    "An advanced plastitanium composite plate manufactured by Aether.":
        "Продвинутая композитная пластина из пластитания производства Aether.",
    
    # Clothing - костюмы
    "hardsuit": "скафандр",
    "tacsuit": "тактический костюм",
    "EVA suit": "костюм EVA",
    "combat suit": "боевой костюм",
    "JACKAL mk.II viper hardsuit": "скафандр JACKAL mk.II Viper",
    "IMP mk.III viper hardsuit": "скафандр IMP mk.III Viper",
    "USSP UF-16 \"Voenkom\" commissar tacsuit": "тактический костюм комиссара USSP UF-16 \"Военком\"",
    "armored EVA suit": "бронированный костюм EVA",
    "U.I. ENFORCER combat tacsuit": "боевой тактический костюм U.I. ENFORCER",
    "U.I. ENFORCER MKII combat tacsuit": "боевой тактический костюм U.I. ENFORCER MKII",
    "M-320X AURORA exosuit": "экзокостюм M-320X AURORA",
    "SelfUnremovable": "экзокостюм Аврора",
    "An experimental exosuit designed for the future of warfare. Despite not having any head covering, the utilization of new nanomachine technology allows it to protect the wearer from the pressure and cold of space.":
        "Экспериментальный экзокостюм, разработанный для будущего войны. Несмотря на отсутствие защиты головы, использование новой технологии наномашин позволяет защитить носителя от давления и холода космоса.",
    "An armored hardsuit, designed to be an upgrade for the M82 series. The extra armor gives it some more weight to move around.":
        "Бронированный скафандр, разработанный как улучшение серии M82. Дополнительная броня добавляет веса при движении.",
    "The interchangeable helmet system for the majority of M82 hardsuits. Outfitted with a basic NVG system.":
        "Взаимозаменяемая система шлемов для большинства скафандров M82. Оснащена базовой системой ночного видения.",
    "A hardsuit helmet with signature markings of the Viper Group. Has a built-in nightvision system.":
        "Шлем скафандра с характерными маркировками группы Viper. Имеет встроенную систему ночного видения.",
    "A hardsuit helmet with signature markings of the Viper Group. Has a built-in medical HUD complemented by thermal pulse systems.":
        "Шлем скафандра с характерными маркировками группы Viper. Имеет встроенный медицинский HUD, дополненный системами теплового импульса.",
    "The standard combat suit of USSP naval operations, outfitted with a medical hud too!":
        "Стандартный боевой костюм морских операций USSP, также оснащён медицинским HUD!",
    "An old USSP model of combat suit that is still in use in the frontlines.":
        "Старая модель боевого костюма USSP, всё ещё используемая на передовой.",
    "A new prototype of combat suit using the old L-10 as a baseline. It has a integrated mass scanner in his helmet.":
        "Новый прототип боевого костюма, использующий старый L-10 в качестве основы. Имеет встроенный масс-сканер в шлеме.",
    "The commissar's parade hardsuit helmet, outfitted with a medical hud too to check on the troops!":
        "Шлем парадного скафандра комиссара, также оснащённый медицинским HUD для проверки войск!",
    "A standard EVA helmet modified by the UNSA as a cheap and cool-looking alternative to voidsuits for use by vanguards. The skull is a necessity.":
        "Стандартный шлем EVA, модифицированный UNSA как дешёвая и стильная альтернатива вакуумным костюмам для использования авангардом. Череп — необходимость.",
    "This top of the line helmet comes with flashproof lining, a mass scanner and an inbuilt medical diagnostic system.":
        "Этот топовый шлем поставляется с защитой от вспышек, масс-сканером и встроенной системой медицинской диагностики.",
    "A cheap and effective hardsuit helmet, just with an extra black market touch.":
        "Дешёвый и эффективный шлем скафандра, просто с дополнительным налётом чёрного рынка.",
    "A helmet for Ullman Industry pilots.":
        "Шлем для пилотов Ullman Industry.",
    "A purpose built helmet designed by Felix Ullman, for Felix Ullman.":
        "Шлем специальной конструкции, разработанный Феликсом Уллманом для Феликса Уллмана.",
    "The standard combat suit of the Armed Trauma Unit, outfitted with a limited-range radar hud as well as a medical hud.":
        "Стандартный боевой костюм Вооружённого отряда травматологии, оснащённый HUD радара ограниченного радиуса действия, а также медицинским HUD.",
    "An old SCAF suit painted in an PDV tan color scheme. The lighting systems have been replaced with a thermal pulse.":
        "Старый костюм SCAF, окрашенный в коричневую цветовую схему PDV. Системы освещения заменены на тепловой импульс.",
    "A heavy headgear piece accompanying the Warlord suit, it offers flash inmunity aswell mass scanner support.":
        "Тяжёлый элемент головного убора, сопровождающий костюм Warlord, обеспечивает защиту от вспышек, а также поддержку масс-сканера.",
    "A combat tacsuit designed in the Phaethon Dynasty.":
        "Боевой тактический костюм, разработанный в династии Фаэтон.",
    "Based off of the CV-32, sacrifices combat protection for environment protection.":
        "Основан на CV-32, жертвует боевой защитой ради защиты окружающей среды.",
    "An adorned tacsuit designed with an imperfect nanolaminate composition. High maneuverability, sturdy armor.":
        "Украшенный тактический костюм, разработанный с несовершенным наноламинатным составом. Высокая манёвренность, прочная броня.",
    "Part of an advanced pre-fracture combat harness.":
        "Часть продвинутого боевого подвеса до Раскола.",
    
    # Clothing - обувь и прочее
    "boots": "ботинки",
    "magboots": "магнитные ботинки",
    "shoes": "обувь",
    "puffy vest": "пуховая жилетка",
    "Old robe": "старая мантия",
    
    # Combat uniforms (уже есть в fix_ammoloader_clothing_translations.py, но добавлю основные)
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
    
    # Дополнительные переводы для бронежилетов и шлемов
    "light ballistic helmet": "лёгкий баллистический шлем",
    "A light ballistic helmet to protect against small arms.":
        "Лёгкий баллистический шлем для защиты от стрелкового оружия.",
    "A light ballistic helmet to protect against small arms":
        "Лёгкий баллистический шлем для защиты от стрелкового оружия",
    "A simple kevlar vest of unknown origin. This one is a simple bulletproof vest made to resist low caliber rounds.":
        "Простой кевларовый жилет неизвестного происхождения. Это простой бронежилет, предназначенный для защиты от патронов малого калибра.",
    "A simple kevlar vest of unknown origin. This one is more heavily reinforced against bullet at the cost of it being cumbersome.":
        "Простой кевларовый жилет неизвестного происхождения. Этот более усилен против пуль, но за счёт громоздкости.",
    "A simple kevlar vest of unknown origin. This juggernaut vest makes you practically a walking tank at, at the cose of heat protection and extreme bulk.":
        "Простой кевларовый жилет неизвестного происхождения. Этот жилет-джаггернаут делает вас практически ходячим танком, но за счёт защиты от тепла и крайней громоздкости.",
    "A simple kevlar vest of unknown origin. This one isn't made to protect against a specific type of threat.":
        "Простой кевларовый жилет неизвестного происхождения. Этот не предназначен для защиты от конкретного типа угрозы.",
    "A simple kevlar vest of unknown origin. This one is reinforced against stabbings.":
        "Простой кевларовый жилет неизвестного происхождения. Этот усилен против колющих ударов.",
    
    # Дополнительные переводы для костюмов и одежды
    "U.I. ENFORCER combat tacsuit": "боевой тактический костюм U.I. ENFORCER",
    "U.I. ENFORCER MKII combat tacsuit": "боевой тактический костюм U.I. ENFORCER MKII",
    "U.I. engineering hardsuit": "инженерный скафандр U.I.",
    "U.I. pilot voidsuit": "вакуумный костюм пилота U.I.",
    "U.I. VK-1 experimental hardsuit": "экспериментальный скафандр U.I. VK-1",
    "Infamously one of the most reliable combat tacsuits that the Black Market has to offer, developed by Ullman Industries. \"Heads up display sold seperately!\"":
        "Печально известный один из самых надёжных боевых тактических костюмов, которые предлагает Чёрный рынок, разработанный Ullman Industries. \"HUD продаётся отдельно!\"",
    "Based off of the infamous MKI design with versatility in mind. This is Ullman Industries' top of the line combat suit. Whether it be slipping away from the feds, taking out the competition, or serving your corporate overlords, this marvel of engineering will make sure that you get it done.":
        "Основан на печально известном дизайне MKI с упором на универсальность. Это топовый боевой костюм Ullman Industries. Будь то уход от федов, устранение конкурентов или служение вашим корпоративным повелителям, это чудо инженерии гарантирует, что вы справитесь.",
    "A protective hardsuit worn by black market engineering specialists. Developed by Ullman Industries.":
        "Защитный скафандр, носимый инженерными специалистами чёрного рынка. Разработан Ullman Industries.",
    "A voidsuit made for black market pilots. Developed by Ullman Industries":
        "Вакуумный костюм, созданный для пилотов чёрного рынка. Разработан Ullman Industries",
    "Felix Ullman's top of the line personal hardsuit. A warning label engraved on the chestplate reads \"Theft of this suit has a high chance of death! Seriously, I will find you. You will die.\"":
        "Топовый личный скафандр Феликса Уллмана. Предупреждающая надпись, выгравированная на нагрудной пластине, гласит: \"Кража этого костюма имеет высокий шанс смерти! Серьёзно, я найду вас. Вы умрёте.\"",
    "USSP officer coat": "пальто офицера USSP",
    "A comfy coat used by the officers of the USSP.":
        "Удобное пальто, используемое офицерами USSP.",
    "EMT jacket": "куртка парамедика",
    "A bright yellow signal jacket, beloved by paramedics of the end of the 21st century.":
        "Ярко-жёлтая сигнальная куртка, любимая парамедиками конца 21 века.",
    "armed trauma unit T-23 tacsuit": "тактический костюм вооружённого отряда травматологии T-23",
    "armed trauma unit T-53 tacsuit": "тактический костюм вооружённого отряда травматологии T-53",
    "PDV SCAF hardsuit": "скафандр PDV SCAF",
    "PMC WL-01": "ЧВК WL-01",
    "PDV CV-32 combat tacsuit": "боевой тактический костюм PDV CV-32",
    "PDV CV-67 combat tacsuit": "боевой тактический костюм PDV CV-67",
    "PDV CV-53 combat hardsuit": "боевой скафандр PDV CV-53",
    "DME EVA Suit": "костюм EVA DME",
    "Panzerkorps Varyag": "Панцеркорпс Варяг",
    "Marshevyye Varyag": "Маршевые Варяг",
    "Sapogi Zastavnika": "Сапоги Заставника",
    "RX-01 modsuit ботинки": "ботинки модкостюма RX-01",
    "Volta Modsuit Boots": "ботинки модкостюма Volta",
    "mercenary modsuit ботинки": "ботинки модкостюма наёмника",
    "painted магнитные ботинки": "окрашенные магнитные ботинки",
    "voidботинки": "вакуумные ботинки",
    "pre-fracture магнитные ботинки": "магнитные ботинки до Раскола",
    "tactical магнитные ботинки": "тактические магнитные ботинки",
    "advanced tactical магнитные ботинки": "продвинутые тактические магнитные ботинки",
    "tan tactical swat ботинки": "коричневые тактические ботинки SWAT",
    "olive tactical swat ботинки": "оливковые тактические ботинки SWAT",
    "black tactical swat ботинки": "чёрные тактические ботинки SWAT",
    "ranger green tactical swat ботинки": "тактические ботинки SWAT зелёного рейнджера",
    "coyote brown tactical swat ботинки": "тактические ботинки SWAT коричневого койота",
    "white tactical swat ботинки": "белые тактические ботинки SWAT",
    "Heavy-duty boots designed for combat and EVA.":
        "Тяжёлые ботинки, разработанные для боя и EVA.",
    "Thick, reinforced boots with magnetic stabilizers and shock absorption.":
        "Толстые усиленные ботинки с магнитными стабилизаторами и амортизацией.",
    
    # Оружие - турели и режимы
    "NanoTrasen": "NanoTrasen",
    "Hostile": "Враждебный",
    "All hostile": "Все враждебные",
    "Syndicate": "Синдикат",
    "TSF": "TSF",
    "PDV": "PDV",
    "Medical": "Медицинский",
    "Rogue AI": "Враждебный ИИ",
    
    # Оружие - дробовики
    "Big Leady": "Big Leady",
    "Big Johnny": "Big Johnny",
    "Big Buddy": "Big Buddy",
    "UW12-B Helepolis": "UW12-B Helepolis",
    "4 gauge": "4 калибр",
    "12 gauge": "12 калибр",
    
    # Оружие - снайперские винтовки
    "MI Lee Enfield Mk 98": "MI Lee Enfield Mk 98",
    "7.62x51mm": "7.62x51mm",
    
    # Оружие - ПП
    "NTSF-HCLM-45": "NTSF-HCLM-45",
    ".45 magnum": ".45 magnum",
    "LWC Knallstock": "LWC Knallstock",
    "9x19mm/.45 ACP": "9x19mm/.45 ACP",
    "PA Keyboard": "PA Keyboard",
    ".45 ACP": ".45 ACP",
    "HWM Firestarter": "HWM Firestarter",
    
    # Оружие - винтовки
    "HWM FCM-C \"Vulcan\"": "HWM FCM-C \"Vulcan\"",
    "HWM FCL \"Prometheus\"": "HWM FCL \"Prometheus\"",
    "5.56x45mm": "5.56x45mm",
    "NTSF-LTR-556": "NTSF-LTR-556",
    "6.8x52mm Caseless": "6.8x52mm Caseless",
    
    # Боеприпасы - снаряды
    "Heavy Pulse Bolt": "тяжёлый импульсный болт",
    "Explosive Pulse Bolt": "взрывной импульсный болт",
    "energy slug": "энергетический снаряд",
    "energy": "энергия",
    "gestalt bolt": "болт гештальта",
    "golum spike": "шип голума",
    "PulsedPlasma": "импульсная плазма",
    "UllmanPulse": "импульс Уллмана",
    "UllmanPulseHeavy": "тяжёлый импульс Уллмана",
    
    # Описания дробовиков
    "A massive 4 gauge (23x75mm) shotgun made to kill what any caliber bellow autocannon cant.":
        "Массивный дробовик 4-го калибра (23x75мм), созданный уничтожать то, что не может ни один калибр ниже автопушки.",
    "A massive 4 gauge (23x75mm) shotgun made to kill what any caliber bellow autocannon cant. This one is outfitted with various tactical additions and is made for CQC at the cost of low ammo capacity.":
        "Массивный дробовик 4-го калибра (23x75мм), созданный уничтожать то, что не может ни один калибр ниже автопушки. Этот оснащён различными тактическими дополнениями и создан для ближнего боя за счёт низкой ёмкости боеприпасов.",
    "The Union Wrightworks 12-gauge breaching model \"Helepolis\", a compact shotgun that sacrifices all combat ergonomics to better serve as a breaching tool. Breaks doors with slugs. Combat use unadvised.":
        "Модель пролома Union Wrightworks 12-го калибра \"Helepolis\", компактный дробовик, который жертвует всей боевой эргономикой, чтобы лучше служить инструментом пролома. Разбивает двери снарядами. Боевое использование не рекомендуется.",
    "heavy ballistic turret": "тяжёлая баллистическая турель",
    "A massively reinforced turret, firing a barrage of 8x65mm SKR rounds that rip up targets. Woe be the fool who walks in front of this.":
        "Массивно усиленная турель, стреляющая залпом патронов 8x65mm SKR, которые разрывают цели. Горе глупцу, который пройдёт перед этим.",
    
    # Описания боевых форм (добавлю основные)
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
    "Digital camouflaged combat suit. Camo in space...":
        "Боевой костюм в цифровом камуфляже. Камуфляж в космосе...",
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

def has_english_text(text):
    """Проверяет, содержит ли текст английские слова (кроме имен собственных)"""
    if not text:
        return False
    # Ищем английские слова (минимум 2 буквы), но исключаем аббревиатуры и имена собственные
    english_word_pattern = re.compile(r'\b([a-zA-Z]{2,})\b')
    matches = english_word_pattern.findall(text)
    # Исключаем известные аббревиатуры и имена собственных
    excluded = {'USSP', 'TSF', 'TSFMC', 'UNSA', 'CCE', 'MOPP', 'CBURN', 'PDV', 'SCAF', 'EVA', 'U.I.', 'UI', 'MKI', 'MKII', 'MKIII', 'FMJ', 'AP', 'HE', 'EMP', 'HP', 'RIP', 'SAM', 'ACP', 'GCS', 'ADS', 'GPOL', 'LOSAT', 'ECM', 'ASM', 'ADMP', 'TPC', 'ADEX', 'NVG', 'HUD', 'Drake', 'Industries', 'Aether', 'Erebus', 'HI', 'Viper', 'Group', 'JACKAL', 'IMP', 'Voenkom', 'Felix', 'Ullman', 'Misko', 'Lampart', 'M86', 'M82', 'L-27', 'L-10', 'L-10-A', 'M-10', 'L-30', 'UF-16', 'VK-1', 'T-23', 'T-53', 'WL-01', 'CV-32', 'CV-53', 'CV-67', 'M-320X', 'AURORA', 'mk.II', 'mk.III', 'Type', 'B', 'MOPP', 'mk', 'II', 'III', 'OUTP', 'CA', 'diagonal', 'of', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should', 'may', 'might', 'must', 'shall'}
    
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
            
            if line.strip().startswith('ent-'):
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
        if not line.strip().startswith('#'):
            # Проверяем строку с ключом
            if line.strip().startswith('ent-'):
                key_match = re.match(r'^(\S+)\s*=\s*(.+)', line)
                if key_match:
                    entity_key = key_match.group(1)
                    entity_id = entity_key.replace('ent-', '')
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
                                    entity_id = entity_key.replace('ent-', '')
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

def validate_translations():
    """Валидация всех переводов"""
    print("\nВалидация переводов...")
    issues = []
    
    for ftl_file in LOCALE_DIR.rglob('*.ftl'):
        try:
            with open(ftl_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if detect_mojibake(line):
                    issues.append(f"{ftl_file.relative_to(LOCALE_DIR)}:{i} - Mojibake обнаружен")
                elif line.strip() and not line.strip().startswith('#') and has_english_text(line):
                    # Исключаем строки с ссылками на другие ключи FTL
                    if not re.match(r'^\s*\{', line) and not re.match(r'^\s*\.(desc|suffix|name)\s*=\s*\{', line):
                        # Проверяем, не является ли это именем собственным или аббревиатурой
                        if not re.match(r'^\s*ent-\w+\s*=\s*[A-Z0-9\s\.\-\"\(\)]+$', line):
                            issues.append(f"{ftl_file.relative_to(LOCALE_DIR)}:{i} - Английский текст: {line[:50]}")
        except Exception as e:
            issues.append(f"{ftl_file.relative_to(LOCALE_DIR)} - Ошибка чтения: {e}")
    
    if issues:
        print(f"Найдено проблем: {len(issues)}")
        for issue in issues[:20]:  # Показываем первые 20
            print(f"  {issue}")
        if len(issues) > 20:
            print(f"  ... и ещё {len(issues) - 20} проблем")
    else:
        print("Все файлы проверены, проблем не найдено!")
    
    return len(issues) == 0

def main():
    """Основная функция"""
    print("Завершение перевода всех файлов в папке entities...")
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
    
    # Валидация
    validate_translations()

if __name__ == "__main__":
    main()
