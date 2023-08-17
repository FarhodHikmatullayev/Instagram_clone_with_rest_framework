from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.custom_pagination import CustomPagination
from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer


class PostListApiView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination


class PostCreateApiView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):  # saqlashdan oldin postni ushlab qolib unga authorni yuklaydi
        serializer.save(author=self.request.user)


class RetrieveUpdateDeleteApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.all()


class CommentListApiView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostComment.objects.filter(post__id=post_id)
        return queryset


class PostCommentCreateApiView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post_id=self.kwargs["pk"])


class CommentListCreateApiView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentLikeListCreateApiView(ListCreateAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = CommentLike.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostLikeListCreateApiView(ListCreateAPIView):
    serializer_class = PostLikeSerializer
    queryset = PostLike.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostOwnLikesListApiView(ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PostLike.objects.filter(post__id=self.kwargs['pk'])


class CommentOwnLikesListApiView(ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CommentLike.objects.filter(comment__id=self.kwargs['pk'])


class CommentLikingApiView(APIView):
    def post(self, request, pk):
        try:
            comment_like = CommentLike.objects.get(author=request.user, comment__id=pk)

            comment_like.delete()
            data = {
                "success": True,
                "message": "Comment LIKE muvaffaqiyatli o'chirildi"
            }
        except:

            like = CommentLike.objects.create(author=request.user, comment_id=pk)
            serializer = CommentLikeSerializer(like)
            data = {
                "success": True,
                "message": "Commentga LIKE muvaffaqiyatli o'rnatildi",
                "data": serializer.data
            }
        return Response(
            data,
            status=200
        )


class PostLikingApiView(APIView):
    def post(self, request, pk):
        try:
            post_like = PostLike.objects.get(author=self.request.user, post_id=pk)
            post_like.delete()
            data = {
                "success": True,
                "message": "Post LIKE muvaffaqiyatli o'chirildi"
            }

        except:
            like = PostLike.objects.create(author=self.request.user, post_id=pk)
            serializer = PostLikeSerializer(like)
            data = {
                "success": True,
                "message": "Postga LIKE muvaffaqiyatli o'rnatildi",
                "data": serializer.data
            }

        return Response(
            data,
            status=200
        )


