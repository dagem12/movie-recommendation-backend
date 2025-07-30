# Movie Recommendation Backend

A real-world Django backend application providing movie recommendations using third-party APIs, JWT-based user authentication, Redis caching for high performance, and fully documented APIs for seamless frontend integration.

---

## Overview

This backend serves as the core engine for a movie recommendation app, supporting:

* Trending & personalized movie recommendations via **TMDb API**
* JWT-based user authentication
* Favorite movie management
* Redis caching for faster API responses
* Swagger API documentation

---

## Tech Stack

| Tool               | Purpose               |
| ------------------ | --------------------- |
| Django             | Backend web framework |
| PostgreSQL         | Relational database   |
| Redis              | Caching layer         |
| TMDb API           | Movie data source     |
| JWT (SimpleJWT)    | Authentication        |
| Swagger (drf-yasg) | API documentation     |

---

## Key Features

### Movie Recommendations

* Fetch **trending** and **recommended** movies from TMDb API
* Redis-based caching to reduce external API calls and boost speed
* Smart aggregation for recommendations based on user favorites

### User Authentication

* Register/login using **JWT tokens**
* Access protected endpoints via:

  ```
  Authorization: Bearer <your_token>
  ```

### User Favorites

* Save/remove favorite movies by TMDb ID
* Get list of saved movies
* Recommendations are personalized from favorites

### Performance Optimization

* Redis caches responses for:

  * Trending movies (global)
  * Personalized recommendations (per user)
* TTL: 1 hour (configurable)

### API Documentation

* Full Swagger docs generated via `drf-yasg`
* Available at: [**/api/docs**](http://localhost:8000/api/docs)

---

## Project Structure

```
movie-backend/
├── movies/               # Recommendation APIs and TMDb integration
├── users/                # Auth, favorites, user profile
├── core/                 # Project settings and root config
├── templates/            # Swagger UI customizations
├── manage.py
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/dagem12/movie-recommendation-backend.git
cd movie-recommendation-backend
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
TMDB_API_KEY=your_tmdb_key
DATABASE_URL=postgres://user:password@localhost:5432/yourdb
REDIS_URL=redis://localhost:6379
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Start Server

```bash
python manage.py runserver
```

---

## API Authentication

All protected routes require a JWT token:

```http
Authorization: Bearer <your_token>
```

Use the following endpoint to obtain a token:

```http
POST /api/token/
```

---

## Sample API Endpoints

| Endpoint                     | Method | Auth | Description                      |
| ---------------------------- | ------ | ---- | -------------------------------- |
| `/api/movies/trending/`      | GET    | ❌    | Get global trending movies       |
| `/api/movies/recommended/`   | GET    | ✅    | Get personalized recommendations |
| `/api/users/register/`       | POST   | ❌    | Register new user                |
| `/api/token/`                | POST   | ❌    | Get JWT token                    |
| `/api/users/favorites/`      | GET    | ✅    | List user’s favorites            |
| `/api/users/favorites/<id>/` | POST   | ✅    | Add/remove favorite movie        |
| `/api/docs/`                 | GET    | ❌    | Swagger API documentation        |

---

## Caching Strategy

| Data Type            | Key Format                       | TTL         |
| -------------------- | -------------------------------- | ----------- |
| Trending Movies      | `trending_movies`                | 1 hour      |
| User Recommendations | `user:{user_id}:recommendations` | 1 hour/user |

* Redis improves performance and reduces TMDb API traffic.
* Cached entries are refreshed automatically after expiration.

---

## Git Commit Workflow

| Prefix      | Description                             |
| ----------- | --------------------------------------- |
| `feat:`     | New feature (e.g. `feat: trending API`) |
| `fix:`      | Bug fix                                 |
| `perf:`     | Performance improvements                |
| `docs:`     | Documentation changes                   |
| `refactor:` | Code restructuring (no feature change)  |

---

## Deployment Options

* Docker-based deployment (recommended):
  * Nginx + Gunicorn
  * PostgreSQL + Redis


## License

This project is licensed under the MIT License.
See [`LICENSE`](./LICENSE) for more details.

---

