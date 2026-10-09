#!/usr/bin/env bash

format () {
    sort -u "$1" -o "$1"
}

add () {
    if [ -s ban_list.txt ] && grep -q "$1" ban_list.txt; then
        echo "This user already banned"
    else
        echo "$1" "$2" "$3" >> ban_list.txt
    fi
}

info () {
    cat ban_list.txt | grep "$1" | sort -u
}

remove () {
    sed -i "/$1/d" ban_list.txt
}

sort_file () { # Removes duplicates in addition to sorting
    if [ "$1" = "--name" ]; then
        sort -u -k1 "$2" -o "$2"
    elif [ "$1" = "--time" ]; then
        sort -u -k2 "$2" -o "$2"
    fi
}

case "$1" in
    add)
        add $2 $3 $4
        ;;
    format)
        format $2
        ;;
    info)
        info $2
        ;;
    remove)
        remove $2
        ;;
    sort_file)
        sort_file $2 $3
        ;;
esac
