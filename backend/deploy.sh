#!/bin/bash
set -x
set -e

python="/srv/venv/noteprinter/bin/python"

manage="sudo -u noteprinter $python manage.py"

git pull

$manage collectstatic --noinput
$manage migrate

sudo systemctl restart noteprinter.service
sudo systemctl restart noteprinter-worker.service
