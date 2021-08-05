from django.urls import path
from .views import (SignUpView, LoginView, LogoutView, PermissionsView, RolesView)


urlpatterns = [
    path('signup', SignUpView.as_view(), name='user_signup'),
    path('login', LoginView.as_view(), name='user_login'),
    path('logout', LogoutView.as_view(), name='user_logout'),
    path('permissions', PermissionsView.as_view(), name='user_permissions'),
    path('roles', RolesView.as_view(), name='user_roles'),
]
