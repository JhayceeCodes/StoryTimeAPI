from re import search
from django.core.cache import cache
import pytest
from django.urls import reverse
from rest_framework import status
from .models import Story



@pytest.mark.django_db
class TestStoryViewset:
    def test_create_story_success(self, create_story_api, story_data):
        response = create_story_api(story_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Story.objects.filter(title=story_data["title"]).exists()

    @pytest.mark.parametrize("payload", [
        {"title": "Tu", "content": "Valid content" * 5, "genre": "fiction"},
        {"title": "Valid title", "content": "Too short", "genre": "fiction"},
        {"title": "Valid title", "content": "Valid content" * 5, "genre": "invalid"},
    ])
    def test_create_story_invalid_data(self, create_story_api, payload):
        response = create_story_api(payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_create_story_unauthorized(self, api_client, story_data):
        """Test unauthorized story creation"""
        url = reverse('story-list')

        response = api_client.post(url, story_data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_stories_authenticated(self, authenticated_client):
        """Test anyone can list stories"""
        url = reverse('story-list')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_stories_unauthenticated(self, api_client):
        """Test anyone can list published stories"""
        url = reverse('story-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_stories_ordering(self, create_story_api, api_client, story_data):
        cache.clear()

        create_story_api({"title": "Story A", "content": story_data["content"], "genre": story_data["genre"]})
        create_story_api({"title": "Story B", "content": story_data["content"], "genre": story_data["genre"]})
        create_story_api({"title": "Story C", "content": story_data["content"], "genre": story_data["genre"]})

        response = api_client.get(reverse("story-list"))
        titles = [s["title"] for s in response.data["results"]]
        print(response.data)  #run pytest -s to see
        assert titles == ["Story C", "Story B", "Story A"]
        assert response.status_code == status.HTTP_200_OK

    def test_stories_search(self, create_story_api, api_client, story_data):
        cache.clear()

        create_story_api({"title": "The Genius", "content": story_data["content"], "genre": story_data["genre"]})
        create_story_api({"title": "Jungle", "content": story_data["content"], "genre": story_data["genre"]})

        response1 = api_client.get(reverse("story-list"), data={"search": "StoryA"}, format="json") #PS: Search isn't exact
        response2 = api_client.get(reverse("story-list"), data={"search": "Jungle"}, format="json")

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK

        titles1 = [s["title"] for s in response1.data["results"]]
        titles2 = [s["title"] for s in response2.data["results"]]

        assert titles1 == []
        assert titles2 == ["Jungle"]










