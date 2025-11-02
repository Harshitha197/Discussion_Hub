# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


class Page(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')


    # def get_replies(self):
    #     return self.replies.all().order_by('created_at')


    def __str__(self):
        return f'Comment by {self.author.username} on {self.page.title}'

    def is_parent(self):
        return self.parent is None

    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('created_at')

    # def get_upvote_count(self):
    #     return self.votes.filter(vote_type='up').count()

    # def get_downvote_count(self):
    #     return self.votes.filter(vote_type='down').count()

    # def get_vote_score(self):
    #     return self.get_upvote_count() - self.get_downvote_count()

    def get_user_vote(self, user):
        vote = self.votes.filter(user=user).first()
        return vote.vote_type if vote else None

    # models.py

    @property
    def upvote_count(self):
        return self.votes.filter(vote_type='up').count()

    @property
    def downvote_count(self):
        return self.votes.filter(vote_type='down').count()

    @property
    def score(self):
        return self.upvote_count - self.downvote_count

    is_deleted = models.BooleanField(default=False)  # NEW FIELD

    def can_be_edited_by(self, user):
        return (
            user == self.author and
            not self.is_deleted and
            timezone.now() <= self.created_at + timedelta(minutes=settings.COMMENT_EDIT_TIMEOUT_MINUTES)
        )

    def can_be_deleted_by(self, user):
        return user == self.author and not self.is_deleted


    class Meta:
        ordering = ['created_at']

class Vote(models.Model):
    VOTE_TYPES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)
    voted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} {self.vote_type}d on comment {self.comment.id}'
