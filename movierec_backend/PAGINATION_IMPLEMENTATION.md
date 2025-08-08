# Pagination Implementation Guide

## 🎯 Strategy Overview

This implementation uses a **hybrid approach** that works optimally with TMDB API's existing pagination system while providing consistent pagination for our database queries.

### **Why This Approach?**

1. **TMDB API Already Has Pagination:** TMDB returns paginated results with `page`, `total_pages`, `total_results`
2. **We Pass Through TMDB Pagination:** Instead of re-paginating, we use TMDB's pagination and format it consistently
3. **Global Settings for Database Queries:** For endpoints that query our database (like favorites)
4. **Consistent Response Format:** Standardize how we present pagination data

## 📁 Files Modified

### **1. Settings Configuration**
- **File:** `movierec_backend/movierec_backend/settings.py`
- **Changes:** Added global pagination settings to `REST_FRAMEWORK`

### **2. Custom Pagination Classes**
- **File:** `movierec_backend/utils/pagination.py` (NEW)
- **Features:** 
  - `TMDbPagination`: Handles TMDB API responses
  - `StandardPagination`: Handles database queries

### **3. TMDB Client Enhancement**
- **File:** `movierec_backend/utils/tmdb_client.py`
- **Changes:** Added `page` parameter to all methods that support pagination

### **4. Movie Views Enhancement**
- **File:** `movierec_backend/movies/views.py`
- **Changes:** Updated all views to use `TMDbPagination`

### **5. User Views Enhancement**
- **File:** `movierec_backend/users/views.py`
- **Changes:** Updated `FavoriteMovieListView` to use `StandardPagination`

## 🔧 How It Works

### **TMDB API Pagination Flow**

```
Client Request: GET /api/movies/trending/?page=2&time_window=day
    ↓
Our API: Extracts page parameter
    ↓
TMDB API: GET /trending/movie/day?page=2&api_key=xxx
    ↓
TMDB Response: { page: 2, total_pages: 500, total_results: 10000, results: [...] }
    ↓
Our Pagination Class: Formats response with consistent metadata
    ↓
Client Response: { success: true, data: [...], pagination: {...} }
```

### **Database Query Pagination Flow**

```
Client Request: GET /api/users/favorites/?page=2&page_size=10
    ↓
Django ORM: Queries database with LIMIT/OFFSET
    ↓
Our Pagination Class: Formats response with consistent metadata
    ↓
Client Response: { success: true, data: [...], pagination: {...} }
```

## 📊 Response Format

### **TMDB API Endpoints**
```json
{
    "success": true,
    "data": [
        {
            "id": 123,
            "title": "Movie Title",
            "overview": "...",
            "poster_path": "/path/to/poster.jpg"
        }
    ],
    "pagination": {
        "count": 10000,
        "next": "http://localhost:8000/api/movies/trending/?page=3&time_window=day",
        "previous": "http://localhost:8000/api/movies/trending/?page=1&time_window=day",
        "current_page": 2,
        "total_pages": 500,
        "page_size": 20
    }
}
```

### **Database Query Endpoints**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "tmdb_id": 123,
            "title": "Movie Title",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "pagination": {
        "count": 150,
        "next": "http://localhost:8000/api/users/favorites/?page=3&page_size=20",
        "previous": "http://localhost:8000/api/users/favorites/?page=1&page_size=20",
        "current_page": 2,
        "total_pages": 8,
        "page_size": 20
    }
}
```

## 🎯 Endpoints with Pagination

### **TMDB API Endpoints (TMDbPagination)**
1. **`GET /api/movies/trending/`**
   - Parameters: `page`, `time_window`
   - TMDB pagination: Yes
   - Caching: Page 1 only

2. **`GET /api/movies/search/`**
   - Parameters: `query`, `page`
   - TMDB pagination: Yes
   - Caching: None (search results vary)

3. **`GET /api/movies/popular/`**
   - Parameters: `page`
   - TMDB pagination: Yes
   - Caching: None (popular changes frequently)

4. **`GET /api/movies/{id}/recommendations/`**
   - Parameters: `page`
   - TMDB pagination: Yes
   - Caching: Page 1 only

### **Database Query Endpoints (StandardPagination)**
1. **`GET /api/users/favorites/`**
   - Parameters: `page`, `page_size`
   - Database pagination: Yes
   - Ordering: Most recent first

## ⚙️ Configuration

### **Global Settings**
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### **Custom Pagination Classes**
```python
# For TMDB API responses
pagination_class = TMDbPagination

# For database queries
pagination_class = StandardPagination
```

## 🔍 Query Parameters

### **TMDB API Endpoints**
- `page`: Page number (default: 1, min: 1)
- `time_window`: For trending movies ('day' or 'week')

### **Database Query Endpoints**
- `page`: Page number (default: 1, min: 1)
- `page_size`: Items per page (default: 20, max: 100)

## 🚀 Benefits

### **Performance**
- ✅ Faster response times for large datasets
- ✅ Reduced memory usage
- ✅ Better server performance

### **User Experience**
- ✅ Better navigation through large result sets
- ✅ Consistent pagination across all endpoints
- ✅ Clear pagination metadata

### **Developer Experience**
- ✅ Automatic Swagger documentation
- ✅ Consistent response format
- ✅ Easy to implement and maintain

### **Scalability**
- ✅ Handles growing datasets efficiently
- ✅ Works with TMDB's existing pagination
- ✅ No breaking changes to existing API

## 🧪 Testing

### **Test URLs**
```bash
# TMDB API endpoints
GET /api/movies/trending/?page=2&time_window=day
GET /api/movies/search/?query=batman&page=3
GET /api/movies/popular/?page=1
GET /api/movies/123/recommendations/?page=2

# Database endpoints
GET /api/users/favorites/?page=2&page_size=10
```

### **Expected Behavior**
- All endpoints return consistent pagination format
- TMDB endpoints respect TMDB's pagination limits
- Database endpoints support customizable page sizes
- Error handling for invalid page numbers

## 🔄 Caching Strategy

### **TMDB API Caching**
- **Page 1 only:** Cache first page of trending movies and recommendations
- **Other pages:** Always fetch from TMDB API
- **Reason:** TMDB controls pagination, we can't cache all pages efficiently

### **Database Caching**
- **User favorites:** No caching (real-time data)
- **Cache invalidation:** When favorites are added/removed

## 📈 Future Enhancements

### **Possible Improvements**
1. **Cursor-based pagination** for better performance
2. **Infinite scroll support** with `next_cursor` tokens
3. **Custom page sizes** for different endpoints
4. **Pagination metadata** in response headers

### **Monitoring**
1. **Pagination usage analytics**
2. **Performance metrics** for different page sizes
3. **Error tracking** for invalid pagination requests

## 🎉 Summary

This implementation provides:
- **Optimal TMDB integration** by using their pagination system
- **Consistent user experience** across all endpoints
- **Performance benefits** for large datasets
- **Easy maintenance** with clear separation of concerns
- **Future-proof design** that can be extended as needed

The hybrid approach ensures we get the best of both worlds: TMDB's efficient pagination and our consistent API design. 