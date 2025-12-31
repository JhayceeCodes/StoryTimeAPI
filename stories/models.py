from django.db import models
from accounts.models import Author, User

class Story(models.Model):
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='stories')
    title = models.CharField(250)
    GENRE_CHOICES = (
        ('mystery', 'Mystery'), 
        ('fiction', 'Fiction'),
        ('comedy', 'Comedy'),
        ('others', 'Others'),
    )
    genre = models.CharField(max_length=7, choices=GENRE_CHOICES)
    content = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

class Reaction(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'), 
        ('dislike', 'Dislike'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="reactions")
    reaction = models.CharField(max_length=7, choices=REACTION_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "story"],
                name="unique_user_story_reaction"
            )
        ]


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alias = models.CharField(max_length=50, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="reviews")
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.alias:
            self.alias = self.user.username
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields=["story", "alias"],
            name="unique_alias_per_story"
            ),
            models.UniqueConstraint(
                fields=["user", "story"],
                name="unique_review_per_user_per_story"
            )
        
        ]

        ordering = ["-created_at"]