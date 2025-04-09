from rest_framework import generics, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle # Import throttle classes
from .models import Post, Comment, Category 
from .serializers import PostSerializer, CommentSerializer, CategorySerializer 



class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet providing complete CRUD operations for Posts, plus like/dislike actions.

    Includes:
    - List all Posts (GET /api/posts/)
    - Create a Post (POST /api/posts/)
    - Retrieve a Post (GET /api/posts/{pk}/)
    - Update a Post (PUT/PATCH /api/posts/{pk}/)
    - Delete a Post (DELETE /api/posts/{pk}/)
    - Like a Post (POST /api/posts/{pk}/like/)
    - Dislike a Post (POST /api/posts/{pk}/dislike/)

    Supports filtering, searching, and ordering:
    - Filter by author: ?author=<author_name>
    - Filter by category ID: ?categories=<category_id>
    - Search title/content: ?search=<search_term>
    - Order results: ?ordering=<field_name> (e.g., likes, -created_at)
    """
    # --- Basic ViewSet Configuration ---
    queryset = Post.objects.all().order_by('-created_at') # Default ordering
    serializer_class = PostSerializer

    # --- Throttling Configuration ---
    # Apply throttling (adjust class based on auth: UserRateThrottle or AnonRateThrottle)
    #  'user' or 'anon' scope is defined in settings.DEFAULT_THROTTLE_RATES
    throttle_classes = [UserRateThrottle]
    # throttle_scope = 'user' # Explicit scope (optional if using default 'user'/'anon')

  

    # Fields available for ?field=value filtering (requires DjangoFilterBackend)
    filterset_fields = {
        'author': ['exact'], # Allow filtering like ?author=JohnDoe
        'categories': ['exact'] # Allow filtering like ?categories=1 (by Category ID)
    }
    # Fields available for ?search=term searching (requires SearchFilter)
    search_fields = ['title', 'content']
    # Fields available for ?ordering=field sorting (requires OrderingFilter)
    ordering_fields = ['created_at', 'updated_at', 'likes', 'dislikes', 'author', 'title']
    # ordering = ['-created_at'] # Set default ordering via queryset is often preferred


    # --- Custom Actions for Like/Dislike ---

    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        """
        Action to increment the like count for a specific post.
        Accessible via POST request to /api/posts/{pk}/like/
        """
        # Retrieve the specific Post instance using the primary key from the URL
        post = self.get_object()
        # Increment the likes field
        post.likes += 1
        # Save only the 'likes' field for efficiency
        post.save(update_fields=['likes'])
        # Return a success response with the updated like count
        return Response(
            {'status': 'post liked', 'likes': post.likes},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='dislike')
    def dislike(self, request, pk=None):
        """
        Action to increment the dislike count for a specific post.
        Accessible via POST request to /api/posts/{pk}/dislike/
        """
        # Retrieve the specific Post instance
        post = self.get_object()
        # Increment the dislikes field
        post.dislikes += 1
        # Save only the 'dislikes' field for efficiency
        post.save(update_fields=['dislikes'])
        # Return a success response with the updated dislike count
        return Response(
            {'status': 'post disliked', 'dislikes': post.dislikes},
            status=status.HTTP_200_OK
        )



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for listing and retrieving Categories.

    Includes:
    - List Categories (GET /api/categories/)
    - Retrieve a Category (GET /api/categories/{pk}/)
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    
    throttle_classes = [UserRateThrottle]

# ==============================================================================
# Comment Views (Using Generic Views for Nested Structure)
# ==============================================================================

class CommentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint that allows comments for a specific post to be viewed or created.
    Handles GET (list) and POST (create) for /api/posts/{post_pk}/comments/
    """
    serializer_class = CommentSerializer
    # Apply throttling (adjust class based on auth)
    throttle_classes = [UserRateThrottle]

    def get_queryset(self):
        """
        Overrides default queryset to filter comments based on the 'post_pk'
        captured from the URL. Ensures comments shown belong only to the specified post.
        Also handles 404 if the post itself doesn't exist.
        """
        # Get the post primary key from the URL kwargs
        post_id = self.kwargs.get('post_pk')
        # Verify the parent Post exists, otherwise raise 404
        try:
            Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=f"Post with ID {post_id} not found.")
        # Return only comments related to the specific post
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')

    def perform_create(self, serializer):
        """
        Overrides the save behavior for comment creation.
        Automatically associates the new comment with the parent Post
        identified by 'post_pk' in the URL, removing the need to send 'post' in the request body.
        Handles 404 if the post doesn't exist.
        """
        # Get the post primary key from the URL kwargs
        post_id = self.kwargs.get('post_pk')
        # Retrieve the parent Post instance
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            # Should not happen if get_queryset logic is sound, but good practice to check
            raise NotFound(detail=f"Post with ID {post_id} not found.")
        # Save the comment instance, injecting the parent post relationship
        serializer.save(post=post)


class CommentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    API endpoint that allows a specific comment to be retrieved or deleted.
    Handles GET (retrieve) and DELETE (destroy) for /api/posts/{post_pk}/comments/{comment_pk}/
    """
    serializer_class = CommentSerializer
    # Apply throttling (adjust class based on auth)
    throttle_classes = [UserRateThrottle]
    # Specify which URL kwarg contains the primary key for *this* view's object (the comment)
    lookup_url_kwarg = 'comment_pk'

    def get_queryset(self):
        """
        Overrides default queryset to ensure the retrieved/deleted comment
        belongs to the specific post identified by 'post_pk' in the URL.
        Prevents accessing a comment through the wrong post's URL.
        Handles 404 if the post or the specific comment doesn't exist for that post.
        """
        # Get keys from the URL kwargs
        post_id = self.kwargs.get('post_pk')
        comment_id = self.kwargs.get('comment_pk') # The ID for the comment itself

        # Optional: Verify the parent Post exists first (improves clarity of 404s)
        try:
            Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=f"Post with ID {post_id} not found.")

        # Filter comments matching both the post ID and the comment ID
        # This ensures the comment actually belongs to the specified post
        return Comment.objects.filter(post_id=post_id, pk=comment_id)