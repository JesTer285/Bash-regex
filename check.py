#!/usr/bin/env python3
"""
Самопроверка решений студента.
Генерирует входные данные, прогоняет скрипты студента, сравнивает
с ожиданием. Если тест упал — сохраняет данные в failed/<task>_<i>/.

Запуск из корня папки:
    python3 selfcheck.py
    python3 selfcheck.py --task task3
    python3 selfcheck.py --dump-tests
"""
import os
import re
import sys
import random
import shutil
import string
import signal
import time
import argparse
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).parent.resolve()
FAILED_DIR = ROOT / "failed"
DUMP_DIR = ROOT / "tests_dump"

SCRIPT_NAMES = {
    "task1": "welcome.sh",
    "task2": "check_environs.sh",
    "task3": "find_fraud.sh",
    "task4": "ban_manager.sh",
    "task5": "report.sh",
}

NICKS = ["Steve", "Alex", "Notch", "Herobrine", "Dinnerbone",
         "Grumm", "jeb_", "NoobMaster69", "EnderDragon",
         "CreeperKing", "DiamondMiner", "RedstoneGuru"]

REASONS = ["cheating", "griefing", "duping", "advertising",
           "insulting", "afk_farming", "xray", "fly_hack"]

ITEMS = ["diamond", "iron", "gold", "redstone", "lapis",
         "emerald", "netherite", "coal"]

DEFAULTS = {
    "SERVER_NAME": "StarCraft",
    "MAX_PLAYERS": "125",
    "SPAWN_COORDS": "274 67 -249",
}


def run_sh(script, cwd, args=None, stdin=None, env=None, timeout=10):
    if args is None:
        args = []
    if not script.exists():
        return "", f"{script} не найден", 127
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        r = subprocess.run(
            ["sh", str(script), *args],
            cwd=str(cwd), input=stdin,
            capture_output=True, text=True,
            timeout=timeout, env=full_env,
        )
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", 124


def save_failure(task, idx, files):
    dst = FAILED_DIR / f"{task}_{idx}"
    dst.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        p = dst / name
        if isinstance(content, Path):
            shutil.copy(content, p)
        else:
            p.write_text(content, encoding="utf-8")
    return dst


def random_nick():
    return random.choice(NICKS) + str(random.randint(1, 999))


# ============ TASK 1 ============
def iter_task1():
    cases = []

    cases += [
        ("abc", 0), ("a" * 16, 0), ("Steve", 0), ("Alex_123", 0),
        ("Xx_Destroyer_xX", 0), ("___", 0), ("123", 0), ("000", 0),
        ("ABC", 0), ("abc", 0), ("aBc", 0),
        ("a_b_c_d_e_f_g_h_i", 1), ("a1b2c3d4e5f6g7h8", 0),
        ("_a_", 0), ("zZ9_", 0),
    ]

    cases += [
        ("", 1), ("a", 1), ("ab", 1),
        ("a" * 17, 1), ("a" * 18, 1), ("a" * 100, 1), ("a" * 1000, 1),
    ]

    cases += [
        (" ", 1), ("  ", 1), (" a", 1), ("a ", 1), (" a ", 1),
        ("a b", 1), ("a\tb", 1), ("\ta", 1), ("a\n", 1), ("a\nb", 1),
    ]

    cases += [
        ("a-b", 1), ("-ab", 1), ("ab-", 1), ("a.b", 1),
        ("..", 1), ("a..b", 1),
    ]

    for ch in "!@#$%^&*()+=/\\|?<>,;:\"'`~^[]{}":
        cases.append((f"nick{ch}", 1))

    cases += [
        ("НикНаРусском", 1), ("Ник_123", 1), ("日本語", 1),
        ("Ünïcödé", 1), ("café", 1), ("😀", 1), ("😀😀", 1),
        ("a😀b", 1), ("ＡＢＣ", 1),
    ]

    for _ in range(10):
        n = random.randint(3, 16)
        cases.append(("".join(random.choices(
            string.ascii_letters + string.digits + "_", k=n)), 0))

    random.shuffle(cases)
    return cases


def check_task1():
    lvl = ROOT / "task1"
    script = lvl / SCRIPT_NAMES["task1"]
    cases = iter_task1()
    for i, (nick, expected_code) in enumerate(cases):
        out, err, code = run_sh(script, lvl, [nick])
        ok = True
        if expected_code == 0:
            if code != 0 or "Welcome," not in out:
                ok = False
        else:
            if code != 1 or "Invalid nickname" not in err:
                ok = False
        if not ok:
            expected_desc = (
                f"exit code = 0\n"
                f"stdout    = 'Welcome, {nick}!'\n"
                f"stderr    = ''\n"
                if expected_code == 0 else
                f"exit code = 1\n"
                f"stdout    = ''\n"
                f"stderr    = 'Invalid nickname'\n"
            )
            failed = save_failure("task1", i, {
                "input.txt": f"nick={nick!r}\n",
                "expected.txt": expected_desc,
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {out!r}\n"
                    f"stderr    = {err!r}\n"
                ),
            })
            return False, (f"итерация {i}: ник {nick!r}, "
                           f"ожидался код {expected_code}, получен {code}. "
                           f"Смотри {failed}")
    return True, f"{len(cases)} кейсов пройдено"


