import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

User = get_user_model()

# Create your tests here.
@pytest.mark.django_db
class TestRegisterView:

    @patch('accounts.views.send_verification_email_task.delay')
    @patch('accounts.views.generate_token')
    def test_register_success(self, mock_generate_token, mock_send_email, api_client, user_data):
        """Test successful user registration"""
        mock_generate_token.return_value = ('test-uid', 'test-token')

        url = reverse('register')  # Adjust to your URL name
        response = api_client.post(url, user_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=user_data['email']).exists()

        user = User.objects.get(email=user_data['email'])
        assert user.username == user_data['username']
        assert not user.is_verified
        assert mock_send_email.called

    def test_register_duplicate_email(self, api_client, create_user, user_data):
        """Test registration with duplicate email"""
        create_user(email=user_data['email'])

        url = reverse('register')
        response = api_client.post(url, user_data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_register_invalid_password(self, api_client, user_data):
    #     """Test registration with weak password"""
    #     user_data['password'] = '123'
    #
    #     url = reverse('register')
    #     response = api_client.post(url, user_data, format='json')
    #
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields"""
        url = reverse('register')
        response = api_client.post(url, {'username': 'test_user'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestVerifyEmailView:

    @patch('accounts.views.verify_token')
    def test_verify_email_success(self, mock_verify_token, api_client, create_user):
        """Test successful email verification"""
        user = create_user(is_verified=False)
        mock_verify_token.return_value = user

        url = reverse('verify_email', kwargs={'uid': 'test-uid', 'token': 'test-token'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_verified

    @patch('accounts.views.verify_token')
    def test_verify_email_invalid_token(self, mock_verify_token, api_client):
        """Test email verification with invalid token"""
        mock_verify_token.return_value = None

        url = reverse('verify_email', kwargs={'uid': 'invalid-uid', 'token': 'invalid-token'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('accounts.views.verify_token')
    def test_verify_email_already_verified(self, mock_verify_token, api_client, verified_user):
        """Test verification of already verified email"""
        mock_verify_token.return_value = verified_user

        url = reverse('verify_email', kwargs={'uid': 'test-uid', 'token': 'test-token'})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'already verified' in response.data['detail'].lower()


@pytest.mark.django_db
class TestSendVerificationEmailView:

    @patch('accounts.views.send_verification_email_task.delay')
    @patch('accounts.views.generate_token')
    def test_send_verification_email_success(self, mock_generate_token, mock_send_email,
                                            api_client, create_user):
        """Test sending verification email to unverified user"""
        user = create_user(is_verified=False)
        api_client.force_authenticate(user=user)
        mock_generate_token.return_value = ('test-uid', 'test-token')

        url = reverse('resend_email')
        response = api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert mock_send_email.called

    def test_send_verification_email_already_verified(self, authenticated_client):
        """Test sending verification email when already verified"""
        url = reverse('resend_email')
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'already verified' in response.data['message'].lower()

    def test_send_verification_email_unauthenticated(self, api_client):
        """Test sending verification email without authentication"""
        url = reverse('resend_email')
        response = api_client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestRequestPasswordResetView:

    @patch('accounts.views.send_password_reset_email_task.delay')
    @patch('accounts.views.generate_token')
    def test_request_password_reset_success(self, mock_generate_token, mock_send_email,
                                           api_client, verified_user):
        """Test requesting password reset for existing user"""
        mock_generate_token.return_value = ('test-uid', 'test-token')

        url = reverse('request_password_reset')
        response = api_client.post(url, {'email': verified_user.email}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert mock_send_email.called

    def test_request_password_reset_nonexistent_user(self, api_client):
        """Test requesting password reset for non-existent user"""
        url = reverse('request_password_reset')
        response = api_client.post(url, {'email': 'nonexistent@example.com'}, format='json')

        # Should return 200 to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK

    def test_request_password_reset_missing_email(self, api_client):
        """Test requesting password reset without email"""
        url = reverse('request_password_reset')
        response = api_client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestPasswordResetConfirmView:

    @patch('accounts.views.verify_token')
    def test_password_reset_confirm_success(self, mock_verify_token, api_client, verified_user):
        """Test successful password reset"""
        mock_verify_token.return_value = verified_user

        url = reverse('confirm_password_reset', kwargs={'uid': 'test-uid', 'token': 'test-token'})
        response = api_client.post(url, {'password': 'NewPass123!'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        verified_user.refresh_from_db()
        assert verified_user.check_password('NewPass123!')

    @patch('accounts.views.verify_token')
    def test_password_reset_confirm_invalid_token(self, mock_verify_token, api_client):
        """Test password reset with invalid token"""
        mock_verify_token.return_value = None

        url = reverse('confirm_password_reset', kwargs={'uid': 'invalid', 'token': 'invalid'})
        response = api_client.post(url, {'password': 'NewPass123!'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('accounts.views.verify_token')
    def test_password_reset_confirm_weak_password(self, mock_verify_token, api_client, verified_user):
        """Test password reset with weak password"""
        mock_verify_token.return_value = verified_user

        url = reverse('confirm_password_reset', kwargs={'uid': 'test-uid', 'token': 'test-token'})
        response = api_client.post(url, {'password': '123'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('accounts.views.verify_token')
    def test_password_reset_confirm_missing_password(self, mock_verify_token, api_client, verified_user):
        """Test password reset without password"""
        mock_verify_token.return_value = verified_user

        url = reverse('confirm_password_reset', kwargs={'uid': 'test-uid', 'token': 'test-token'})
        response = api_client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestLoginView:

    def test_login_success(self, api_client, verified_user):
        """Test successful login"""
        url = reverse('login')
        response = api_client.post(url, {
            'username': verified_user.username,
            'password': 'TestPass123!'
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client, verified_user):
        """Test login with invalid credentials"""
        url = reverse('login')
        response = api_client.post(url, {
            'username': verified_user.username,
            'password': 'WrongPassword123!'
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unverified_user(self, api_client, create_user):
        """Test login with unverified user"""
        user = create_user(is_verified=False)

        url = reverse('login')
        response = api_client.post(url, {
            'email': user.email,
            'password': 'TestPass123!'
        }, format='json')

        # Depends on your LoginSerializer implementation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

@pytest.mark.django_db
class TestLogoutView:

    def test_logout_success(self, authenticated_client, tokens_for_user):
        """Test successful logout"""
        url = reverse('logout')
        response = authenticated_client.post(url, {
            'refresh': tokens_for_user['refresh']
        }, format='json')

        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_missing_token(self, authenticated_client):
        """Test logout without refresh token"""
        url = reverse('logout')
        response = authenticated_client.post(url, {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_invalid_token(self, authenticated_client):
        """Test logout with invalid token"""
        url = reverse('logout')
        response = authenticated_client.post(url, {
            'refresh': 'invalid-token'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client, tokens_for_user):
        """Test logout without authentication"""
        url = reverse('logout')
        response = api_client.post(url, {
            'refresh': tokens_for_user['refresh']
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestProfileView:

    def test_get_profile_success(self, authenticated_client, verified_user):
        """Test retrieving user profile"""
        url = reverse('profile')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == verified_user.email

    def test_update_profile_success(self, authenticated_client, verified_user):
        """Test updating user profile"""
        url = reverse('profile')
        response = authenticated_client.patch(url, {
            'username': 'Sam',
            'email': 'sam@user.com'
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        verified_user.refresh_from_db()
        assert verified_user.username == 'Sam'

    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile without authentication"""
        url = reverse('profile')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestUpdateUserRoleView:

    def test_update_role_to_admin_success(self, api_client, superuser, verified_user):
        """Test updating user role to admin"""
        api_client.force_authenticate(user=superuser)

        url = reverse('update_user_role')
        response = api_client.patch(url, {
            'user_id': verified_user.id,
            'role': 'admin'
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        verified_user.refresh_from_db()
        assert verified_user.role.lower() == 'admin'
        assert verified_user.is_staff

    def test_update_role_to_user_success(self, api_client, superuser, create_user):
        """Test updating admin role to regular user"""
        admin_user = create_user(role='admin', is_staff=True, is_verified=True)
        api_client.force_authenticate(user=superuser)

        url = reverse('update_user_role')
        response = api_client.patch(url, {
            'user_id': admin_user.id,
            'role': 'user'
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        admin_user.refresh_from_db()
        assert admin_user.role.lower() == 'user'
        assert not admin_user.is_staff

    def test_update_role_non_superuser(self, authenticated_client, create_user):
        """Test updating role without superuser permission"""
        target_user = create_user(username='target', email='target@example.com')

        url = reverse('update_user_role')
        response = authenticated_client.patch(url, {
            'user_id': target_user.id,
            'role': 'admin'
        }, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_role_unauthenticated(self, api_client, verified_user):
        """Test updating role without authentication"""
        url = reverse('update_user_role')
        response = api_client.patch(url, {
            'user_id': verified_user.id,
            'role': 'admin'
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED