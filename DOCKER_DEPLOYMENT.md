# Docker Deployment Guide for Movie Recommendation Backend

This guide provides step-by-step instructions for deploying your Django movie recommendation backend using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned
- TMDB API key (for movie data)

## Quick Start (Development)

### 1. Environment Setup

```bash
# Copy the environment template
cp docker.env.example .env

# Edit .env file with your configuration
nano .env
```

**Required environment variables:**
- `SECRET_KEY`: Django secret key
- `DB_PASSWORD`: PostgreSQL password
- `REDIS_PASSWORD`: Redis password
- `TMDB_API_KEY`: Your TMDB API key

### 2. Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Database Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Access Your Application

- **Django App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Production Deployment

### 1. Production Environment

```bash
# Use production docker-compose file
cp docker.env.example .env
# Edit .env with production values
nano .env
```

### 2. SSL Certificate Setup

```bash
# Create SSL directory
mkdir ssl

# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem

# For production, use Let's Encrypt or your CA
```

### 3. Production Deployment

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Production Database Setup

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## Service Management

### Common Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ data loss)
docker-compose down -v

# Restart specific service
docker-compose restart web

# View service logs
docker-compose logs web

# Execute commands in running container
docker-compose exec web python manage.py shell
docker-compose exec db psql -U postgres -d movie_recommendation_db
```

### Health Checks

```bash
# Check service health
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health/
```

## Monitoring and Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
docker-compose logs -f redis
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Database connections
docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Redis memory usage
docker-compose exec redis redis-cli -a $REDIS_PASSWORD info memory
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 5432, 6379, 80, 443 are available
2. **Permission errors**: Check file ownership and Docker user permissions
3. **Database connection**: Verify PostgreSQL is running and credentials are correct
4. **Redis connection**: Check Redis password and connection settings

### Debug Commands

```bash
# Check container status
docker-compose ps

# Inspect container
docker-compose exec web env
docker-compose exec web python manage.py check

# Database connection test
docker-compose exec web python manage.py dbshell

# Redis connection test
docker-compose exec web python -c "import redis; r = redis.Redis(host='redis', port=6379, password='your_password'); print(r.ping())"
```

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v --remove-orphans

# Remove all images
docker system prune -a

# Rebuild from scratch
docker-compose up --build -d
```

## Security Considerations

### Production Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use HTTPS with valid SSL certificates
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Regular security updates

### Environment Variables

Never commit `.env` files to version control. Use `.env.example` as a template.

## Scaling

### Horizontal Scaling

```bash
# Scale web service
docker-compose up -d --scale web=3

# Load balancer configuration needed for multiple web instances
```

### Resource Limits

Add resource constraints in docker-compose files:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U postgres movie_recommendation_db > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres movie_recommendation_db < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v movie-recommendation-backend_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v movie-recommendation-backend_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## Support

For issues and questions:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check service health: `docker-compose ps`
4. Review this documentation

## Next Steps

- Set up CI/CD pipeline
- Configure monitoring (Prometheus, Grafana)
- Set up automated backups
- Implement logging aggregation
- Configure load balancing for high availability
