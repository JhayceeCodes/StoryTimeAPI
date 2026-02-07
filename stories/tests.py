from re import search
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import pytest, time
from django.urls import reverse
from rest_framework import status
from .models import Story, Review, Reaction, Rating



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

    def test_put_method_not_allowed(self, api_client, author, create_story, story_data):
        """Test PUT method is not allowed (should use PATCH)"""
        user, author = author
        story = create_story(author=author)
        api_client.force_authenticate(user=user)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        data = {'title': 'Updated', 'content': story_data["content"]}

        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_own_story(self, api_client, author, create_story):
        """Test author can delete their own story"""
        user, author = author
        story = create_story(author=author)
        api_client.force_authenticate(user=user)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Story.objects.filter(pk=story.pk).exists()

    def test_moderator_can_delete_story(self, api_client, moderator, create_story):
        """Test moderator can delete any story"""
        story = create_story(author=moderator.author)
        api_client.force_authenticate(user=moderator)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Story.objects.filter(pk=story.pk).exists()

    def test_cannot_delete_others_story(self, api_client, another_author, create_story, author):
        """Test regular user cannot delete another user's story"""
        _, author = author
        story = create_story(author=author)
        api_client.force_authenticate(user=another_author)

        url = reverse('story-detail', kwargs={'pk': story.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Story.objects.filter(pk=story.pk).exists()


@pytest.mark.django_db
class TestReactionView:

    def test_add_reaction(self, api_client, author, create_story, reaction_url):
        user, author_profile = author
        story = create_story(author=author_profile)

        api_client.force_authenticate(user=user)
        response = api_client.post(
            reaction_url(story.id),
            {"reaction": "like"},
            format="json"
        )

        story.refresh_from_db()

        assert response.status_code == status.HTTP_201_CREATED
        assert story.likes == 1

    def test_update_reaction(self, api_client, author, create_story, reaction_url):
        user, author_profile = author
        story = create_story(author=author_profile)

        Reaction.objects.create(user=user, story=story, reaction="like")

        api_client.force_authenticate(user=user)
        response = api_client.patch(
            reaction_url(story.id),
            {"reaction": "dislike"},
            format="json"
        )

        story.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert story.likes == 0
        assert story.dislikes == 1

    def test_delete_reaction(self, api_client, author, create_story, reaction_url):
        user, author_profile = author
        story = create_story(author=author_profile)

        Reaction.objects.create(user=user, story=story, reaction="like")

        api_client.force_authenticate(user=user)
        response = api_client.delete(reaction_url(story.id))

        story.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert story.likes == 0


@pytest.mark.django_db
class TestReviewViewSet:

    def test_create_review(self, api_client, author, create_story, review_url, review_data):
        user, author_profile = author
        story = create_story(author=author_profile)

        api_client.force_authenticate(user=user)
        response = api_client.post(
            review_url(story.id),
            review_data,
            format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(story=story).exists()

    def test_update_review_within_30_minutes(self, api_client, author, create_story):
        user, author_profile = author
        story = create_story(author=author_profile)

        review = Review.objects.create(
            user=user,
            story=story,
            content="Old review"
        )

        api_client.force_authenticate(user=user)
        url = reverse("story-review-detail", kwargs={"story_pk": story.id, "pk": review.id})

        response = api_client.patch(url, {"content": "Updated"}, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_cannot_update_review_after_30_minutes(self, api_client, author, create_story):
        user, author_profile = author
        story = create_story(author=author_profile)

        review = Review.objects.create(
            user=user,
            story=story,
            content="Old review",
        )

        #forces created_at backwards
        Review.objects.filter(id=review.id).update(
            created_at=timezone.now() - timedelta(minutes=31)
        )

        api_client.force_authenticate(user=user)
        url = reverse("story-review-detail", kwargs={"story_pk": story.id, "pk": review.id})

        response = api_client.patch(url, {"content": "Updated"}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_not_allowed(self, api_client, author, create_story):
        user, author_profile = author
        story = create_story(author=author_profile)
        review = Review.objects.create(user=user, story=story, content="Test")

        api_client.force_authenticate(user=user)
        url = reverse("story-review-detail", kwargs={"story_pk": story.id, "pk": review.id})

        response = api_client.put(url, {"content": "Updated"}, format="json")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestRatingAPI:

    def test_author_cannot_rate_own_story(self, api_client, author, create_story, rating_url):
        user, author_profile = author
        story = create_story(author=author_profile)

        api_client.force_authenticate(user=user)
        response = api_client.post(
            rating_url(story.id),
            {"rating": 5},
            format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_rating(self, api_client, author, another_author, create_story, rating_url):
        _, author_profile = author
        story = create_story(author=author_profile)

        api_client.force_authenticate(user=another_author)
        response = api_client.post(
            rating_url(story.id),
            {"rating": 4},
            format="json"
        )

        story.refresh_from_db()

        assert response.status_code == status.HTTP_201_CREATED
        assert story.total_ratings == 1
        assert story.average_rating == 4

    def test_update_rating(self, api_client, author, another_author, create_story, rating_url):
        _, author_profile = author
        story = create_story(author=author_profile)

        Rating.objects.create(user=another_author, story=story, rating=2)

        api_client.force_authenticate(user=another_author)
        response = api_client.patch(
            rating_url(story.id),
            {"rating": 5},
            format="json"
        )

        story.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert story.average_rating == 5

    def test_delete_rating(self, api_client, author, another_author, create_story, rating_url):
        _, author_profile = author
        story = create_story(author=author_profile)

        Rating.objects.create(user=another_author, story=story, rating=3)

        api_client.force_authenticate(user=another_author)
        response = api_client.delete(rating_url(story.id))

        story.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert story.total_ratings == 0
