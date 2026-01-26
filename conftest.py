import pytest, uuid
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Author
from stories.models import Story

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
        'password': 'super:_@#TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def create_user(db):
    """Fixture to create a user"""

    def make_user(**kwargs):
        defaults = {
            "username": f"user_{uuid.uuid4().hex[:8]}",
            "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
            "password": "strong--_:TestPass123!",
        }
        defaults.update(kwargs)

        return User.objects.create_user(**defaults)

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

@pytest.fixture
def story_data():
    return {
        "title": "The New Story",
        "content": "The package arrived on a quiet Tuesday morning..." * 3,
        "genre": "mystery",
    }



@pytest.fixture
def author(create_user, db):
    """Create a user with an author profile"""
    user = create_user(username='author', email='author@example.com', is_verified=True)
    author = Author.objects.create(user=user, pen_name='Satoshi')
    return user, author



@pytest.fixture
def create_story_api(api_client, author):
    user, _ = author
    def _create(payload):
        api_client.force_authenticate(user=user)
        return api_client.post(
            reverse("story-list"),
            payload,
            format="json",
        )
    return _create






