"""import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create_user(**kwargs):
        defaults = {
            "email": "user@example.com",
            "password": "StrongPass123!",
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    return _create_user


@pytest.fixture
def verified_user(create_user):
    user = create_user(email="verified@example.com", username="Satoshi")
    user.is_verified = True
    user.save()
    return user


@pytest.fixture
def unverified_user(create_user):
    return create_user(email="unverified@example.com", username="UnverifiedAnon")


@pytest.fixture
def authenticated_client(api_client, verified_user):
    api_client.force_authenticate(user=verified_user)
    return api_client
"""



import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client"""
    return APIClient()


@pytest.fixture
def user_data():
    """Fixture for user registration data"""
    return {
        'username': 'test_user',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def create_user(db):
    """Fixture to create a user"""
    def make_user(**kwargs):
        defaults = {
            'username': 'test_user',
            'email': 'test@example.com',
            'is_verified': False
        }
        defaults.update(kwargs)
        password = defaults.pop('password', 'TestPass123!')
        user = User.objects.create_user(**defaults)
        user.set_password(password)
        user.save()
        return user
    return make_user


@pytest.fixture
def verified_user(create_user):
    """Fixture for verified user"""
    return create_user(is_verified=True)


@pytest.fixture
def superuser(db):
    """Fixture for superuser"""
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!'
    )
    user.is_verified = True
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, verified_user):
    """Fixture for authenticated API client"""
    api_client.force_authenticate(user=verified_user)
    return api_client


@pytest.fixture
def tokens_for_user(verified_user):
    """Fixture to generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(verified_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }