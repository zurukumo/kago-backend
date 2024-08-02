#!/bin/bash
set -e

# docker起動処理
sudo docker compose -f docker-compose.production.yml down
sudo docker compose -f docker-compose.production.yml build
sudo docker compose -f docker-compose.production.yml up
