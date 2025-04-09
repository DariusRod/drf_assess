from django.db import models

# Represents a blog post
class Post(models.Model):
    # Title of the blog post, limited to 255 characters
    title = models.CharField(max_length=255)
    # Main content of the blog post
    content = models.TextField()
    # Timestamp when the post was created, automatically set on creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the post was last updated, automatically set on save
    updated_at = models.DateTimeField(auto_now=True)
    # Author's name (simple CharField as no user authentication is required)
    author = models.CharField(max_length=100)

    # String representation of the Post object, useful for admin interface etc.
    def __str__(self):
        return self.title

#  comment on a blog post
class Comment(models.Model):
    # Content of the comment
    content = models.TextField()
    # Timestamp when the comment was created, automatically set on creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the comment was last updated, automatically set on save
    updated_at = models.DateTimeField(auto_now=True)
    # ForeignKey linking the comment to its parent post.
    # related_name='comments' allows accessing comments from a post object (e.g., post.comments.all())
    # on_delete=models.CASCADE ensures that if a post is deleted, all its comments are also deleted.
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
 
    author = models.CharField(max_length=100)

    # String representation of the Comment object
    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'