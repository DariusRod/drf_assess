from rest_framework import serializers
from .models import Post, Comment 


# Serializer for the Post model
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        # fields to include in the serialized output
        model = Post
        fields = ['id', 'title', 'author','content', 'created_at', 'updated_at']

        # fields that should be read-only (not editable through the API)
        read_only_fields = ['created_at', 'updated_at']


# Serializer for the Comment model
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        # fields to include in the serialized output
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at', 'updated_at']

        # fields that should be read-only (not editable through the API)
        read_only_fields = ['created_at', 'updated_at']