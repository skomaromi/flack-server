#! /bin/bash

file=bin/activate
if [[ ! -f "$file" ]]; then
    echo "'$file' does not exist. Please run 'setup.sh' before starting server."
    exit 1
fi

source bin/activate
python src/manage.py runserver 0:8000
