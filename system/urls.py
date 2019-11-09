"""system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views import static

from system.features.game import TakePartInGameView, GamesView, GameInfoView, PlayGameView, PlayGameLevelView, \
    FinishGameView
from system.features.teams import MyTeamView, CreateTeamView, InviteToTeamView, DeleteInvitationView, \
    AcceptInvitationView
from system.views import auth_logout, HomeView, SetLangView, RegisterView, ProfileView

urlpatterns = [
    url(r'^$', login_required(HomeView.as_view()), name="home"),

    url(r'^user/(?P<team_id>\d+)/info/$', login_required(HomeView.as_view()), name="user"),

    url(r'^my/team/$', login_required(MyTeamView.as_view()), name="my_team"),
    url(r'^team/new/$', login_required(CreateTeamView.as_view()), name="create_team"),
    url(r'^team/(?P<team_id>\d+)/info/$', login_required(HomeView.as_view()), name="team"),
    url(r'^team/(?P<team_id>\d+)/invite/$', login_required(InviteToTeamView.as_view()), name="invite_to_team"),
    url(r'^team/delete_invite/(?P<id>\d+)/$', login_required(DeleteInvitationView.as_view()), name="delete_invite"),
    url(r'^team/accept_invite/(?P<id>\d+)/$', login_required(AcceptInvitationView.as_view()), name="accept_invite"),

    url(r'^games/$', login_required(GamesView.as_view()), name="games"),
    url(r'^game/(?P<game_id>\d+)/info/$', login_required(GameInfoView.as_view()), name="game_info"),
    url(r'^game/(?P<game_id>\d+)/take_part/$', login_required(TakePartInGameView.as_view()), name="take_part_in_game"),
    url(r'^game/(?P<game_id>\d+)/play/$', login_required(PlayGameView.as_view()), name="play_game"),
    url(r'^game/(?P<game_id>\d+)/level/(?P<level>\d+)/play/$', login_required(PlayGameLevelView.as_view()),
        name="play_level"),
    url(r'^game/(?P<game_id>\d+)/finish/$', login_required(FinishGameView.as_view()),name="finish_game"),

    url(r'^accounts/login/', auth_views.login, name="my_login"),
    url(r'^accounts/logout/$', auth_logout, name="logout"),
    url(r'^accounts/profile/$', ProfileView.as_view(), name="profile"),
    url(r'^accounts/register/$', RegisterView.as_view(), name="register"),
    url(r'^set_language/$', SetLangView.as_view(), name='set_language'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}),
]




