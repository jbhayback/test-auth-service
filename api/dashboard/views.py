import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.views import View

from rest_framework import status

User = get_user_model()

class ProcessLoginView(View):
    def get(self, request):
        if checkSessionExist(request):
            return redirect('/dashboard')
        else:
            return render(request, 'login.html')

    def post(self, request):
        url = 'http://localhost:8000/api/login'
        payload = {"username":request.POST.get("username"),"password": request.POST.get("password")}
        responsedata = requests.post(url, data=payload)

        if responsedata.status_code == status.HTTP_200_OK:
            data = responsedata.json()
            request.session['token'] = data.get("token")
            request.session['username'] = data.get("username")
            request.session['userid'] = data.get("userid")
            return redirect('/dashboard')   
        else:
            message = {}
            message['error_message'] = construct_message(responsedata)
            return render(request, "login.html", message)

class DashBoardView(View):
    def get(self, request):
        if checkSessionExist(request):
            permissions = self._getUserRolesPermissions(request)
            context = {}
            context['permissions'] = permissions
            return render(request, 'dashboard.html', context)
        else:
            return redirect('/login')
    

    def _getUserRolesPermissions(self, request):
        userid = request.session.get("userid")
        url = f"http://localhost:8000/api/users/{userid}/roles"
        headers={'Content-Type':'application/x-www-form-urlencoded', 'Authorization':f"Token {request.session.get('token').get('auth_token')}"}
        responsedata = requests.get(url, headers=headers)
        if responsedata.status_code == status.HTTP_200_OK:
            data = responsedata.json()
            return self._getUserPermissions(data)
        return []

    @staticmethod
    def _getUserPermissions(data):
        permissions = [Permission.objects.filter(group__id=id) for id in data.values()]
        if permissions:  
            return [list(permission.values())[0] for permission in permissions]

        return []

class UserLogoutView(View):
    def get(self, request):
        return redirect('/login')

    def post(self, request):
        if checkSessionExist(request):
            del request.session['token']
            del request.session['username']
            del request.session['userid']

        return redirect('/login')

class UserSignUpView(View): 
    def get(self, request):
        if checkSessionExist(request):
            return redirect('/dashboard')
        return render(request, 'signup.html')
    
    def post(self, request):
        url = 'http://localhost:8000/api/signup'
        payload = {"username":request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password")}
        responsedata = requests.post(url, data=payload)
        message = {}
        if responsedata.status_code == status.HTTP_201_CREATED:
            message['success_message'] = "Registration Successful! You may now login."
        else:
            message['error_message'] = construct_message(responsedata)
        return render(request, 'signup.html', message)

def construct_message(responsedata):
    messages = ""
    for k,v in responsedata.json().items():
        messages += f" {k}: {v}"
    return messages

def checkSessionExist(request):
    return request.session.get("userid") != None
