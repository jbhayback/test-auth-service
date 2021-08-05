import re

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework import exceptions as drf_exceptions

from djoser import utils
from djoser.conf import settings
from config import exceptions

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            'email',
            'password',
        )

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            messages = [_(message) for message in e.messages]

            raise serializers.ValidationError({'password': messages})

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise exceptions.AlreadyExists(
                _('The provided email address already has an account.'))

        return user

    @staticmethod
    def perform_create(validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            user.is_active = True
            user.save(update_fields=['is_active'])
        return user


class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ('auth_token', )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user_account = self._get_user_by_username(username)
        if not user_account:
            raise drf_exceptions.AuthenticationFailed(
                _('Unable to login with the provided credentials.'))

        self.user = authenticate(username=username, password=password)
        if not self.user:
            if user_account.is_active:
                raise drf_exceptions.AuthenticationFailed(
                    _('Unable to login with the provided credentials.'))

        return attrs

    @staticmethod
    def _get_user_by_username(username):
        if username and re.search(r'[^@\s]+@[^@\s]+\.[^@\s]+', username):
            username_field = 'email'
        else:
            username_field = 'username'

        user = User.objects.filter(**{
            username_field + '__iexact': username
        }).first()

        return user


class CreatePermissionsSerializer(serializers.Serializer):
    codename = serializers.CharField()
    name = serializers.CharField()


class CreateRolesSerializer(serializers.Serializer):
    permission_codename = serializers.CharField()
    role_name = serializers.CharField()
