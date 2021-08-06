import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views import View

from rest_framework import status

User = get_user_model()

# Helper functions
def construct_message(response_data):
    messages = ""
    for k,v in response_data.json().items():
        messages += f" {k}: {v}"
    return messages

def check_session_if_exists(request):
    return request.session.get("userid") != None


class ProcessLoginView(View):
    def get(self, request):
        if check_session_if_exists(request):
            return redirect('/dashboard')
        else:
            return render(request, 'login.html')

    def post(self, request):
        url = 'http://localhost:8000/api/login'
        payload = {"username":request.POST.get("username"),"password": request.POST.get("password")}
        response_data = requests.post(url, data=payload)

        if response_data.status_code == status.HTTP_200_OK:
            data = response_data.json()
            request.session['token'] = data.get("token")
            request.session['username'] = data.get("username")
            request.session['userid'] = data.get("userid")
            return redirect('/dashboard')
        else:
            message = {}
            message['error_message'] = construct_message(response_data)
            return render(request, "login.html", message)

class DashBoardView(View):
    def get(self, request):
        if check_session_if_exists(request):
            permissions = self._get_user_roles_permissions(request)
            context = {}
            context['permissions'] = permissions
            return render(request, 'dashboard.html', context)
        else:
            return redirect('/login')

    def _get_user_roles_permissions(self, request):
        userid = request.session.get("userid")
        url = f"http://localhost:8000/api/users/{userid}/roles"
        headers={'Content-Type':'application/x-www-form-urlencoded', 'Authorization':f"Token {request.session.get('token').get('auth_token')}"}
        response_data = requests.get(url, headers=headers)
        if response_data.status_code == status.HTTP_200_OK:
            data = response_data.json()
            return self._get_user_permissions(data)
        return []

    @staticmethod
    def _get_user_permissions(data):
        permissions = [Permission.objects.filter(group__id=id) for id in data.values()]
        if permissions:
            return [list(permission.values())[0] for permission in permissions]

        return []

class UserLogoutView(View):
    def get(self, request):
        return redirect('/login')

    def post(self, request):
        if check_session_if_exists(request):
            del request.session['token']
            del request.session['username']
            del request.session['userid']

        return redirect('/login')

class UserSignUpView(View):
    def get(self, request):
        if check_session_if_exists(request):
            return redirect('/dashboard')
        return render(request, 'signup.html')

    def post(self, request):
        url = 'http://localhost:8000/api/signup'
        payload = {"username":request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password")}
        response_data = requests.post(url, data=payload)
        message = {}
        if response_data.status_code == status.HTTP_201_CREATED:
            message['success_message'] = "Registration Successful! You may now login."
        else:
            message['error_message'] = construct_message(response_data)
        return render(request, 'signup.html', message)
