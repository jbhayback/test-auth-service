from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from config import exceptions
from . import serializers

User = get_user_model()

class UserPermissionsView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.CreateUserPermissionsSerializer

    def post(self, request, id):
        permission_ids = request.POST.get('permission_ids')
        if not permission_ids:
            content = {"message": f"'permission_ids' field is required."}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=id)
        permissions = Permission.objects.filter(Q(user=user) | Q(group__user=user)).all()
        result = { p_id : False for p_id in permission_ids.split(',') }

        for permission in permissions:
            if str(permission.id) in permission_ids:
                result.update(
                    {
                        str(permission.id): True
                    }
                )

        return Response(data=result)

class UserRolesView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateUserRolesSerializer

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExists(
                _(f'No user with id={id} exists.'))

        return Response({role.name: role.id for role in user.groups.all()})

    def post(self, request, id):
        roles = request.POST.get('roles')
        print(request.POST)
        if not roles:
            content = {"message": f"'roles' field is required."}
            return Response(data=content, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=id)
            for role in roles.split(','):
                roles_obj = Group.objects.get(name=role)
                roles_obj.user_set.add(user)

        except IntegrityError:
            raise exceptions.AlreadyExists(
                _(f'{role} already assigned to user.'))
        except ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExists(
                _(f'No user with id={id} and/or no {role} role exists.'))

        content = {"message": f"{role} has been added to user."}
        return Response(data=content, status=status.HTTP_201_CREATED)
    