# ============ TASK 2 ============
def iter_task2():
    return [
        {"env": {}},
        {"env": {"SERVER_NAME": "MyServer", "MAX_PLAYERS": "50",
                 "SPAWN_COORDS": "100 64 200"}},
        {"env": {"SERVER_NAME": "OnlyName"}},
        {"env": {"MAX_PLAYERS": "999"}},
        {"env": {"SPAWN_COORDS": "-1 0 1"}},
        {"env": {"SERVER_NAME": "TwoVars", "MAX_PLAYERS": "10"}},
        {"env": {"SERVER_NAME": "TwoVars", "SPAWN_COORDS": "1 2 3"}},
        {"env": {"MAX_PLAYERS": "10", "SPAWN_COORDS": "1 2 3"}},
        {"env": {"SERVER_NAME": ""}},
        {"env": {"MAX_PLAYERS": ""}},
        {"env": {"SPAWN_COORDS": ""}},
        {"env": {"SERVER_NAME": "", "MAX_PLAYERS": ""}},
        {"env": {"SERVER_NAME": "", "MAX_PLAYERS": "", "SPAWN_COORDS": ""}},
        {"env": {"MAX_PLAYERS": "100000"}},
        {"env": {"MAX_PLAYERS": "999999999"}},
        {"env": {"SPAWN_COORDS": "-1000 -1000 -1000"}},
        {"env": {"SPAWN_COORDS": "0 0 0"}},
        {"env": {"SERVER_NAME": "My Server"}},
        {"env": {"SERVER_NAME": "Сервер 1"}},
        {"env": {"SPAWN_COORDS": "30000000 -64 -30000000"}},
    ]


def check_task2():
    lvl = ROOT / "task2"
    script = lvl / SCRIPT_NAMES["task2"]
    conf = lvl / "server.conf"
    tests = iter_task2()
    for i, test in enumerate(tests):
        if conf.exists():
            conf.unlink()
        env = test["env"]
        out, err, code = run_sh(script, lvl, [], env=env)
        problems = []
        if code != 0:
            problems.append(f"код {code}, stderr={err!r}")
        elif not conf.exists():
            problems.append("server.conf не создан")
        else:
            content = conf.read_text()
            for var in ["SERVER_NAME", "MAX_PLAYERS", "SPAWN_COORDS"]:
                exp = env.get(var, DEFAULTS[var]) or DEFAULTS[var]
                m = re.search(rf'^{var}=(.*)$', content, re.MULTILINE)
                if not m:
                    problems.append(f"{var} не найден")
                    continue
                got = m.group(1).strip().strip('"').strip("'")
                if got != exp:
                    problems.append(f"{var}: ожидалось {exp!r}, получено {got!r}")
        if problems:
            expected_conf = "\n".join(
                f"{k}={(env.get(k) or DEFAULTS[k])!r}"
                for k in ["SERVER_NAME", "MAX_PLAYERS", "SPAWN_COORDS"]
            )
            actual_conf = conf.read_text() if conf.exists() else "<нет>"
            failed = save_failure("task2", i, {
                "input.txt": "env: " + repr(env) + "\n",
                "expected.txt": (
                    "exit code = 0\n"
                    "stdout    = <содержимое server.conf>\n"
                    "stderr    = ''\n"
                    "\n"
                    "Ожидаемый server.conf:\n"
                    + expected_conf + "\n"
                ),
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {out!r}\n"
                    f"stderr    = {err!r}\n"
                    f"\nФактический server.conf:\n{actual_conf}\n"
                ),
            })
            return False, (f"итерация {i}: env={env}. "
                           f"{problems[0]}. Смотри {failed}")
    return True, f"{len(tests)} env-тестов пройдено"


# ============ TASK 3 ============
def gen_transactions():
    players = [random_nick() for _ in range(random.randint(5, 10))]
    lines = []
    for _ in range(random.randint(20, 40)):
        a, b = random.sample(players, 2)
        lines.append(f"{a} -> {b} {random.randint(1,100)} {random.choice(ITEMS)}")
    cheaters = set()
    for _ in range(random.randint(1, 3)):
        c = random.choice(players)
        if c in cheaters:
            continue
        cheaters.add(c)
        for _ in range(random.randint(5, 10)):
            b = random.choice([p for p in players if p != c])
            lines.append(f"{c} -> {b} {random.randint(500,2000)} diamond")
    random.shuffle(lines)
    return lines


