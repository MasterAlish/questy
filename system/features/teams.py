# coding=utf-8
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from system.forms import TeamForm
from system.models import UserDetails, Invitation, Team, TeamInGame
from system.views import BaseView


class BaseTeamView(BaseView):
    def assert_user_is_cap(self, team):
        if not self.user_is_cap(team):
            raise Http404()

    def assert_user_can_delete_invite(self, invitation):
        if not self.user_is_cap(invitation.team) and invitation.user_id != self.request.user.id:
            raise Http404()

    def user_is_cap(self, team):
        user_details = UserDetails.of(self.request.user)
        return team == user_details.current_team and user_details.is_cap


class MyTeamView(BaseView):
    template_name = "teams/team.html"

    def dispatch(self, request, *args, **kwargs):
        user_details = UserDetails.of(request.user)

        context = {
            'team': user_details.current_team,
            'invitations': request.user.invitations.all()
        }
        return render(request, self.template_name, context)


class TeamView(BaseView):
    template_name = "teams/team.html"

    def dispatch(self, request, *args, **kwargs):
        team = Team.objects.get(pk=kwargs["team_id"])

        context = {
            'team': team
        }
        return render(request, self.template_name, context)


class UserView(BaseView):
    template_name = "registration/profile.html"

    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs["user_id"])
        details = UserDetails.of(user)

        context = {
            'user': user,
            'details': details
        }
        return render(request, self.template_name, context)


class CreateTeamView(BaseView):
    template_name = "teams/team_form.html"

    def dispatch(self, request, *args, **kwargs):
        form = TeamForm()
        if request.method == 'POST':
            form = TeamForm(request.POST)
            if form.is_valid():
                form.instance.created_by = request.user
                form.save()
                self.check_current_team(request.user, form.instance)
                return redirect(reverse("my_team"))
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def check_current_team(self, user, team):
        user_details = UserDetails.of(user)
        if not user_details.current_team:
            user_details.current_team = team
            user_details.is_cap = True
            user_details.save()


class InviteToTeamView(BaseTeamView):
    template_name = "teams/invitation.html"

    def dispatch(self, request, *args, **kwargs):
        team = Team.objects.get(pk=kwargs['team_id'])
        self.assert_user_is_cap(team)

        context = {
            'team': team
        }
        if request.method == "POST":
            if "search" in request.POST:
                keyword = request.POST.get("keyword", "")
                member_user_ids = map(lambda m: m[0], team.members.values_list("user_id"))
                context["keyword"] = keyword
                context["search_result"] = True
                context["users"] = User.objects.filter(Q(username=keyword) |
                                                       Q(username__icontains=keyword) |
                                                       Q(first_name__icontains=keyword) |
                                                       Q(last_name__icontains=keyword))\
                    .exclude(pk=request.user.id) \
                    .exclude(pk__in=member_user_ids)
            elif "invite" in request.POST:
                active_games = self.get_active_games_of(team)
                if active_games:
                    messages.error(request, u"Во время игры нельзя приглашать участников в команду")
                    return redirect(reverse("my_team"))
                else:
                    user_id = request.POST.get("user", "")
                    try:
                        user = User.objects.get(pk=user_id)
                        invitation, created = Invitation.objects.get_or_create(team=team, user=user)
                        if created:
                            messages.success(request, u"Приглашение успешно отправлено")
                        else:
                            messages.warning(request, u"Участник уже приглашен")
                        return redirect(reverse("my_team"))
                    except Exception as e:
                        return redirect(reverse("my_team"))

        return render(request, self.template_name, context)

    def get_active_games_of(self, team):
        return TeamInGame.objects.filter(team=team, game__status="started").count()


class DeleteInvitationView(BaseTeamView):
    template_name = "teams/invitation.html"

    def dispatch(self, request, *args, **kwargs):
        invitation = Invitation.objects.get(pk=kwargs['id'])
        self.assert_user_can_delete_invite(invitation)
        invitation.delete()
        messages.success(request, u"Приглашение успешно удалено")
        return redirect(reverse("my_team"))


class AcceptInvitationView(BaseTeamView):
    template_name = "teams/invitation.html"

    def dispatch(self, request, *args, **kwargs):
        invitation = Invitation.objects.get(pk=kwargs['id'])
        if invitation.user_id != request.user.id:
            raise Http404()
        user_details = UserDetails.of(request.user)
        old_team = user_details.current_team

        active_games = self.get_active_games_of(invitation.team)
        if active_games:
            messages.error(request, u"Во время игры команды нельзя принимать приглашения")
        else:
            user_details.current_team = invitation.team
            user_details.is_cap = False
            user_details.save()
            invitation.delete()

            self.validate_team_cap(old_team)
            self.validate_team_cap(user_details.current_team)

            messages.success(request, u"Вы теперь в составе команды %s" % user_details.current_team.name)
        return redirect(reverse("my_team"))

    def validate_team_cap(self, team):
        if team and not team.members.filter(is_cap=True).exists():
            if team.members.all().exists():
                new_cap = team.members.first()
                new_cap.is_cap = True

    def get_active_games_of(self, team):
        return TeamInGame.objects.filter(team=team, game__status="started").count()
