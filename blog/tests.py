from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Post, Comment
# from .serializers import PostSerializer, CommentSerializer # Import serializers if needed for direct comparison


class BlogAPITests(APITestCase):

    def setUp(self):
        """
        Set up a common post that exists before each test method runs.
        This impacts tests that assert on the total count of posts.
        """
        self.post = Post.objects.create(title='Setup Post for Comments', content='Content for setUp', author='Setup Author')

    # ---- Test Post Endpoints ----

    def test_create_post(self):
        """
        Ensure we can create a new post object via the API.
        """
        initial_count = Post.objects.count() # Count posts *after* setUp ran (should be 1)
        url = reverse('post-list-create')
        data = {'title': 'Test Create Post', 'content': 'This is test content.', 'author': 'Test Author'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the total count increased by 1
        self.assertEqual(Post.objects.count(), initial_count + 1)

        # Check the details of the newly created post in the response
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['author'], data['author'])

        # Optionally, check the object in the database directly
        new_post = Post.objects.get(pk=response.data['id'])
        self.assertEqual(new_post.title, data['title'])
        self.assertEqual(new_post.author, data['author'])


    def test_list_posts(self):
        """
        Ensure we can list all posts and pagination structure is present.
        Accounts for the post created in setUp.
        """
        # setUp created self.post
        # Create 2 additional posts for this test
        post1 = Post.objects.create(title='List Post 1', content='Content 1', author='Author 1')
        post2 = Post.objects.create(title='List Post 2', content='Content 2', author='Author 2')
        expected_total_posts = 3 # 1 from setUp + 2 created here

        url = reverse('post-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check pagination structure keys exist (even if only one page)
        self.assertTrue('count' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertTrue('results' in response.data)

        # Check the total count matches the expected number
        self.assertEqual(response.data['count'], expected_total_posts)
        # Check the number of results on the current page
        self.assertEqual(len(response.data['results']), expected_total_posts)

        # Optional: Check if the titles are present (order depends on default_ordering)
        returned_titles = {p['title'] for p in response.data['results']}
        expected_titles = {self.post.title, post1.title, post2.title}
        self.assertSetEqual(returned_titles, expected_titles)


    def test_retrieve_post(self):
        """
        Ensure we can retrieve a single post (the one from setUp) by its ID.
        """
        url = reverse('post-detail', kwargs={'pk': self.post.pk}) # Use the post from setUp
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)
        self.assertEqual(response.data['content'], self.post.content)
        self.assertEqual(response.data['author'], self.post.author)
        self.assertTrue('created_at' in response.data)
        self.assertTrue('updated_at' in response.data)


    def test_update_post(self):
        """
        Ensure any user can update any post (using the post from setUp).
        """
        url = reverse('post-detail', kwargs={'pk': self.post.pk}) # Use the post from setUp
        updated_data = {'title': 'New Updated Title', 'content': 'New Updated Content', 'author': 'Updater Author'}
        response = self.client.put(url, updated_data, format='json') # PUT requires all required fields

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db() # Reload the object from the database
        self.assertEqual(self.post.title, updated_data['title'])
        self.assertEqual(self.post.content, updated_data['content'])
        self.assertEqual(self.post.author, updated_data['author'])


    def test_delete_post(self):
        """
        Ensure any user can delete any post.
        Creates a *new* post specifically for this test to delete,
        and ensures the setUp post remains untouched.
        """
        # Create a specific post to delete in this test
        post_to_delete = Post.objects.create(title='To Delete', content='Delete me', author='Deleter')
        count_before_delete = Post.objects.count() # Should be 2 (setUp post + post_to_delete)

        url = reverse('post-detail', kwargs={'pk': post_to_delete.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check that the total count decreased by 1
        self.assertEqual(Post.objects.count(), count_before_delete - 1)
        # Check that the specific post is gone
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(pk=post_to_delete.pk)
        # Check that the setUp post still exists (verifies we deleted the correct one)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())


    # ---- Test Comment Endpoints ----
    # Note: These tests rely on self.post created in setUp

    def test_create_comment(self):
        """
        Ensure we can create a comment on the setUp post.
        Includes debugging output if status code is not 201.
        """
        url = reverse('comment-list-create', kwargs={'post_pk': self.post.pk})
        data = {'content': 'This is a test comment.', 'author': 'Commenter'}
        response = self.client.post(url, data, format='json')

        # --- Debugging: Print response data if the status code is unexpected ---
        if response.status_code != status.HTTP_201_CREATED:
            print(f"\n----- DEBUG: test_create_comment received status {response.status_code} -----")
            try:
                print(response.json()) # Try to print JSON data for DRF errors
            except Exception:
                 print(response.content) # Fallback to raw content
            print("----- END DEBUG -----")
        # ----------------------------------------------------------------------

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check only 1 comment exists in total after this action
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get() # Get the created comment
        self.assertEqual(comment.content, data['content'])
        self.assertEqual(comment.author, data['author'])
        self.assertEqual(comment.post, self.post) # Ensure linked to the correct post

        # Check response data matches
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['author'], data['author'])
        self.assertEqual(response.data['post'], self.post.pk) # Should return the post ID


    def test_list_comments_for_post(self):
        """
        Ensure we can list comments specifically for the setUp post.
        """
        # Create comments for the specific post from setUp
        comment1 = Comment.objects.create(post=self.post, content='Comment 1', author='Author A')
        comment2 = Comment.objects.create(post=self.post, content='Comment 2', author='Author B')
        # Create a comment for another post (should not be listed)
        other_post = Post.objects.create(title='Other Post', content='...', author='Other')
        Comment.objects.create(post=other_post, content='Comment on other post', author='Author C')

        url = reverse('comment-list-create', kwargs={'post_pk': self.post.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check pagination structure keys exist
        self.assertTrue('count' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertTrue('results' in response.data)

        # Should only list the 2 comments for self.post
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

        # Check content (assuming default ordering is -created_at)
        returned_contents = {c['content'] for c in response.data['results']}
        expected_contents = {comment1.content, comment2.content}
        self.assertSetEqual(returned_contents, expected_contents)
        # If order matters:
        # self.assertEqual(response.data['results'][0]['content'], comment2.content)
        # self.assertEqual(response.data['results'][1]['content'], comment1.content)


    def test_retrieve_comment(self):
        """
        Ensure we can retrieve a specific comment by its ID for the setUp post.
        """
        comment = Comment.objects.create(post=self.post, content='Retrieve this comment', author='Retriever Commenter')
        url = reverse('comment-detail', kwargs={'post_pk': self.post.pk, 'comment_pk': comment.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], comment.content)
        self.assertEqual(response.data['author'], comment.author)
        self.assertTrue('created_at' in response.data)

        # Ensure we cannot retrieve a comment using the wrong post_pk
        wrong_post_pk_url = reverse('comment-detail', kwargs={'post_pk': self.post.pk + 99, 'comment_pk': comment.pk})
        # Create a dummy post with ID + 99 if it doesn't exist, otherwise this might give 404 on post lookup
        Post.objects.get_or_create(pk=self.post.pk + 99, defaults={'title':'Dummy', 'content':'...', 'author':'Dummy'})
        response_wrong_post = self.client.get(wrong_post_pk_url, format='json')
        self.assertEqual(response_wrong_post.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_comment(self):
        """
        Ensure any user can delete any comment.
        """
        comment = Comment.objects.create(post=self.post, content='Delete this comment', author='Deleter Commenter')
        initial_comment_count = Comment.objects.count() # Should be 1
        self.assertEqual(initial_comment_count, 1)

        url = reverse('comment-detail', kwargs={'post_pk': self.post.pk, 'comment_pk': comment.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), initial_comment_count - 1) # Count should be 0
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(pk=comment.pk)

        # Ensure we cannot delete a comment using the wrong post_pk
        comment_again = Comment.objects.create(post=self.post, content='Delete this comment again', author='Deleter Commenter')
        self.assertEqual(Comment.objects.count(), 1) # Count back to 1
        wrong_post_pk_url = reverse('comment-detail', kwargs={'post_pk': self.post.pk + 99, 'comment_pk': comment_again.pk})
        # Ensure dummy post exists for the URL check
        Post.objects.get_or_create(pk=self.post.pk + 99, defaults={'title':'Dummy', 'content':'...', 'author':'Dummy'})
        response_wrong_post = self.client.delete(wrong_post_pk_url)
        self.assertEqual(response_wrong_post.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Comment.objects.count(), 1) # Comment should still exist


    # ---- Test Pagination ----

    def test_pagination_on_posts(self):
        """
        Ensure pagination works correctly for the post list endpoint.
        Accounts for the post created in setUp.
        """
        # setUp created self.post
        num_to_create = 15
        for i in range(num_to_create):
            Post.objects.create(title=f'Pag Post {i}', content=f'Content {i}', author=f'Author {i}')

        # Total posts = 1 (from setUp) + 15 (created here) = 16
        total_expected_posts = num_to_create + 1

        url = reverse('post-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('count' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('previous' in response.data)
        self.assertTrue('results' in response.data)

        # Check total count
        self.assertEqual(response.data['count'], total_expected_posts)

        # Assuming PAGE_SIZE=10 from settings.py
        page_size = 10
        self.assertIsNotNone(response.data['next']) # Should be a link to page 2
        self.assertIsNone(response.data['previous']) # Should be null on page 1
        self.assertEqual(len(response.data['results']), page_size) # Should contain PAGE_SIZE items

        # Test fetching the second page
        response_page2 = self.client.get(response.data['next'], format='json') # Follow the 'next' link
        self.assertEqual(response_page2.status_code, status.HTTP_200_OK)
        # Remaining items on page 2 = 16 - 10 = 6
        self.assertEqual(len(response_page2.data['results']), total_expected_posts - page_size)
        self.assertIsNone(response_page2.data['next']) # No next page after page 2
        self.assertIsNotNone(response_page2.data['previous']) # Should be a link back to page 1