def fixtures_task3():
    return [
        ("all_cheaters", [
            "A -> B 1000 diamond",
            "B -> C 1000 diamond",
            "C -> A 1000 diamond",
        ]),
        ("balanced", ["A -> B 100 iron", "B -> A 100 iron"]),
        ("one_player", ["A -> B 50 diamond", "B -> A 50 diamond"]),
        ("only_income", ["A -> B 100 iron", "A -> B 200 iron"]),
        ("only_expense", ["A -> B 100 iron", "A -> B 200 iron",
                          "B -> C 50 iron"]),
        ("exact_balance", ["A -> B 500 diamond", "B -> A 500 diamond"]),
        ("diff_by_one", ["A -> B 101 iron", "B -> A 100 iron"]),
        ("empty", []),
        ("one_line", ["A -> B 100 diamond"]),
        ("self_loop", ["A -> A 100 diamond"]),
        ("many_items", ["A -> B 10 diamond", "A -> B 20 iron",
                        "A -> B 30 gold", "B -> A 60 coal"]),
        ("big_numbers", ["A -> B 1000000 diamond",
                         "B -> A 999999 diamond"]),
        ("zero_amounts", ["A -> B 0 diamond", "B -> A 0 iron"]),
    ]


def expected_fraud(lines):
    income = defaultdict(int)
    expense = defaultdict(int)
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue
        a, b, amount = parts[0], parts[2], int(parts[3])
        expense[a] += amount
        income[b] += amount
    return sorted(p for p in set(income) | set(expense)
                  if expense.get(p, 0) > income.get(p, 0))


def check_task3():
    lvl = ROOT / "task3"
    script = lvl / SCRIPT_NAMES["task3"]

    all_cases = list(fixtures_task3())
    for k in range(8):
        all_cases.append((f"random_{k}", gen_transactions()))

    for i, (name, lines) in enumerate(all_cases):
        tmp = lvl / "_selfcheck.log"
        tmp.write_text("\n".join(lines) + ("\n" if lines else ""))
        exp = expected_fraud(lines)
        out, err, code = run_sh(script, lvl, [str(tmp)])
        got = sorted(set(l for l in out.strip().split("\n") if l))
        ok = (code == 0 and got == exp)
        if not ok:
            expected_stdout = "\n".join(exp) if exp else "<пусто>"
            failed = save_failure("task3", i, {
                "transactions.log": tmp.read_text(),
                "expected.txt": (
                    f"Кейс: {name}\n"
                    f"exit code = 0\n"
                    f"stdout    = список читеров (построчно):\n"
                    f"{expected_stdout}\n"
                    f"stderr    = ''\n"
                ),
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {got!r}\n"
                    f"stderr    = {err!r}\n"
                ),
            })
            tmp.unlink(missing_ok=True)
            return False, (f"кейс {name}: ожидалось {exp}, получено {got}. "
                           f"Смотри {failed}")
        tmp.unlink(missing_ok=True)
    return True, f"{len(all_cases)} кейсов пройдено"


# ============ TASK 4 ============
def fixtures_task4():
    return [
        ("typical", [
            "Herobrine1 01:01:2024 cheating",
            "Alex2 02:02:2024 griefing",
            "Steve3 03:03:2024 cheating",
            "Herobrine1 01:01:2024 cheating",
            "11_Steve_11 05:05:2024 griefing",
            "11_Steve_11 06:06:2024 cheating",
            "Notch4 04:04:2024 advertising",
        ]),
        ("no_11steve", ["A1 01:01:2024 cheating", "B2 02:02:2024 griefing"]),
        ("only_11steve", ["11_Steve_11 01:01:2024 griefing"]),
        ("all_duplicates", ["X 01:01:2024 a", "X 01:01:2024 a",
                            "X 01:01:2024 a"]),
        ("empty", []),
        ("one_line", ["Solo 01:01:2024 cheating"]),
        ("many_duplicates", [
            "A 01:01:2024 x", "A 01:01:2024 x",
            "B 02:02:2024 y", "B 02:02:2024 y",
            "C 03:03:2024 z", "C 03:03:2024 z",
            "11_Steve_11 04:04:2024 w",
        ]),
        ("11steve_in_centre", [
            "Alpha 01:01:2024 a",
            "11_Steve_11 02:02:2024 b",
            "Beta 03:03:2024 c",
        ]),
        ("unsorted", [
            "Zeta 05:05:2024 z",
            "Alpha 01:01:2024 a",
            "Mike 03:03:2024 m",
        ]),
        ("same_names", [
            "Same 01:01:2024 a",
            "Same 02:02:2024 b",
            "Same 03:03:2024 c",
        ]),
    ]


