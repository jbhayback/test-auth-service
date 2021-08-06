from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
from users.models import User


class AuthTest(APITestCase):
    def setUp(self):
        self.base_url = 'http://localhost:8000/api'
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_superuser('admin@admin.com', 'admin1234')
        self.token = Token.objects.create(user=self.user)

        # Set Credentials
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_user(self):
        url = f'{self.base_url}/signup'
        data =  {'username': 'test', 'email': 'test@gmail.com', 'password': 'test1234test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email='test@gmail.com').email, 'test@gmail.com')

    def test_create_user_invalid_password(self):
        url = f'{self.base_url}/signup'
        data =  {'username': 'test', 'email': 'test@gmail.com', 'password': 'test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_user_invalid_email(self):
        url = f'{self.base_url}/signup'
        data =  {'username': 'test', 'email': 'test@gmail', 'password': 'test1234test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_login(self):
        url = f'{self.base_url}/login'
        data =  {'username': 'admin@admin.com', 'password': 'admin1234'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_invalid_credentials(self):
        url = f'{self.base_url}/login'
        data =  {'username': 'test1', 'password': 'test1234tesv'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_retrieve_permissions(self):
        url = f'{self.base_url}/permissions'
        response = self.client.get(url, format='json')

        expected_available_permissions = {'sites.change_site', 'admin.change_logentry', 'auth.add_permission',
            'auth.delete_group', 'auth.change_permission', 'authtoken.delete_token', 'authtoken.view_token',
            'sites.add_site', 'contenttypes.change_contenttype', 'contenttypes.delete_contenttype',
            'admin.delete_logentry', 'sessions.delete_session', 'auth.change_group', 'users.add_user',
            'auth.delete_permission', 'admin.add_logentry', 'authtoken.add_token', 'authtoken.change_token',
            'admin.view_logentry', 'users.change_user', 'sessions.change_session', 'sessions.view_session',
            'sites.delete_site', 'auth.view_group', 'sites.view_site', 'auth.add_group', 'users.view_user',
            'contenttypes.view_contenttype', 'contenttypes.add_contenttype', 'auth.view_permission',
            'sessions.add_session', 'users.delete_user'}

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_available_permissions)


    def test_create_permission(self):
        url = f'{self.base_url}/permissions'
        data = {'codename': 'can_dance', 'name': 'Can dance'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if newly created permission is in the expected available permissions
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('users.can_dance' in response.data)

    def test_create_permission_invalid_paramters(self):
        url = f'{self.base_url}/permissions'
        data = {'codena': 'can_dance', 'name': 'Can dance'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_retrieve_roles(self):
        url = f'{self.base_url}/roles'
        response = self.client.get(url, format='json')
        expected_roles = {}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_roles)


    def test_retrieve_roles_invalid_credentials(self):
        url = f'{self.base_url}/roles'
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + '3cc256f101034a3e70b3a74c0cb3f23cbf814fc3')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_roles(self):
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if newly created role can be retieved
        response = self.client.get(url, format='json')
        expected_created_role = {'SysAdmin': 4}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_created_role)


    def test_add_role_to_user(self):
        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{self.user.id}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response_1 = self.client.post(url_1, data_1)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)


    def test_add_non_existent_role_to_user(self):
        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{self.user.id}/roles'
        data_1 = {'roles': 'NormalUser'}
        response_1 = self.client.post(url_1, data_1)
        self.assertEqual(response_1.status_code, status.HTTP_409_CONFLICT)


    def test_retrieve_specific_user_roles(self):
        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{self.user.id}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response = self.client.post(url_1, data_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve user roles
        url_2 = f'{self.base_url}/users/{self.user.id}/roles'
        response = self.client.get(url_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_retrieve_specific_user_permissions(self):
        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to user
        url_1 = f'{self.base_url}/users/{self.user.id}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response = self.client.post(url_1, data_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve user permissions
        url_2 = f'{self.base_url}/users/{self.user.id}/permissions'
        data = {'permission_ids': '1,24,3,29'}
        response = self.client.post(url_2, data)
        expected_user_permissions = {'1': False, '24': True, '3': False, '29': True}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_user_permissions)


    def test_retrieve_specific_user_permissions_without_providing_permission_ids(self):
        # Retrieve user permissions
        url = f'{self.base_url}/users/{self.user.id}/permissions'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_add_role_to_user_without_providing_roles(self):
        # Assign roles to users
        url_ = f'{self.base_url}/users/{self.user.id}/roles'
        response_ = self.client.post(url_)
        self.assertEqual(response_.status_code, status.HTTP_400_BAD_REQUEST)
