from re import search
from django.core.cache import cache
import pytest, time
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

    #TESTING CACHING
    # METHOD A --- Checking no. of database hit before and after(which should be zero) caching
    def test_stories_list_uses_cache(
            self,
            api_client,
            create_story_api,
            story_data,
            django_assert_num_queries,
    ):
        #cache.clear()

        create_story_api({"title": "Story A", **story_data})

        # First request ---  DB hit (hits both story and author table)
        with django_assert_num_queries(2):
            api_client.get(reverse("story-list"))

        # Second request --- cached (no DB hit)
        with django_assert_num_queries(0):
            api_client.get(reverse("story-list"))

    # METHOD B --- Checking time difference (Cache speed)
    def test_stories_list_faster_with_cache(self, api_client):
        #cache.clear()
        url = reverse("story-list")

        start = time.monotonic()
        api_client.get(url)
        first_time = time.monotonic() - start

        start = time.monotonic()
        api_client.get(url)
        second_time = time.monotonic() - start

        print(f"First: {first_time:.4f}s | Cached: {second_time:.4f}s") #confirm time difference
        assert second_time < first_time

    def test_update_own_story(self, api_client, author, create_story):
        """Test author can update their own story"""
        user, author = author
        story = create_story(author=author)
        api_client.force_authenticate(user=user)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        data = {'title': 'Updated Title'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        story.refresh_from_db()
        assert story.title == 'Updated Title'

    def test_cannot_update_others_story(self, api_client, author, another_author, create_story):
        """Test user cannot update another user's story"""
        _, author = author
        story = create_story(author=author)  # Created by default author
        api_client.force_authenticate(user=another_author)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        data = {'title': 'Hacked Title'}

        response = api_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
        story.refresh_from_db()
        assert story.title != 'Hacked Title'








