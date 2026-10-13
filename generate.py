#!/usr/bin/env python3
"""
Создаёт структуру для проверочной: папки task1..task5 и копирует решения из папки solutions.
Входные данные НЕ генерирует — этим занимается selfcheck.py при запуске.

Запуск (из чистой папки):
    python3 generate.py
"""

import sys
import os
from pathlib import Path

SCRIPT_NAMES = {
    "task1": "welcome.sh",
    "task2": "check_environs.sh",
    "task3": "find_fraud.sh",
    "task4": "ban_manager.sh",
    "task5": "report.sh",
}

def build():
    root = Path(__file__).parent.resolve()
    solutions_dir = root / "solutions"
    
    # Проверяем, существует ли папка с решениями
    if not solutions_dir.exists():
        print(f"Ошибка: Папка с решениями не найдена: {solutions_dir}")
        sys.exit(1)

    # Проверяем, нет ли уже созданных папок заданий
    existing = [d for d in SCRIPT_NAMES if (root / d).exists()]
    if existing:
        print(f"В текущей директории уже есть: {', '.join(existing)}")
        print("Удали их (cleanup.py) или запусти генератор в чистой папке.")
        sys.exit(1)

    # Копируем файлы решений в соответствующие папки
    for task, script in SCRIPT_NAMES.items():
        source_file = solutions_dir / script
        target_file = root / task / script

        # Проверяем, что исходный файл решения существует
        if not source_file.exists():
            print(f"Ошибка: Файл решения {script} не найден в {solutions_dir}")
            sys.exit(1)

        # Создаем целевую папку (например, task1)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Читаем решение и записываем в целевой файл
        content = source_file.read_text(encoding="utf-8")
        target_file.write_text(content, encoding="utf-8")
        
        # Делаем файл исполняемым
        os.chmod(target_file, 0o755)

    print(f"Структура успешно создана в: {root}")
    print("Решения скопированы из папки solutions.")
    print()
    print("Не забудь положить task.md в каждую папку.")
    print("Тестовые данные генерируются автоматически при запуске selfcheck.py.")

if __name__ == "__main__":
    build()

