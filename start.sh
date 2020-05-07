#!/bin/bash
docker-compose down --volumes --rmi all
docker-compose up --force-recreate -d
docker network connect bridge full_app
docker network connect bridge full_db_postgres