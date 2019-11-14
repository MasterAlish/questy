# coding=utf-8
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import translation
from django.views.generic import TemplateView
from django.utils import timezone
from system.forms import RegistrationForm
from system.models import UserDetails, Game


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
        # type: (object) -> object
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
        games_in_progress = Game.objects.filter(active=True, status="started")
        games_in_future = Game.objects.filter(active=True, status="not_started")
        six_hours_ago = timezone.now() - timedelta(hours=6)
        just_finished_games = Game.objects.filter(Q(status="finished") | Q(status="scoring")).filter(
            finishes_at__gt=six_hours_ago, active=True)
        return render(request, self.template_name, {
            'games_in_progress': games_in_progress,
            'games_in_future': games_in_future,
            'just_finished_games': just_finished_games
        })


class RegisterView(BaseView):
    template_name = "registration/register.html"

    def dispatch(self, request, *args, **kwargs):
        form = RegistrationForm()
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                self.save_details(form)
                messages.success(request, u"Вы успешно прошли регистрацию! Войдите используя свой аккаунт")
                return redirect(reverse("my_login"))

        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def save_details(self, form):
        form.instance.set_password(form.cleaned_data['password'])
        form.instance.save()
        details = UserDetails(user=form.instance)
        details.sex = form.cleaned_data["sex"]
        if "phone_number" in form.cleaned_data:
            details.phone_number = form.cleaned_data["phone_number"]
        if "weight" in form.cleaned_data:
            details.weight = form.cleaned_data["weight"]
        if "height" in form.cleaned_data:
            details.height = form.cleaned_data["height"]
        details.save()


class ProfileView(BaseView):
    template_name = "registration/profile.html"


class SetLangView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        old_lang = translation.get_language()
        lang = request.GET.get("language", None)
        if lang in ['ru', 'en']:
            translation.activate(lang)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
            request.LANGUAGE_CODE = translation.get_language()
        return redirect("/")

