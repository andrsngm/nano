#!/bin/bash

cd /ruta/hacia/tu/carpeta/Nano

git pull origin main

docker-compose up -d --build

docker image prune -f
