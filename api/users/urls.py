from django.urls import path
from .views import UserPermissionsView, UserRolesView


urlpatterns = [
    path('<uuid:id>/permissions', UserPermissionsView.as_view(), name='user_specific_permissions'),
    path('<uuid:id>/roles', UserRolesView.as_view(), name='user_specific_roles'),
]
