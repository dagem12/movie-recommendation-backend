from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TMDbPagination(PageNumberPagination):
    """
    Custom pagination for TMDB API responses.
    
    TMDB API already provides pagination data in their response:
    - page: current page
    - total_pages: total number of pages
    - total_results: total number of results
    - results: array of movies
    
    This pagination class extracts and formats this data consistently.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with TMDB-style pagination metadata.
        
        Args:
            data: The paginated data (usually from TMDB API)
            
        Returns:
            Response with pagination metadata
        """
        # If data is from TMDB API, extract their pagination info
        if isinstance(data, dict) and 'page' in data and 'total_pages' in data:
            # TMDB response format
            return Response({
                'success': True,
                'data': data.get('results', []),
                'pagination': {
                    'count': data.get('total_results', 0),
                    'next': self._get_next_url(data),
                    'previous': self._get_previous_url(data),
                    'current_page': data.get('page', 1),
                    'total_pages': data.get('total_pages', 1),
                    'page_size': data.get('results', []).__len__() if data.get('results') else 0
                }
            })
        else:
            # Standard pagination for database queries
            return Response({
                'success': True,
                'data': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                    'current_page': self.page.number,
                    'total_pages': self.page.paginator.num_pages,
                    'page_size': self.get_page_size(self.request)
                }
            })
    
    def _get_next_url(self, tmdb_data):
        """Generate next URL for TMDB pagination"""
        current_page = tmdb_data.get('page', 1)
        total_pages = tmdb_data.get('total_pages', 1)
        
        if current_page < total_pages:
            # Get the current request URL and update the page parameter
            request = getattr(self, 'request', None)
            if request:
                url = request.build_absolute_uri()
                if 'page=' in url:
                    return url.replace(f'page={current_page}', f'page={current_page + 1}')
                else:
                    separator = '&' if '?' in url else '?'
                    return f"{url}{separator}page={current_page + 1}"
        return None
    
    def _get_previous_url(self, tmdb_data):
        """Generate previous URL for TMDB pagination"""
        current_page = tmdb_data.get('page', 1)
        
        if current_page > 1:
            # Get the current request URL and update the page parameter
            request = getattr(self, 'request', None)
            if request:
                url = request.build_absolute_uri()
                if 'page=' in url:
                    return url.replace(f'page={current_page}', f'page={current_page - 1}')
                else:
                    separator = '&' if '?' in url else '?'
                    return f"{url}{separator}page={current_page - 1}"
        return None


class StandardPagination(PageNumberPagination):
    """
    Standard pagination for database queries.
    
    Used for endpoints that query our database (like user favorites).
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with consistent metadata.
        
        Args:
            data: The paginated data from database
            
        Returns:
            Response with pagination metadata
        """
        return Response({
            'success': True,
            'data': data,
            'pagination': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.get_page_size(self.request)
            }
        }) 