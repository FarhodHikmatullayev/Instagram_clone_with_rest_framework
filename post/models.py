from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel

User = get_user_model()


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
                              upload_to="users/posts/images/")
    caption = models.TextField(validators=[MaxLengthValidator(limit_value=200)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return f"{self.author}'s post"


class PostComment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)


class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'], name='unique_postlike_for_author'
            )
        ]


class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='like')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'], name='unique_commentlike_for_author'
            )
        ]
