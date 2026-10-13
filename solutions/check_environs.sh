#!/usr/bin/env bash

> server.conf

if [[ (-v SERVER_NAME) ]]; then
    echo "SERVER_NAME=$SERVER_NAME" >> server.conf
else
    echo "SERVER_NAME=\"StarCraft\"" >> server.conf
fi


if [[ (-v MAX_PLAYERS) ]]; then
    echo "MAX_PLAYERS=$MAX_PLAYERS" >> server.conf
else
    echo "MAX_PLAYERS=125" >> server.conf
fi

if [[ (-v SPAWN_COORDS) ]]; then
    echo "SPAWN_COORDS=$SPAWN_COORDS" >> server.conf
else
    echo "SPAWN_COORDS=\"274 67 -249\"" >> server.conf
fi

cat server.conf
