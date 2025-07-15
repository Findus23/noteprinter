from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from notes.models import APIToken


class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            return
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Token "):
            return
        key = auth.split(" ", 1)[1]

        CACHE_PREFIX = "api_token_userid_"
        CACHE_TTL = 60 * 60 * 24

        cache_key = f"{CACHE_PREFIX}{key}"
        user = cache.get(cache_key)
        if user is None:
            try:
                token = APIToken.objects.select_related("user").get(key=key)
                user = token.user
            except APIToken.DoesNotExist:
                return JsonResponse({"detail": "Invalid token"}, status=401)
            cache.set(cache_key, user, CACHE_TTL)
        request.user = user


@database_sync_to_async
def _get_user_by_token(key):
    try:
        token = APIToken.objects.select_related("user").get(key=key)
        return token.user
    except APIToken.DoesNotExist:
        return None


class TokenAuthMiddlewareAsync(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Copy scope to stop changes going upstream
        scope = dict(scope)
        # Run the inner application along with the scope
        if scope.get("user") and scope["user"].is_authenticated:
            return await self.inner(scope, receive, send)
        headers = {name.decode().lower(): value.decode()
                   for name, value in scope.get("headers", [])}

        auth = headers.get("authorization", "")
        if auth.startswith("Token "):
            key = auth.split(" ", 1)[1]

            CACHE_PREFIX = "api_token_userid_"
            CACHE_TTL = 60 * 60 * 24

            cache_key = f"{CACHE_PREFIX}{key}"
            user = cache.get(cache_key)
            if user is None:
                user = await _get_user_by_token(key)
                if user:
                    cache.set(cache_key, user, CACHE_TTL)

            if user:
                scope["user"] = user

                cache.set(cache_key, user, CACHE_TTL)

        return await self.inner(scope, receive, send)
