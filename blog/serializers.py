from rest_framework import serializers
from .models import Post, Comment, Category 

# category serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# PostSerializer ---
class PostSerializer(serializers.ModelSerializer):
    # To show category names instead of IDs (Optional, makes API nicer)
    # Use StringRelatedField for read-only names
    # categories = serializers.StringRelatedField(many=True, read_only=True)

    
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False # Allow creating/updating posts without categories
    )

    class Meta:
        model = Post
        # Add 'likes', 'dislikes', 'categories' to fields
        fields = [
            'id', 'title', 'content', 'author',
            'created_at', 'updated_at',
            'likes', 'dislikes', # Add counts
            'categories'       # Add categories field
        ]
        # read-only
        read_only_fields = ['created_at', 'updated_at', 'likes', 'dislikes']

#  CommentSerializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at', 'post']
        read_only_fields = ['created_at', 'updated_at', 'post']