import pytest
from .models import Story

@pytest.mark.django_db
class TestStories:
    def test_fetch_story(self):
        stories = Story.objects.all()
        assert stories == {}
