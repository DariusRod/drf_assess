from django.db import models




# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True) # Category names should be unique

    class Meta:
        verbose_name_plural = "Categories" # Correct plural name in admin

    def __str__(self):
        return self.name



# Blog Post Model
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=100)

   
    # Like/Dislike counts
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    # Relationship to Categories
    # related_name allows accessing posts from a category object (e.g., category.posts.all())
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    # `blank=True` allows posts to be created without assigning a category initially

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
    
    # on_delete=models.CASCADE ensures that if a post is deleted, all its comments are also deleted.
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
 
    author = models.CharField(max_length=100)

    # String representation of the Comment object
    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'