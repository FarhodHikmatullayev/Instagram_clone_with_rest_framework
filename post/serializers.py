from rest_framework import serializers

from post.models import Post, PostLike, PostComment, CommentLike
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'photo']


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_like_count = serializers.SerializerMethodField('get_post_like_count')
    post_comment_count = serializers.SerializerMethodField('get_post_comment_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = ['id', 'author', 'image', 'caption', 'created_time', 'post_like_count', 'post_comment_count',
                  'me_liked']

    @staticmethod
    def get_post_like_count(obj):
        return obj.likes.count()

    @staticmethod
    def get_post_comment_count(obj):
        return obj.comments.count()

    def get_me_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if PostLike.objects.filter(author=request.user, post=obj).exists():
                return True
            else:
                return False
        else:
            return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    likes_count = serializers.SerializerMethodField('get_likes_count')

    class Meta:
        model = PostComment
        fields = ['id', 'author', 'comment', 'post', 'parent', 'created_time', 'replies', 'me_liked', 'likes_count']

    def get_replies(self, obj):
        if obj.children.exists():
            serializer = self.__class__(data=obj.children.all(), many=True, context=self.context)
            return serializer.data
        else:
            return None

    def get_me_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return CommentLike.objects.filter(author=user, comment=obj).exists()
        else:
            return False

    @staticmethod
    def get_likes_count(obj):
        return CommentLike.objects.filter(comment=obj).count()


class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommentLike
        fields = ['id', 'author', 'comment']


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ['id', 'author', 'post']
