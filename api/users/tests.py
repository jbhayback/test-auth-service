from rest_framework import status
from rest_framework.test import APITestCase, RequestsClient, APIClient
from .models import User


class AuthTest(APITestCase):
    base_url = 'http://localhost:8000/api'
    api_client = APIClient()


    def create_multiple_users(self):
        url = f'{self.base_url}/signup'
        data_list =  [
            {'username': 'test1', 'email': 'test1@gmail.com', 'password': 'test1234test'},
            {'username': 'test2', 'email': 'test2@gmail.com', 'password': '!@#4aaaa'},
        ]

        user_ids = []
        for data in data_list:
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            user_ids.append(response.data['id'])

        return user_ids


    def test_create_user(self):
        url = f'{self.base_url}/signup'
        data =  {'username': 'test', 'email': 'test@gmail.com', 'password': 'test1234test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@gmail.com')
        self.assertEqual(User.objects.get().username, 'test')


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
        # Create User
        self.create_multiple_users()

        # Login
        url = f'{self.base_url}/login'
        data =  {'username': 'test1', 'password': 'test1234test'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_invalid_credentials(self):
        # Create User
        self.create_multiple_users()

        # Login
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

    def test_retrieve_roles(self):
        url = f'{self.base_url}/roles'
        response = self.client.get(url, format='json')
        expected_roles = {}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_roles)


    def test_create_roles(self):
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if newly created role can be retieved
        response = self.client.get(url, format='json')
        # expected_created_role = {'SysAdmin': 4}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(response.data, expected_created_role)


    def test_add_role_to_user(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{user_ids[0]}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response_1 = self.api_client.post(url_1, data_1)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        url_2 = f'{self.base_url}/users/{user_ids[1]}/roles'
        data_2 = {'roles': 'NormalUser'}
        response_2 = self.api_client.post(url_2, data_2)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)


    def test_add_non_existent_role_to_user(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{user_ids[0]}/roles'
        data_1 = {'roles': 'SysAdmin'}
        response_1 = self.api_client.post(url_1, data_1)
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)

        url_2 = f'{self.base_url}/users/{user_ids[1]}/roles'
        data_2 = {'roles': 'NormalUser'}
        response_2 = self.api_client.post(url_2, data_2)
        self.assertEqual(response_2.status_code, status.HTTP_409_CONFLICT)


    def test_retrieve_specific_user_roles(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to users
        url_1 = f'{self.base_url}/users/{user_ids[0]}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response = self.api_client.post(url_1, data_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve user roles
        url = f'{self.base_url}/users/{user_ids[0]}/roles'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_retrieve_specific_user_permissions(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Create roles
        url = f'{self.base_url}/roles'
        data = {'permission_codename': 'add_user', 'role_name': 'SysAdmin'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {'permission_codename': 'view_site', 'role_name': 'NormalUser'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assign roles to user
        url_1 = f'{self.base_url}/users/{user_ids[0]}/roles'
        data_1 = {'roles': 'SysAdmin,NormalUser'}
        response = self.api_client.post(url_1, data_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve user permissions
        url = f'{self.base_url}/users/{user_ids[0]}/permissions'
        data = {'permission_ids': '1,24,3,29'}
        response = self.api_client.post(url, data)
        expected_user_permissions = {'1': False, '24': True, '3': False, '29': True}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_user_permissions)


    def test_retrieve_specific_user_permissions_without_providing_permission_ids(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Retrieve user permissions
        url = f'{self.base_url}/users/{user_ids[0]}/permissions'
        response = self.api_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_add_role_to_user_without_providing_roles(self):
        # Create users
        user_ids = self.create_multiple_users()

        # Assign roles to users
        url_ = f'{self.base_url}/users/{user_ids[0]}/roles'
        response_ = self.api_client.post(url_)
        self.assertEqual(response_.status_code, status.HTTP_400_BAD_REQUEST)
