from functools import wraps

from django.http import HttpResponse


def require_authentification(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    return wrapper
