# blog/urls.py

from django.urls import path
from .views import (
    PostListCreateView,
    PostRetrieveUpdateDestroyView,
    CommentListCreateView,
    CommentRetrieveDestroyView,
)

urlpatterns = [
    # Post URLs
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='post-detail'),

    # Comment URLs (nested under posts)
    # Use 'post_pk' to match the keyword argument used in the Comment views
    path('posts/<int:post_pk>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/', CommentRetrieveDestroyView.as_view(), name='comment-detail'),
]