def check_task4():
    lvl = ROOT / "task4"
    script = lvl / SCRIPT_NAMES["task4"]
    banlist = lvl / "banlist.txt"

    fixtures = fixtures_task4()
    for i, (name, lines) in enumerate(fixtures):
        banlist.write_text("\n".join(lines) + ("\n" if lines else ""))
        expected_format = sorted(set(
            l for l in lines if not l.startswith("11_Steve_11 ")
        ))

        # format
        tmp = lvl / "_selfcheck_banlist.txt"
        tmp.write_text("\n".join(lines) + ("\n" if lines else ""))
        out, err, code = run_sh(script, lvl, ["format", str(tmp)])
        got = sorted(set(l for l in tmp.read_text().splitlines() if l.strip()))
        if code != 0 or got != expected_format:
            expected_out = ("\n".join(expected_format)
                            if expected_format else "<пусто>")
            failed = save_failure("task4", f"{name}_format", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"format ({name})\n"
                    f"exit code = 0\n"
                    f"stdout    = '' (или пусто)\n"
                    f"stderr    = ''\n"
                    f"\nОжидаемое содержимое banlist после format:\n"
                    f"{expected_out}\n"
                ),
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {out!r}\n"
                    f"stderr    = {err!r}\n"
                ),
            })
            tmp.unlink(missing_ok=True)
            return False, f"format ({name}) упал. Смотри {failed}"
        tmp.unlink(missing_ok=True)

        # add (3)
        banlist.write_text("\n".join(lines) + ("\n" if lines else ""))
        new_nick = "Test" + str(random.randint(100, 999))
        new_time = "01:01:2025"
        new_reason = "cheating"
        out, err, code = run_sh(script, lvl,
                                ["add", new_nick, new_time, new_reason])
        content = banlist.read_text()
        if code != 0 or new_nick not in content:
            failed = save_failure("task4", f"{name}_add3", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"add(3 арг) ({name}): {new_nick} {new_time} {new_reason}\n"
                    f"exit code = 0\n"
                    f"stdout    = ''\n"
                    f"stderr    = ''\n"
                    f"\nПосле add ник {new_nick} должен быть в banlist\n"
                ),
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {out!r}\n"
                    f"stderr    = {err!r}\n"
                    f"\nФактический banlist:\n{content}\n"
                ),
            })
            return False, f"add(3) ({name}) упал. Смотри {failed}"

        # add (1)
        run_sh(script, lvl,
               ["add", f"{new_nick} {new_time} {new_reason}"])
        content = banlist.read_text()
        if content.count(new_nick) > 1:
            failed = save_failure("task4", f"{name}_add1", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"add(1 арг) ({name}): '{new_nick} {new_time} {new_reason}'\n"
                    f"exit code = 0\n"
                    f"stdout    = ''\n"
                    f"stderr    = ''\n"
                    f"\nПосле повторного add ник {new_nick} должен быть один раз\n"
                ),
                "actual.txt": (
                    f"ник {new_nick} встречается {content.count(new_nick)} раз\n"
                ),
            })
            return False, f"add(1) ({name}) упал. Смотри {failed}"

        # info
        if lines:
            target = lines[0].split()[0]
            out, err, code = run_sh(script, lvl, ["info", target])
            if target not in out:
                failed = save_failure("task4", f"{name}_info", {
                    "banlist.txt": "\n".join(lines) + "\n",
                    "expected.txt": (
                        f"info ({name}): info {target}\n"
                        f"exit code = 0\n"
                        f"stdout    = строка с {target} "
                        f"(nickname time reason)\n"
                        f"stderr    = ''\n"
                    ),
                    "actual.txt": (
                        f"exit code = {code}\n"
                        f"stdout    = {out!r}\n"
                        f"stderr    = {err!r}\n"
                    ),
                })
                return False, f"info ({name}) упал. Смотри {failed}"

        # remove
        if lines:
            target_rm = lines[-1].split()[0]
            run_sh(script, lvl, ["remove", target_rm])
            content = banlist.read_text()
            if target_rm in content:
                failed = save_failure("task4", f"{name}_remove", {
                    "banlist.txt": "\n".join(lines) + "\n",
                    "expected.txt": (
                        f"remove ({name}): remove {target_rm}\n"
                        f"exit code = 0\n"
                        f"stdout    = ''\n"
                        f"stderr    = ''\n"
                        f"\nПосле remove ник {target_rm} не должен "
                        f"встречаться в banlist\n"
                    ),
                    "actual.txt": f"{target_rm} остался в banlist\n",
                })
                return False, f"remove ({name}) упал. Смотри {failed}"

        # sort --name
        run_sh(script, lvl, ["sort", "--name", "sorted_name.txt"])
        f = lvl / "sorted_name.txt"
        if not f.exists():
            failed = save_failure("task4", f"{name}_sortname", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"sort --name ({name})\n"
                    f"exit code = 0\n"
                    f"stdout    = ''\n"
                    f"stderr    = ''\n"
                    f"\nДолжен быть создан файл sorted_name.txt "
                    f"(отсортирован по нику)\n"
                ),
            })
            return False, f"sort --name ({name}) упал. Смотри {failed}"
        lines_sorted = [l for l in f.read_text().splitlines() if l.strip()]
        names_sorted = [l.split()[0] for l in lines_sorted]
        if names_sorted != sorted(names_sorted):
            failed = save_failure("task4", f"{name}_sortname", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"sort --name ({name}): sorted_name.txt "
                    f"должен быть отсортирован по нику\n"
                ),
                "actual.txt": "\n".join(lines_sorted) + "\n",
            })
            return False, f"sort --name ({name}) упал. Смотри {failed}"

        # sort --time
        run_sh(script, lvl, ["sort", "--time", "sorted_time.txt"])
        f = lvl / "sorted_time.txt"
        if not f.exists():
            failed = save_failure("task4", f"{name}_sorttime", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"sort --time ({name})\n"
                    f"exit code = 0\n"
                    f"stdout    = ''\n"
                    f"stderr    = ''\n"
                    f"\nДолжен быть создан файл sorted_time.txt "
                    f"(отсортирован по времени DD:MM:YYYY)\n"
                ),
            })
            return False, f"sort --time ({name}) упал. Смотри {failed}"
        lines_sorted = [l for l in f.read_text().splitlines() if l.strip()]

        def tkey(line):
            parts = line.split()
            if len(parts) < 2:
                return (0, 0, 0)
            try:
                d, m, y = parts[1].split(":")
                return (int(y), int(m), int(d))
            except ValueError:
                return (0, 0, 0)

        times = [tkey(l) for l in lines_sorted]
        if times != sorted(times):
            failed = save_failure("task4", f"{name}_sorttime", {
                "banlist.txt": "\n".join(lines) + "\n",
                "expected.txt": (
                    f"sort --time ({name}): sorted_time.txt "
                    f"должен быть отсортирован по времени\n"
                ),
                "actual.txt": "\n".join(lines_sorted) + "\n",
            })
            return False, f"sort --time ({name}) упал. Смотри {failed}"

    return True, f"{len(fixtures)} наборов пройдено"


