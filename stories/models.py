from django.db import models
from accounts.models import Author

class Story(models.Model):
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='stories')
    title = models.CharField(250)
    GENRE_CHOICES = (
        ('mystery', 'Mystery'), 
        ('fiction', 'Fiction'),
        ('comedy', 'Comedy'),
        ('others', 'Others'),
    )
    genre = models.CharField(max_length=7, choices=GENRE_CHOICES, default='others')
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

