# coding=utf-8
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from system.forms import TeamForm
from system.models import UserDetails, Invitation, Team
from system.views import BaseView


class BaseTeamView(BaseView):
    def assert_user_is_cap(self, team):
        if team.captain_id != self.request.user.id:
            raise Http404()

    def assert_user_can_delete_invite(self, invitation):
        if invitation.team.captain_id != self.request.user.id and invitation.user_id != self.request.user.id:
            raise Http404()


class MyTeamView(BaseView):
    template_name = "teams/my_team.html"

    def dispatch(self, request, *args, **kwargs):
        user_details = UserDetails.of(request.user)

        context = {
            'team': user_details.current_team,
            'invitations': request.user.invitations.all()
        }
        return render(request, self.template_name, context)


class CreateTeamView(BaseView):
    template_name = "teams/team_form.html"

    def dispatch(self, request, *args, **kwargs):
        form = TeamForm()
        if request.method == 'POST':
            form = TeamForm(request.POST)
            if form.is_valid():
                form.instance.captain = request.user
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
                context["keyword"] = keyword
                context["search_result"] = True
                context["users"] = User.objects.filter(Q(username=keyword) | Q(username__icontains=keyword) |
                                                       Q(first_name__icontains=keyword) | Q(
                    last_name__icontains=keyword)
                                                       ).exclude(pk=request.user.id).exclude(pk__in=team.members.all())
            elif "invite" in request.POST:
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
        user_details.current_team = invitation.team
        user_details.save()
        invitation.delete()

        messages.success(request, u"Вы теперь в составе команды %s" % user_details.current_team.name)
        return redirect(reverse("my_team"))
