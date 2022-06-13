#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


python manage.py migrate
python manage.py runserver_plus --print-sql --keep-meta-shutdown ${HOST}:${PORT}
