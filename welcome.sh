#!/usr/bin/env bash


if [[ "$1" =~ ^[0-9A-Za-z_]{3,16}$ ]]; then
	echo "Welcome, $1"
	exit 0
else
	echo "Invalid nickname" >&2
	exit 1
fi
