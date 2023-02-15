from django.conf.global_settings import LANGUAGE_COOKIE_NAME
from django.shortcuts import redirect


def lang_view(request, lang):
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie(LANGUAGE_COOKIE_NAME, lang)
    return response
