from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Page, Comment, Vote


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'date_joined']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    upvotes = serializers.IntegerField(read_only=True)
    downvotes = serializers.IntegerField(read_only=True)
    net_votes = serializers.IntegerField(read_only=True)
    user_vote = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'page', 'author', 'parent', 'content', 'created_at', 
                  'updated_at', 'is_deleted', 'upvotes', 'downvotes', 'net_votes',
                  'user_vote', 'replies_count']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'is_deleted']
    
    def get_user_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                vote = Vote.objects.get(user=request.user, comment=obj)
                return vote.vote_type
            except Vote.DoesNotExist:
                return None
        return None
    
    def get_replies_count(self, obj):
        return obj.replies.filter(is_deleted=False).count()


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['page', 'parent', 'content']
    
    def validate_parent(self, value):
        if value and value.is_deleted:
            raise serializers.ValidationError("Cannot reply to a deleted comment.")
        return value


class PageSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = ['id', 'title', 'content', 'created_at', 'comments_count']
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_deleted=False, parent__isnull=True).count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'comment', 'vote_type', 'voted_at']
        read_only_fields = ['id', 'voted_at']