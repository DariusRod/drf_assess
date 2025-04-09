from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


 
# Handle Get and Post requests for the Post model
class PostListCreateView(generics.ListCreateAPIView):

    # Fetch all posts and create a new post
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
     # No permission classes needed as per requirement (defaults to AllowAny)
    # Pagination will be applied based on settings.py configuration


# Handles GET (retrieve), PUT (update), and DELETE (destroy) requests for a single Post
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows a single post to be retrieved, updated, or deleted.
    GET /api/posts/{id}/: Retrieve a post by its ID.
    PUT /api/posts/{id}/: Update a post by its ID. Requires 'title', 'content', 'author'.
    PATCH /api/posts/{id}/: Partially update a post by its ID.
    DELETE /api/posts/{id}/: Delete a post by its ID.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # No permission classes needed, any user can update/delete.
    # The lookup field defaults to 'pk' (primary key, which is 'id' in our case)


# comment view 


# Handles GET (list) and POST (create) requests for Comments related to a specific Post
class CommentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint that allows comments for a specific post to be viewed or created.
    GET /api/posts/{post_id}/comments/: List all comments for the post with {post_id}.
    POST /api/posts/{post_id}/comments/: Create a new comment for the post with {post_id}.
                                         Requires 'content' and 'author' in request body.
    """
    serializer_class = CommentSerializer
    # No permission classes needed.

    def get_queryset(self):
        """
        Override to filter comments based on the post_id URL parameter.
        """
        post_id = self.kwargs.get('post_pk') # Get post_id from URL keyword arguments
        # Ensure the post exists before trying to fetch comments
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail="Post not found.") # Return 404 if post doesn't exist

        # Return comments related to the specific post, newest first
        return Comment.objects.filter(post=post).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Override to automatically associate the comment with the correct post
        based on the post_id URL parameter.
        """
        post_id = self.kwargs.get('post_pk')
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
             # Although get_queryset checks, perform_create needs its own check
             # for the POST request context.
            raise NotFound(detail="Post not found.")

        # Save the comment, associating it with the retrieved post.
        # The 'author' and 'content' fields are automatically handled by the serializer
        # from the request data.
        serializer.save(post=post)


# Handles GET (retrieve) and DELETE (destroy) requests for a specific Comment
class CommentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    API endpoint that allows a specific comment to be retrieved or deleted.
    GET /api/posts/{post_id}/comments/{id}/: Retrieve comment {id} for post {post_id}.
    DELETE /api/posts/{post_id}/comments/{id}/: Delete comment {id} for post {post_id}.
    """
    serializer_class = CommentSerializer
    # No permission classes needed.
    lookup_url_kwarg = 'comment_pk' # Use 'comment_pk' from URL as the lookup field identifier

    def get_queryset(self):
        """
        Override to ensure the comment belongs to the specified post.
        """
        post_id = self.kwargs.get('post_pk')
        comment_id = self.kwargs.get('comment_pk') # Get comment_id from URL

        # Ensure the post exists first
        try:
            Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail="Post not found.")

        # Filter comments by both post_id and comment_id to ensure correctness
        return Comment.objects.filter(post_id=post_id, pk=comment_id)

    # Optional: Add a custom delete method if needed, but generic view handles it.
    # def perform_destroy(self, instance):
    #     instance.delete() # Standard behavior  
