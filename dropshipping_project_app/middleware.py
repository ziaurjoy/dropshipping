from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

class SessionRedisCachingMiddleware(MiddlewareMixin):
    """
    Middleware to cache API GET responses per user session using Redis.
    Invalidates the user's cached API responses on state-changing requests (POST, PUT, PATCH, DELETE).
    """

    def process_request(self, request):
        # Only cache GET requests to the API endpoints
        if request.method == 'GET' and request.path.startswith('/api/'):
            user = request.user
            if user and user.is_authenticated:
                query_str = request.META.get('QUERY_STRING', '')
                cache_key = f"user_cache:{user.id}:{request.path}:{query_str}"
                
                try:
                    cached_response = cache.get(cache_key)
                    if cached_response is not None:
                        return cached_response
                except Exception:
                    pass

    def process_response(self, request, response):
        user = request.user
        if user and user.is_authenticated:
            # If it's a GET request and successful, cache the response in Redis
            if request.method == 'GET' and request.path.startswith('/api/') and response.status_code == 200:
                query_str = request.META.get('QUERY_STRING', '')
                cache_key = f"user_cache:{user.id}:{request.path}:{query_str}"
                try:
                    # Cache for 10 minutes (600 seconds)
                    cache.set(cache_key, response, 600)
                except Exception:
                    pass
            
            # If it's a modifying request, invalidate all cache keys for this user
            elif request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                if response.status_code in [200, 201, 204, 302]:
                    try:
                        # Clear all cached API responses for this user
                        cache.delete_pattern(f"user_cache:{user.id}:*")
                    except Exception:
                        pass
                        
        return response
