from rest_framework import serializers

class CreateUserRolesSerializer(serializers.Serializer):
    roles = serializers.ListField(
        child = serializers.CharField()
    )

class CreateUserPermissionsSerializer(serializers.Serializer):
    permission_ids = serializers.ListField(
        child = serializers.IntegerField()
    )
