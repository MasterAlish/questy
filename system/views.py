# coding=utf-8

from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils import translation
from django.views.generic import TemplateView


def auth_logout(request):
    logout(request)
    return redirect(reverse("home"))


class HasPermMixin(object):
    required_permissions = []

    @staticmethod
    def has_perms(permissions, user):
        for permission in permissions:
            if not user.has_perm(permission):
                return False
        return True

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(HasPermMixin, cls).as_view(**initkwargs)
        if not isinstance(cls.required_permissions, list):
            raise Exception("required_permissions must be list of permissions")

        actual_decorator = user_passes_test(
            lambda u: HasPermMixin.has_perms(cls.required_permissions, u),
            login_url="/"
        )

        return actual_decorator(view)


class BaseView(HasPermMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        return super(BaseView, self).dispatch(request, *args, **kwargs)


class HomeView(BaseView):
    template_name = "home.html"

    def dispatch(self, request, *args, **kwargs):

        return super(HomeView, self).dispatch(request, *args, **kwargs)


class SetLangView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        old_lang = translation.get_language()
        lang = request.GET.get("language", None)
        if lang in ['ru', 'en']:
            translation.activate(lang)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
            request.LANGUAGE_CODE = translation.get_language()
        return redirect("/")

