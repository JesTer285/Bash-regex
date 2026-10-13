#!/usr/bin/env bash

LOCKDIR="/tmp/report.lock"

if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "Report in progress" >&2
    exit 1
fi

catch_signals() {
    echo "Reporting was interrupted" >&2
    rmdir "$LOCKDIR" 2>/dev/null
    rm -f report.txt
    exit 1
}

trap 'catch_signals' SIGINT SIGTERM

show_help() {
    echo "Creates a Minecraft server report from log files."
    echo ""
    echo "Options:"
    echo "  -p, --players FILE       Path to players.txt"
    echo "  -b, --banlist FILE       Path to banlist.txt"
    echo "  -t, --transactions FILE  Path to transactions.txt"
    echo "  --help                   Show this help message"
    rmdir "$LOCKDIR" 2>/dev/null
    exit 0
}

players() {
    PLAYERS_COUNT=$(sort "$1" | uniq | wc -l)
}

banlist() {
    BANNED_COUNT=$(sort "$1" | uniq | wc -l)
}

transactions() {
    TRANSACTIONS_COUNT=$(wc -l < "$1")
    MOST_POPULAR=$(awk '
    {
        count[$5]+=1
    }
    END {
        mx = 0
        best_item = "NULL"
        for (item in count) {
            if ( mx < count[item] ) {
                mx = count[item]
                best_item = item
            }
        }
        print best_item
    }' "$1")
}

ARGS=$(getopt -o hp:b:t: --long help,players:,banlist:,transactions: -- "$@")

eval set -- "$ARGS"

while (( $# > 0 )); do
    case "$1" in
        -h | --help)
            show_help
            shift
            ;;
        -p | --players)
            players "$2"
            shift 2
            ;;
        -b | --banlist)
            banlist "$2"
            shift 2
            ;;
        -t | --transactions)
            transactions "$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown command. Use -h for help."
            shift
            ;;
    esac
done


cat << TEXT > report.txt
Minecraft server report

Players: "$PLAYERS_COUNT"
Bans: "$BANNED_COUNT"
Transactions: "$TRANSACTIONS_COUNT"
Top item: "$MOST_POPULAR"
TEXT

rmdir "$LOCKDIR" 2>/dev/null
