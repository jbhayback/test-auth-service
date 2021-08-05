from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.exceptions import PermissionDenied

from djoser import utils, signals
from djoser.conf import settings

from config import exceptions
from . import serializers

User = get_user_model()


class AuthApiListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def aggregate_urlpattern_names():
        from . import urls
        urlpattern_names = [pattern.name for pattern in urls.urlpatterns]

        return urlpattern_names

    @staticmethod
    def get_urls_map(request, urlpattern_names, fmt):
        urls_map = {}
        for urlpattern_name in urlpattern_names:
            try:
                url = reverse(urlpattern_name, request=request, format=fmt)
            except NoReverseMatch:
                url = ''
            urls_map[urlpattern_name] = url
        return urls_map

    def get(self, request, fmt=None):
        urlpattern_names = self.aggregate_urlpattern_names()
        urls_map = self.get_urls_map(request, urlpattern_names, fmt)
        return Response(urls_map)


class SignUpView(generics.CreateAPIView):
    serializer_class = serializers.SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        signals.user_registered.send(sender=self.__class__, user=user,
                                     request=self.request)

class LoginView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = [permissions.AllowAny]

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = serializers.TokenSerializer
        data = {"token":token_serializer_class(token).data, 
            "userid":serializer.user.id,
            "username": serializer.user.username
        }
        return Response(data = data)


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def delete(request):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionsView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = serializers.CreatePermissionsSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(User(is_superuser=True).get_all_permissions())

    def _action(self, serializer):
        codename = serializer.data['codename']
        name = serializer.data['name']

        try:
            content_type = ContentType.objects.get_for_model(User)
            permission = Permission.objects.create(codename=codename,
                                                name=name,
                                                content_type=content_type)
        except IntegrityError:
            raise exceptions.AlreadyExists(
                _('The permission already exists.'))
        except ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExists(
                 _(f'No content_type with app_label={app_label} and/or model={model} exists.'))

        content = {"message": f"Permission {codename} successfully created."}

        return Response(data=content, status=status.HTTP_201_CREATED)

class RolesView(utils.ActionViewMixin, generics.GenericAPIView):
    serializer_class = serializers.CreateRolesSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({group.name: group.id for group in Group.objects.all()})

    def _action(self, serializer):
        codename = serializer.data['permission_codename']
        role_name = serializer.data['role_name']

        try:
            permission = Permission.objects.get(codename=codename)
            group = Group.objects.create(name=role_name)
            group.permissions.add(permission)

        except IntegrityError:
            raise exceptions.AlreadyExists(
                _('The role already exists.'))
        except ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExists(
                 _(f'No permission with codename={codename} exists.'))

        content = {"message": f"{role_name} successfully created."}

        return Response(data=content, status=status.HTTP_201_CREATED)

