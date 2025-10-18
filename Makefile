.PHONY: dev build up down clean

dev:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f