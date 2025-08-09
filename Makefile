.PHONY: help build up down logs clean restart shell migrate superuser collectstatic test production

# Default target
help:
	@echo "Available commands:"
	@echo "  build        - Build Docker images"
	@echo "  up           - Start development services"
	@echo "  down         - Stop all services"
	@echo "  logs         - View logs for all services"
	@echo "  restart      - Restart all services"
	@echo "  shell        - Open Django shell"
	@echo "  migrate      - Run database migrations"
	@echo "  superuser    - Create Django superuser"
	@echo "  collectstatic- Collect static files"
	@echo "  test         - Run tests"
	@echo "  production   - Start production services"
	@echo "  clean        - Remove all containers and volumes"
	@echo "  backup       - Backup database"
	@echo "  restore      - Restore database from backup"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

shell:
	docker-compose exec web python manage.py shell

migrate:
	docker-compose exec web python manage.py migrate

superuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

test:
	docker-compose exec web python manage.py test

# Production commands
production:
	docker-compose -f docker-compose.prod.yml up -d

production-down:
	docker-compose -f docker-compose.prod.yml down

production-logs:
	docker-compose -f docker-compose.prod.yml logs -f

production-shell:
	docker-compose -f docker-compose.prod.yml exec web python manage.py shell

production-migrate:
	docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

production-collectstatic:
	docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Utility commands
clean:
	docker-compose down -v --remove-orphans
	docker system prune -a -f

backup:
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U postgres movie_recommendation_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created successfully!"

restore:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore file=backup_filename.sql"; \
		exit 1; \
	fi
	@echo "Restoring database from $(file)..."
	docker-compose exec -T db psql -U postgres movie_recommendation_db < $(file)
	@echo "Database restored successfully!"

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health/ || echo "Health check failed"
	@docker-compose ps

# Setup commands
setup:
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp docker.env.example .env; \
		echo "Created .env file from template. Please edit it with your configuration."; \
	else \
		echo ".env file already exists."; \
	fi
	@echo "Building and starting services..."
	@make build
	@make up
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running migrations..."
	@make migrate
	@echo "Setup complete! Access your app at http://localhost:8000"

# Quick development restart
dev:
	@echo "Quick development restart..."
	@make down
	@make up
	@echo "Services restarted!"
