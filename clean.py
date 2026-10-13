#!/usr/bin/env python3
"""
Удаляет всё, что нагенерировал generate.py, и failed/ от selfcheck.py.
Сам cleanup.py, generate.py и selfcheck.py не трогает.

Запуск:
    python3 cleanup.py            # спросит подтверждение
    python3 cleanup.py --yes      # без вопросов
    python3 cleanup.py --dry-run  # показать, что будет удалено
"""
import sys
import shutil
import argparse
from pathlib import Path


ROOT = Path(__file__).parent.resolve()

# Что удаляем (папки)
TARGET_DIRS = ["task1", "task2", "task3", "task4", "task5", "failed"]

# Что НЕ удаляем (на всякий случай — если что-то из этого лежит в TARGET_DIRS)
KEEP = {"generate.py", "selfcheck.py", "cleanup.py"}


def find_targets():
    """Возвращает список путей, которые будут удалены."""
    found = []
    for name in TARGET_DIRS:
        p = ROOT / name
        if p.exists():
            found.append(p)
    return found


def human_size(path):
    """Размер папки в человекочитаемом виде."""
    total = 0
    if path.is_file():
        return path.stat().st_size
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def fmt_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Не спрашивать подтверждение")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Только показать, что будет удалено")
    args = parser.parse_args()

    targets = find_targets()
    if not targets:
        print("Нечего удалять — нагенерированных файлов не найдено.")
        return

    print(f"Директория: {ROOT}\n")
    print("Будет удалено:")
    total_size = 0
    for p in targets:
        size = human_size(p)
        total_size += size
        kind = "директория" if p.is_dir() else "файл"
        print(f"  [{kind}] {p.name}  ({fmt_size(size)})")
    print(f"\nВсего: {fmt_size(total_size)}")

    if args.dry_run:
        print("\n--dry-run: ничего не удалено.")
        return

    if not args.yes:
        answer = input("\nУдалить? [y/N] ").strip().lower()
        if answer not in ("y", "yes", "д", "да"):
            print("Отменено.")
            return

    # Удаляем
    for p in targets:
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            print(f"  удалено: {p.name}")
        except OSError as e:
            print(f"  ошибка при удалении {p.name}: {e}", file=sys.stderr)

    print("\nГотово.")


if __name__ == "__main__":
    main()
