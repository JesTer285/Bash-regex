#!/usr/bin/env bash

awk '
{
    total[$1, $5] -= $4
    total[$3, $5] += $4
}
END {
    for (player in total) {
        if (total[player] < 0) {
            split(player, arr, SUBSEP)
            print arr[1]
        }
    }
}' "$1" | sort -u