# ============ TASK 5 ============
def gen_task5_data():
    players = [random_nick() for _ in range(random.randint(5, 15))]
    bans = [random_nick() for _ in range(random.randint(2, 8))]
    tx = []
    for _ in range(random.randint(10, 30)):
        a, b = random.sample(players, 2)
        tx.append(f"{a} -> {b} {random.randint(1,200)} {random.choice(ITEMS)}")
    return players, bans, tx


def fixtures_task5():
    return [
        ("empty_all", [], [], []),
        ("only_players", ["A", "B", "C"], [], []),
        ("only_bans", [], ["X", "Y"], []),
        ("only_tx", [], [], ["A -> B 10 diamond", "B -> A 5 iron"]),
        ("one_of_each", ["A"], ["B"], ["A -> B 1 iron"]),
        ("many_players", [f"P{i}" for i in range(50)], ["B1"],
         ["P0 -> P1 10 diamond", "P2 -> P3 20 iron"]),
        ("many_bans", ["A"], [f"B{i}" for i in range(50)],
         ["A -> B 1 iron"]),
        ("many_tx", ["A", "B"], ["C"],
         [f"A -> B {i} diamond" for i in range(1, 51)]),
        ("big_amounts", ["A", "B"], ["C"],
         ["A -> B 999999999 diamond"]),
        ("tie_top", ["A", "B", "C"], ["D"],
         ["A -> B 10 diamond", "A -> C 10 iron"]),
    ]


def expected_top_item(tx):
    """
    Возвращает имя предмета с максимальной суммой amount.
    При равенстве — лексикографически меньший.
    Если транзакций нет — пустая строка.
    """
    totals = defaultdict(int)
    for line in tx:
        parts = line.split()
        if len(parts) < 5:
            continue
        totals[parts[4]] += int(parts[3])
    if not totals:
        return ""
    max_total = max(totals.values())
    candidates = [k for k, v in totals.items() if v == max_total]
    return min(candidates)


def expected_report(players, bans, tx):
    return {
        "Players": len(players),
        "Bans": len(bans),
        "Transactions": len(tx),
        "Top item": expected_top_item(tx),
    }


def write_files(lvl, players, bans, tx):
    (lvl / "players.txt").write_text(
        "\n".join(players) + ("\n" if players else ""))
    (lvl / "banlist.txt").write_text(
        "\n".join(bans) + ("\n" if bans else ""))
    (lvl / "transactions.log").write_text(
        "\n".join(tx) + ("\n" if tx else ""))


def report_expected_text(exp):
    return (
        "StarCraft server report\n"
        "\n"
        f"Players: {exp['Players']}\n"
        f"Bans: {exp['Bans']}\n"
        f"Transactions: {exp['Transactions']}\n"
        f"Top item: {exp['Top item']}\n"
    )


