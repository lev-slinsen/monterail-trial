run:
	docker-compose up --build

stop:
	docker-compose stop

shell:
	docker-compose run --rm appserver python manage.py shell

superuser:
	docker-compose run --rm appserver python manage.py createsuperuser

migrations:
	docker-compose run --rm appserver python manage.py makemigrations

migrate:
	docker-compose run --rm appserver python manage.py migrate

test:
	docker-compose run --rm appserver python manage.py test
