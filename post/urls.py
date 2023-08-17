from django.urls import path
from .views import PostListApiView, RetrieveUpdateDeleteApiView, PostCreateApiView, CommentListApiView, \
    PostCommentCreateApiView, CommentListCreateApiView, CommentLikeListCreateApiView, PostLikeListCreateApiView, \
    PostOwnLikesListApiView, CommentOwnLikesListApiView, CommentLikingApiView, PostLikingApiView

app_name = 'post'

urlpatterns = [
    path('list/', PostListApiView.as_view(), name='list'),
    path('create/', PostCreateApiView.as_view(), name='create'),
    path('<uuid:pk>/', RetrieveUpdateDeleteApiView.as_view()),
    path('<uuid:pk>/comments/', CommentListApiView.as_view(), name='comment_list'),
    path('<uuid:pk>/comments/create/', PostCommentCreateApiView.as_view(), name='comment_create'),
    path('comments/', CommentListCreateApiView.as_view()),
    path('<uuid:pk>/likes/', PostOwnLikesListApiView.as_view(), name='likes_list'),
    path('comments/<uuid:pk>/likes/', CommentOwnLikesListApiView.as_view(), name='comment_likes'),
    path('comments/<uuid:pk>/liking/', CommentLikingApiView.as_view(), name='comment_liking'),
    path('<uuid:pk>/liking/', PostLikingApiView.as_view()),
]
