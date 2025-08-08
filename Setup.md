# 🎬 Movie Recommendation Backend - Setup Guide

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (configured on your server)
- TMDB API Key

## 🚀 Quick Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd movie-recommendation-backend

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

### 3. Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Django Settings
SECRET_KEY=django-insecure-c40*m0-68t(s-o-8t##lzhj^=dyp(mx#37a_!c!3(+u!2hlfk0
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (PostgreSQL)
DB_NAME=movie_recommendation_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# TMDB API Configuration
TMDB_API_KEY=your_tmdb_api_key_here
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb movie_recommendation_db

# Run migrations
cd movierec_backend
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 5. Get TMDB API Key

1. Go to [TMDB](https://www.themoviedb.org/)
2. Create an account
3. Go to Settings → API
4. Request an API key
5. Add the API key to your `.env` file

### 6. Run the Server

```bash
# Start the development server
python manage.py runserver

# The API will be available at:
# http://localhost:8000/api/
```

## 🔧 Configuration Details

### Database Configuration
- **Engine**: PostgreSQL
- **Default Port**: 5432
- **Database Name**: `movie_recommendation_db` (configurable)

### Redis Configuration
- **Host**: localhost
- **Port**: 6379
- **Password**: your_password
- **Database**: 0

### Cache Configuration
- **Trending Movies**: 1 hour TTL
- **Movie Recommendations**: 1 hour TTL
- **User Info**: 15 minutes TTL

## 📡 API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/refresh/` - Refresh token

### User Management
- `GET /api/users/profile/` - Get user info (cached)
- `GET /api/users/favorites/` - List user favorites
- `POST /api/users/favorites/add/` - Add favorite movie
- `DELETE /api/users/favorites/<id>/remove/` - Remove favorite
- `GET /api/users/favorites/check/<tmdb_id>/` - Check if movie is favorite

### Movies
- `GET /api/movies/trending/` - Get trending movies (cached)
- `GET /api/movies/search/` - Search movies
- `GET /api/movies/<id>/` - Get movie details
- `GET /api/movies/<id>/recommendations/` - Get recommendations (cached)
- `GET /api/movies/popular/` - Get popular movies

### Cache Management (Admin Only)
- `GET /api/utils/cache/` - Get cache statistics
- `DELETE /api/utils/cache/` - Clear all caches

## 🧪 Testing with Postman

### 1. Register a User
```http
POST http://localhost:8000/api/users/register/
Content-Type: application/json

{
    "username": "testuser",
    "email": "test@example.com",
    "password": "your_password123"
}
```

### 2. Login
```http
POST http://localhost:8000/api/users/login/
Content-Type: application/json

{
    "username": "testuser",
    "password": "your_password123"
}
```

### 3. Use Protected Endpoints
```http
GET http://localhost:8000/api/movies/trending/
Authorization: Bearer <your_access_token>
```

## 🔍 Monitoring

### Cache Statistics
```http
GET http://localhost:8000/api/utils/cache/
Authorization: Bearer <admin_token>
```

### Logs
- Console logs: Real-time in terminal
- File logs: `movierec_backend/logs/api.log`

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Redis Connection Error**
   - Check Redis server is accessible
   - Verify Redis credentials in `.env`
   - Test connection: `redis-cli -h serverIP||localhost -p 6380 -a yourpassword`

3. **TMDB API Error**
   - Verify TMDB_API_KEY in `.env`
   - Check API key is valid
   - Ensure internet connection

4. **Migration Errors**
   - Run `python manage.py makemigrations`
   - Then `python manage.py migrate`

### Development Commands

```bash
# Check Django configuration
python manage.py check

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [TMDB API Documentation](https://developers.themoviedb.org/3)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `movierec_backend/logs/api.log`
3. Check cache statistics via `/api/utils/cache/` endpoint 