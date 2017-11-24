import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.test import APITestCase, APIRequestFactory, APIClient

from TooPath3.constants import DEFAULT_ERROR_MESSAGES
from TooPath3.models import CustomUser
from TooPath3.users.views import *

# DATA CONSTANTS
from TooPath3.utils import create_user_with_email, generate_token_for_testing

VALID_DATA_USER = {
    "username": "test",
    "email": "test@test.com",
    "password": "password"
}
INVALID_DATA_USER = {
    "username": "test"
}
VALID_DATA_LOGIN = {
    "username": "test",
    "password": "test"
}
INVALID_DATA_LOGIN = {
    "user": "test",
    "pssword": "test"
}
DATA_LOGIN_NO_PASSWORD = {
    "username": "test"
}
DATA_LOGIN_NO_USERNAME = {
    "password": "test"
}


class GetUserCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user_with_email('user@gmail.com')
        self.token = generate_token_for_testing(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

    def test_return_404_status_when_user_not_exists(self):
        response = self.client.get(path='/users/100/')
        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)

    def test_return_403_status_when_user_is_not_self(self):
        new_user = create_user_with_email('user2@gmail.com')
        response = self.client.get(path='/users/' + str(new_user.pk) + '/')
        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_return_401_status_when_user_is_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.get(path='/users/1/')
        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_return_200_status_when_get_user_is_done(self):
        response = self.client.get(path='/users/' + str(self.user.pk) + '/')
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_return_json_with_user_info_status_when_get_user_is_done(self):
        response = self.client.get(path='/users/' + str(self.user.pk) + '/')
        self.assertEqual(PublicCustomUserSerializer(instance=self.user).data, response.data)


class PostUser(APITestCase):
    """
    POST /users
    """

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_given_non_existing_users__when_post_users__with_username_email_and_password__then_return_created(self):
        response = self.client.post('/users/', VALID_DATA_USER, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_given_non_existing_users__when_post_users__with_username_email_and_password__then_user_is_created(self):
        self.client.post('/users/', VALID_DATA_USER, format='json')
        user = CustomUser.objects.get(username='test')
        self.assertEqual(user.email, 'test@test.com')

    def test_given_non_existing_users__when_post_users__with_invalid_username_email_or_password__then_return_bad_request(
            self):
        response = self.client.post('/users/', INVALID_DATA_USER, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_given_non_existing_users__when_post_users__with_username_email_and_password__then_return_token(self):
        response = self.client.post('/users/', VALID_DATA_USER, format='json')
        self.assertIsNotNone(response.data['token'])


class PatchUserCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user_with_email('user_test')
        self.token = generate_token_for_testing(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + self.token)

    def test_return_404_status_when_user_not_exists(self):
        response = self.client.patch(path='/users/100/', data={})
        self.assertEqual(HTTP_404_NOT_FOUND, response.status_code)

    def test_return_403_status_when_user_is_not_self(self):
        new_user = create_user_with_email('user2@gmail.com')
        response = self.client.patch(path='/users/' + str(new_user.pk) + '/', data={})
        self.assertEqual(HTTP_403_FORBIDDEN, response.status_code)

    def test_return_401_status_when_user_is_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='')
        response = self.client.patch(path='/users/1/', data={})
        self.assertEqual(HTTP_401_UNAUTHORIZED, response.status_code)

    def test_return_400_status_when_json_body_is_invalid(self):
        json_data = {'name': 'test', 'last_name': 'refactor'}
        response = self.client.patch(path='/users/' + str(self.user.pk) + '/', data=json_data)
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)

    def test_return_error_message_status_when_try_to_modify_instance_representation(self):
        json_data = {'email': 'newtest@gmail.com'}
        response = self.client.patch(path='/users/' + str(self.user.pk) + '/', data=json_data)
        expected_error = {'non_field_errors': [DEFAULT_ERROR_MESSAGES['invalid_patch']]}
        self.assertEqual(expected_error, response.data)

    def test_return_200_status_when_user_is_patched(self):
        json_data = {'first_name': 'test', 'last_name': 'refactor'}
        response = self.client.patch(path='/users/' + str(self.user.pk) + '/', data=json_data)
        self.assertEqual(HTTP_200_OK, response.status_code)

    def test_return_json_with_user_info_status_when_get_user_is_done(self):
        json_data = {'first_name': 'test', 'last_name': 'refactor'}
        response = self.client.patch(path='/users/' + str(self.user.pk) + '/', data=json_data)
        user_updated = CustomUser.objects.get(pk=self.user.pk)
        self.assertEqual(PublicCustomUserSerializer(instance=user_updated).data, response.data)


class LoginTest(APITestCase):
    """
    POST /login
    """

    class PayloadObject:
        def __init__(self, username, pk):
            self.username = username
            self.pk = pk

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create(username="test", email='test@test.com', password=make_password('test'))

    def test_given_existing_user__when_post_login__with_valid_username_and_password__then_return_ok(self):
        response = self.client.post('/login/', VALID_DATA_LOGIN, format='json')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_given_existing_user__when_post_login__with_valid_username_and_password__then_return_token(self):
        response = self.client.post('/login/', VALID_DATA_LOGIN, format='json')
        self.assertIsNotNone(response.data['token'])

    def test_given_existing_user__when_post_login__with_invalid_username_or_password__then_return_bad_request(self):
        response = self.client.post('/login/', INVALID_DATA_LOGIN, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_given_existing_user__when_post_login__with_no_password__then_return_password_needed_error(self):
        response = self.client.post('/login/', DATA_LOGIN_NO_PASSWORD, format='json')
        self.assertEqual(response.data['password'], ['This field is required.'])

    def test_given_existing_user__when_post_login__with_no_username__then_return_username_needed_error(self):
        response = self.client.post('/login/', DATA_LOGIN_NO_USERNAME, format='json')
        self.assertEqual(response.data['username'], ['This field is required.'])

    def test_given_existing_user__when_post_verify_token__with_generated_token__then_return_ok_status(self):
        user_jwt_secret = str(self.user.jwt_secret)
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        payload_object = LoginTest.PayloadObject(self.user.username, self.user.pk)
        payload = jwt_payload_handler(payload_object)
        token = jwt.encode(
            payload,
            user_jwt_secret,
            api_settings.JWT_ALGORITHM
        ).decode('utf-8')
        response = self.client.post('/api-token-verify/', {"token": token}, format='json')
        self.assertEqual(response.status_code, HTTP_200_OK)
