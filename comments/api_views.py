from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Count, Q
from .models import Page, Comment, Vote
from .serializers import (
    PageSerializer, CommentSerializer, CommentCreateSerializer, VoteSerializer
)


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing pages/posts.
    GET /api/pages/ - List all pages
    GET /api/pages/{id}/ - Get specific page
    GET /api/pages/{id}/comments/ - Get all comments for a page
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all top-level comments for a page"""
        page = self.get_object()
        comments = Comment.objects.filter(
            page=page, 
            parent__isnull=True,
            is_deleted=False
        ).annotate(
            upvotes=Count('votes', filter=Q(votes__vote_type=1)),
            downvotes=Count('votes', filter=Q(votes__vote_type=-1)),
            net_votes=Count('votes', filter=Q(votes__vote_type=1)) - 
                      Count('votes', filter=Q(votes__vote_type=-1))
        ).order_by('-created_at')
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments.
    GET /api/comments/ - List all comments
    POST /api/comments/ - Create new comment
    GET /api/comments/{id}/ - Get specific comment
    PUT/PATCH /api/comments/{id}/ - Update comment
    DELETE /api/comments/{id}/ - Delete comment
    GET /api/comments/{id}/replies/ - Get replies to a comment
    POST /api/comments/{id}/vote/ - Vote on a comment
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'net_votes']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Comment.objects.filter(is_deleted=False).annotate(
            upvotes=Count('votes', filter=Q(votes__vote_type=1)),
            downvotes=Count('votes', filter=Q(votes__vote_type=-1)),
            net_votes=Count('votes', filter=Q(votes__vote_type=1)) - 
                      Count('votes', filter=Q(votes__vote_type=-1))
        )
        
        # Filter by page if provided
        page_id = self.request.query_params.get('page', None)
        if page_id:
            queryset = queryset.filter(page_id=page_id)
        
        # Filter by parent (top-level or replies)
        parent_id = self.request.query_params.get('parent', None)
        if parent_id == 'null' or parent_id == '':
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'You can only edit your own comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return Response(
                {'error': 'You can only delete your own comments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.is_deleted = True
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Get all replies to a comment"""
        parent_comment = self.get_object()
        replies = Comment.objects.filter(
            parent=parent_comment,
            is_deleted=False
        ).annotate(
            upvotes=Count('votes', filter=Q(votes__vote_type=1)),
            downvotes=Count('votes', filter=Q(votes__vote_type=-1)),
            net_votes=Count('votes', filter=Q(votes__vote_type=1)) - 
                      Count('votes', filter=Q(votes__vote_type=-1))
        ).order_by('created_at')
        
        serializer = CommentSerializer(replies, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """
        Vote on a comment.
        Body: {"vote_type": 1} for upvote, {"vote_type": -1} for downvote
        """
        comment = self.get_object()
        vote_type = request.data.get('vote_type')
        
        if vote_type not in [1, -1]:
            return Response(
                {'error': 'vote_type must be 1 (upvote) or -1 (downvote)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'vote_type': vote_type}
        )
        
        if not created:
            if vote.vote_type == vote_type:
                # Remove vote if clicking same button
                vote.delete()
                return Response({'status': 'vote removed'})
            else:
                # Change vote
                vote.vote_type = vote_type
                vote.save()
                return Response({'status': 'vote changed'})
        
        return Response({'status': 'vote added'}, status=status.HTTP_201_CREATED)