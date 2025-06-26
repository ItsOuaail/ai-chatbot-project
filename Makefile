.PHONY: build up down restart logs shell-backend shell-frontend migrate collectstatic test clean

# Build all services
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

# View logs for specific service
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

# Shell access
shell-backend:
	docker-compose exec backend python manage.py shell

shell-db:
	docker-compose exec db psql -U postgres -d chatbot_db

# Django management commands
migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

# Development commands
dev-up:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Testing
test:
	docker-compose exec backend python manage.py test

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Reset everything (be careful!)
reset:
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d
	docker-compose exec backend python manage.py migrate
	docker-compose exec backend python manage.py collectstatic --noinput