def check_task5():
    lvl = ROOT / "task5"
    script = lvl / SCRIPT_NAMES["task5"]
    report = lvl / "report.txt"
    lock = lvl / "report.lock"

    out, err, code = run_sh(script, lvl, ["--help"])
    if code != 0 or not out.strip():
        failed = save_failure("task5", 0, {
            "expected.txt": (
                "--help\n"
                "exit code = 0\n"
                "stdout    = непустой текст (краткое описание утилиты)\n"
                "stderr    = ''\n"
            ),
            "actual.txt": (
                f"exit code = {code}\n"
                f"stdout    = {out!r}\n"
                f"stderr    = {err!r}\n"
            ),
        })
        return False, f"--help упал. Смотри {failed}"

    cases = list(fixtures_task5())
    for k in range(5):
        cases.append((f"random_{k}", *gen_task5_data()))

    args = ["-p", "players.txt", "-b", "banlist.txt",
            "-t", "transactions.log"]

    for i, (name, players, bans, tx) in enumerate(cases):
        write_files(lvl, players, bans, tx)
        exp = expected_report(players, bans, tx)
        if report.exists():
            report.unlink()
        if lock.exists():
            lock.unlink()
        out, err, code = run_sh(script, lvl, args, timeout=15)
        problems = []
        if code != 0:
            problems.append(f"код {code}, stderr={err!r}")
        elif not report.exists():
            problems.append("report.txt не создан")
        else:
            content = report.read_text()
            for label in ["Players", "Bans", "Transactions"]:
                m = re.search(rf'{label}:\s*(\d+)', content)
                if not m:
                    problems.append(f"{label} не найден")
                elif int(m.group(1)) != exp[label]:
                    problems.append(
                        f"{label}: ожидалось {exp[label]}, получено {m.group(1)}"
                    )
            # Top item: имя без скобок (может быть пустым, если транзакций нет)
            m = re.search(r'Top item:[ \t]*(.*)$', content, re.MULTILINE)
            if not m:
                problems.append("Top item не найден")
            else:
                got_top = m.group(1).strip()
                if got_top != exp["Top item"]:
                    problems.append(
                        f"Top item: ожидалось {exp['Top item']!r}, "
                        f"получено {got_top!r}"
                    )
        if problems:
            actual_report = report.read_text() if report.exists() else "<нет>"
            failed = save_failure("task5", f"{name}", {
                "players.txt": "\n".join(players) + "\n",
                "banlist.txt": "\n".join(bans) + "\n",
                "transactions.log": "\n".join(tx) + "\n",
                "expected.txt": (
                    f"Кейс: {name}\n"
                    f"exit code = 0\n"
                    f"stdout    = ''\n"
                    f"stderr    = ''\n"
                    f"\nОжидаемый report.txt:\n"
                    + report_expected_text(exp)
                ),
                "actual.txt": (
                    f"exit code = {code}\n"
                    f"stdout    = {out!r}\n"
                    f"stderr    = {err!r}\n"
                    f"\nФактический report.txt:\n{actual_report}\n"
                ),
            })
            return False, f"кейс {name}: {problems[0]}. Смотри {failed}"

    # lock
    if lock.exists():
        lock.unlink()
    lock.write_text("")
    if report.exists():
        report.unlink()
    out, err, code = run_sh(script, lvl, args)
    if code != 1 or "Report already in progress" not in err:
        failed = save_failure("task5", "lock", {
            "expected.txt": (
                "защита от параллельного запуска (report.lock уже существует)\n"
                "exit code = 1\n"
                "stdout    = ''\n"
                "stderr    = содержит 'Report already in progress'\n"
            ),
            "actual.txt": (
                f"exit code = {code}\n"
                f"stdout    = {out!r}\n"
                f"stderr    = {err!r}\n"
            ),
        })
        lock.unlink(missing_ok=True)
        return False, f"защита от лока упала. Смотри {failed}"
    lock.unlink(missing_ok=True)

    # SIGINT
    # Перед тестом кладём БОЛЬШОЙ transactions.log, чтобы скрипт
    # не успел завершиться до сигнала. awk будет считать метрики
    # несколько десятых секунды — этого хватит, чтобы поймать процесс.
    big_tx = lvl / "transactions.log"
    with big_tx.open("w") as f:
        for i in range(200000):
            f.write(f"P{i % 100} -> P{(i + 1) % 100} {i % 1000} diamond\n")

    if report.exists():
        report.unlink()
    if lock.exists():
        lock.unlink()

    proc = subprocess.Popen(
        ["sh", str(script), *args],
        cwd=str(lvl),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    # Ждём, пока появится report.lock, но не дольше 2 секунд
    for _ in range(200):
        if lock.exists() or proc.poll() is not None:
            break
        time.sleep(0.01)

    # Если процесс уже завершился — сигнал отправлять поздно
    if proc.poll() is not None:
        proc.kill()
        failed = save_failure("task5", "sigint", {
            "expected.txt": (
                "SIGINT во время работы\n"
                "Скрипт завершился раньше, чем удалось отправить сигнал\n"
                "(проверь, что он не выходит сразу и обрабатывает trap)\n"
            ),
        })
        return False, f"SIGINT не удалось проверить (скрипт слишком быстрый). Смотри {failed}"

    proc.send_signal(signal.SIGINT)
    try:
        out, err = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        failed = save_failure("task5", "sigint", {
            "expected.txt": (
                "SIGINT во время работы\n"
                "exit code = 1\n"
                "stdout    = ''\n"
                "stderr    = содержит 'Reporting was interrupted'\n"
                "report.txt должен быть удалён\n"
                "report.lock должен быть удалён\n"
            ),
            "actual.txt": "скрипт не завершился за 5 секунд\n",
        })
        return False, f"SIGINT упал. Смотри {failed}"
    problems = []
    if "Reporting was interrupted" not in err:
        problems.append(f"нет 'Reporting was interrupted', err={err!r}")
    if report.exists():
        problems.append("report.txt не удалён")
    if lock.exists():
        problems.append("report.lock не удалён")
    if problems:
        failed = save_failure("task5", "sigint", {
            "expected.txt": (
                "SIGINT во время работы\n"
                "exit code = 1\n"
                "stdout    = ''\n"
                "stderr    = содержит 'Reporting was interrupted'\n"
                "report.txt должен быть удалён\n"
                "report.lock должен быть удалён\n"
            ),
            "actual.txt": (
                f"exit code = {proc.returncode}\n"
                f"stdout    = {out!r}\n"
                f"stderr    = {err!r}\n"
                f"report.txt существует: {report.exists()}\n"
                f"report.lock существует: {lock.exists()}\n"
            ),
        })
        return False, f"SIGINT упал. Смотри {failed}"

    return True, f"{len(cases)} наборов + сигналы пройдены"


# ============ DUMP ============
def _write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def dump_task1():
    dst = DUMP_DIR / "task1"
    if dst.exists():
        shutil.rmtree(dst)
    cases = iter_task1()
    for i, (nick, expected_code) in enumerate(cases):
        if expected_code == 0:
            expected = (
                f"nick = {nick!r}\n"
                f"exit code = 0\n"
                f"stdout    = 'Welcome, {nick}!'\n"
                f"stderr    = ''\n"
            )
        else:
            expected = (
                f"nick = {nick!r}\n"
                f"exit code = 1\n"
                f"stdout    = ''\n"
                f"stderr    = 'Invalid nickname'\n"
            )
        _write(dst / f"case_{i:03d}.txt",
               f"# запуск: sh welcome.sh {nick!r}\n\n{expected}")
    return len(cases)


def dump_task2():
    dst = DUMP_DIR / "task2"
    if dst.exists():
        shutil.rmtree(dst)
    tests = iter_task2()
    for i, test in enumerate(tests):
        env = test["env"]
        expected_conf = "\n".join(
            f"{k}={(env.get(k) or DEFAULTS[k])!r}"
            for k in ["SERVER_NAME", "MAX_PLAYERS", "SPAWN_COORDS"]
        )
        _write(dst / f"case_{i:03d}.txt",
               f"env = {env!r}\n"
               f"exit code = 0\n"
               f"stdout    = <содержимое server.conf>\n"
               f"stderr    = ''\n"
               f"\nОжидаемый server.conf:\n{expected_conf}\n")
    return len(tests)


def dump_task3():
    dst = DUMP_DIR / "task3"
    if dst.exists():
        shutil.rmtree(dst)
    cases = list(fixtures_task3())
    for k in range(8):
        cases.append((f"random_{k}", gen_transactions()))
    for i, (name, lines) in enumerate(cases):
        sub = dst / f"case_{i:03d}_{name}"
        _write(sub / "transactions.log",
               "\n".join(lines) + ("\n" if lines else ""))
        exp = expected_fraud(lines)
        expected_stdout = "\n".join(exp) if exp else "<пусто>"
        _write(sub / "expected.txt",
               f"Кейс: {name}\n"
               f"exit code = 0\n"
               f"stdout    = список читеров (построчно):\n"
               f"{expected_stdout}\n"
               f"stderr    = ''\n")
    return len(cases)


def dump_task4():
    dst = DUMP_DIR / "task4"
    if dst.exists():
        shutil.rmtree(dst)
    fixtures = fixtures_task4()
    for i, (name, lines) in enumerate(fixtures):
        sub = dst / f"case_{i:03d}_{name}"
        banlist_text = "\n".join(lines) + ("\n" if lines else "")
        _write(sub / "banlist.txt", banlist_text)

        expected_format = sorted(set(
            l for l in lines if not l.startswith("11_Steve_11 ")
        ))
        fmt_out = "\n".join(expected_format) if expected_format else "<пусто>"

        text = [f"Кейс: {name}", ""]
        text.append("=== format ===")
        text.append("exit code = 0")
        text.append("stdout    = ''")
        text.append("stderr    = ''")
        text.append("Содержимое banlist после format:")
        text.append(fmt_out)
        text.append("")
        text.append("=== add ===")
        text.append("add(3 арг): '<nick>' '<time>' '<reason>'")
        text.append("add(1 арг): '<nick> <time> <reason>'")
        text.append("exit code = 0")
        text.append("stdout    = ''")
        text.append("stderr    = ''")
        text.append("После add ник должен быть в banlist ровно один раз")
        text.append("")
        text.append("=== info ===")
        if lines:
            t = lines[0].split()[0]
            text.append(f"info {t}")
            text.append("exit code = 0")
            text.append(f"stdout    = строка с {t} (nickname time reason)")
            text.append("stderr    = ''")
        text.append("")
        text.append("=== remove ===")
        if lines:
            t = lines[-1].split()[0]
            text.append(f"remove {t}")
            text.append("exit code = 0")
            text.append("stdout    = ''")
            text.append("stderr    = ''")
            text.append(f"После remove {t} не должен встречаться в banlist")
        text.append("")
        text.append("=== sort --name sorted_name.txt ===")
        text.append("exit code = 0")
        text.append("stdout    = ''")
        text.append("stderr    = ''")
        text.append("sorted_name.txt — отсортирован по нику")
        text.append("")
        text.append("=== sort --time sorted_time.txt ===")
        text.append("exit code = 0")
        text.append("stdout    = ''")
        text.append("stderr    = ''")
        text.append("sorted_time.txt — отсортирован по времени DD:MM:YYYY")

        _write(sub / "expected.txt", "\n".join(text) + "\n")
    return len(fixtures)


def dump_task5():
    dst = DUMP_DIR / "task5"
    if dst.exists():
        shutil.rmtree(dst)
    cases = list(fixtures_task5())
    for k in range(5):
        cases.append((f"random_{k}", *gen_task5_data()))
    for i, (name, players, bans, tx) in enumerate(cases):
        sub = dst / f"case_{i:03d}_{name}"
        _write(sub / "players.txt",
               "\n".join(players) + ("\n" if players else ""))
        _write(sub / "banlist.txt",
               "\n".join(bans) + ("\n" if bans else ""))
        _write(sub / "transactions.log",
               "\n".join(tx) + ("\n" if tx else ""))
        exp = expected_report(players, bans, tx)
        _write(sub / "expected.txt",
               f"Кейс: {name}\n"
               f"exit code = 0\n"
               f"stdout    = ''\n"
               f"stderr    = ''\n"
               f"\nОжидаемый report.txt:\n"
               + report_expected_text(exp))
    return len(cases)


def dump_all_tests():
    if DUMP_DIR.exists():
        shutil.rmtree(DUMP_DIR)
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    n1 = dump_task1()
    n2 = dump_task2()
    n3 = dump_task3()
    n4 = dump_task4()
    n5 = dump_task5()

    readme = f"""# tests_dump

Дамп всех тестовых данных и ожидаемых результатов.
Создан флагом `selfcheck.py --dump-tests`.

Скрипты студента НЕ запускались — это только данные для ручного дебага.

| Задача | Кейсов |
|--------|--------|
| task1  | {n1} |
| task2  | {n2} |
| task3  | {n3} |
| task4  | {n4} |
| task5  | {n5} |
"""
    _write(DUMP_DIR / "README.md", readme)

    print(f"Дамп создан: {DUMP_DIR}")
    print(f"  task1: {n1} кейсов")
    print(f"  task2: {n2} кейсов")
    print(f"  task3: {n3} кейсов")
    print(f"  task4: {n4} кейсов")
    print(f"  task5: {n5} кейсов")


# ============ ГЛАВНАЯ ============
CHECKS = {
    "task1": ("welcome.sh", check_task1),
    "task2": ("check_environs.sh", check_task2),
    "task3": ("find_fraud.sh", check_task3),
    "task4": ("ban_manager.sh", check_task4),
    "task5": ("report.sh", check_task5),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-tests", action="store_true",
                        help="Создать tests_dump/ со всеми тестовыми "
                             "данными и ожиданиями (без запуска скриптов)")
    parser.add_argument("--task", choices=list(CHECKS.keys()),
                        help="Прогнать только одну задачу")
    args = parser.parse_args()

    if args.dump_tests:
        dump_all_tests()
        return

    if FAILED_DIR.exists():
        shutil.rmtree(FAILED_DIR)

    print("=== ТЕСТИРОВАНИЕ ===")
    print(f"Папка: {ROOT}\n")

    tasks = [args.task] if args.task else list(CHECKS.keys())
    passed = 0
    for name in tasks:
        script_name, check = CHECKS[name]
        print(f"--- {name} ({script_name}) ---")
        try:
            ok, msg = check()
        except Exception as e:
            ok, msg = False, f"внутренняя ошибка: {e!r}"
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"{status}: {msg}\n")
        if ok:
            passed += 1

    print(f"=== ИТОГ: {passed}/{len(tasks)} ===")
    if FAILED_DIR.exists():
        print(f"\nДанные упавших тестов сохранены в: {FAILED_DIR}")
        print("Загляни туда, чтобы понять, что пошло не так.")


if __name__ == "__main__":
    main()
