
from rest_framework import serializers
from .models import Post, Comment

# serializer for the Post model
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # Specify the fields to be included in the serialized output
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# Serializer for the Comment model
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at', 'post']
        # VITAL LINE: Make sure 'post' is listed here!
        read_only_fields = ['created_at', 'updated_at', 'post']