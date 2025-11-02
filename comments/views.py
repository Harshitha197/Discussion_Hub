from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.paginator import Paginator
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Count, Q

from .models import Page, Comment, Vote
from .forms import CommentForm, CustomUserCreationForm

# Get cache timeout from settings (add this to settings.py if not exists)
CACHE_TTL = getattr(settings, 'CACHE_TTL', 900)  # 15 minutes default


def homepage(request):
    """Display the list of pages/discussions"""
    pages = Page.objects.all().order_by('-created_at')
    
    # Annotate with comment count
    pages = pages.annotate(
        comment_count=Count('comments', filter=Q(comments__is_deleted=False))
    )
    
    return render(request, 'comments/homepage.html', {'pages': pages})


def annotate_comments(comments, user):
    """Helper to add user-specific info and permissions to comment objects.

    NOTE: do NOT assign to model @property attributes like upvote_count/downvote_count/score,
    instead rely on the model properties and only attach temporary attributes used by templates.
    """
    annotated = []
    for comment in comments:
        # user vote status (safe to attach)
        if user.is_authenticated:
            try:
                user_vote = comment.votes.get(user=user)
                comment.user_vote = user_vote.vote_type
            except Vote.DoesNotExist:
                comment.user_vote = None
        else:
            comment.user_vote = None

        # permissions (safe to attach)
        comment.can_edit = comment.can_be_edited_by(user)
        comment.can_delete = comment.can_be_deleted_by(user)

        # do not assign to comment.upvote_count / comment.downvote_count / comment.score
        # those are model @property attributes and should be accessed read-only in templates

        annotated.append(comment)

    return annotated


def page_detail(request, page_id):
    """Display a page/discussion with its comments"""
    # Try to get page from cache first
    cache_key = f'page_{page_id}'
    page = cache.get(cache_key)
    
    if not page:
        page = get_object_or_404(Page, pk=page_id)
        cache.set(cache_key, page, timeout=CACHE_TTL)
    
    # Get top-level comments (don't cache the QuerySet itself, causes issues)
    top_level_comments = Comment.objects.filter(
        page=page, 
        parent__isnull=True,
        is_deleted=False
    ).select_related('author').prefetch_related('votes').order_by('-created_at')
    
    # Annotate comments with vote data and permissions
    annotated_comments = annotate_comments(top_level_comments, request.user)
    
    # Pagination
    paginator = Paginator(annotated_comments, 10)  # 10 comments per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.page = page
            
            # Handle parent comment (reply)
            parent_comment = form.cleaned_data.get('parent_id')
            if parent_comment:
                comment.parent = parent_comment
            
            comment.save()
            
            # Invalidate cache
            cache.delete(f'page_{page_id}')
            
            # Send WebSocket notification
            try:
                channel_layer = get_channel_layer()
                
                # Notify the page room
                async_to_sync(channel_layer.group_send)(
                    f'comments_page_{page_id}',
                    {
                        'type': 'comment_message',
                        'comment': {
                            'id': comment.id,
                            'author': comment.author.username,
                            'content': comment.content,
                            'created_at': comment.created_at.isoformat(),
                            'parent_id': comment.parent_id
                        }
                    }
                )
                
                # If it's a reply, notify the parent comment author
                if comment.parent and comment.parent.author != request.user:
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{comment.parent.author.id}',
                        {
                            'type': 'notification_message',
                            'message': f'{request.user.username} replied to your comment',
                            'comment_id': comment.id,
                            'page_id': page_id
                        }
                    )
            except Exception as e:
                # WebSocket failed but comment was saved
                print(f"WebSocket error: {e}")
            
            if parent_comment:
                messages.success(request, 'Reply added successfully!')
            else:
                messages.success(request, 'Comment added successfully!')
            
            return redirect('comments:page_detail', page_id=page_id)
    else:
        form = CommentForm()
    
    return render(request, 'comments/page_detail.html', {
        'page': page,
        'comments': page_obj,
        'comment_form': form,
        'page_obj': page_obj
    })


def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('comments:homepage')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def add_comment(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.page = page
            comment.author = request.user

            # Get parent_id from cleaned_data (this returns the Comment object or None)
            parent_comment = form.cleaned_data.get('parent_id')
            if parent_comment:
                comment.parent = parent_comment
                messages.success(request, 'Reply added successfully!')
            else:
                messages.success(request, 'Comment added successfully!')

            comment.save()
            return redirect('comments:page_detail', page_id=page_id)

        else:
            # Re-fetch comments with permissions for rendering
            comments = Comment.objects.filter(page=page, parent=None).order_by('-created_at')
            for comment in comments:
                annotate_comments(comment, request.user)
                
            return render(request, 'comments/page_detail.html', {
                'page': page,
                'comments': comments,
                'comment_form': form,
                'parent_id': request.POST.get('parent_id'),
            })

    return redirect('comments:page_detail', page_id=page_id)
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Vote

@login_required
@require_POST
def vote_comment(request, comment_id):
    """Handle upvote/downvote on a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    vote_type = request.POST.get('vote_type')

    # Validate vote_type
    if vote_type not in ['up', 'down']:
        messages.error(request, 'Invalid vote type.')
        return redirect('comments:page_detail', page_id=comment.page.id)

    try:
        existing_vote = Vote.objects.get(user=request.user, comment=comment)

        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
            action = 'removed'
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
            action = 'changed'

    except Vote.DoesNotExist:
        Vote.objects.create(user=request.user, comment=comment, vote_type=vote_type)
        action = 'added'

    # Handle AJAX (optional)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'upvote_count': comment.upvote_count,
            'downvote_count': comment.downvote_count,
            'score': comment.score,
            'user_vote': comment.get_user_vote(request.user)
        })

    # Normal request
    messages.success(request, f"Vote {action}: {vote_type}")
    return redirect('comments:page_detail', page_id=comment.page.id)

@login_required
def edit_comment(request, comment_id):
    """Edit a comment"""
    comment = get_object_or_404(Comment, id=comment_id)

    if not comment.can_be_edited_by(request.user):
        messages.error(request, "You can't edit this comment.")
        return redirect('comments:page_detail', page_id=comment.page.id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            cache.delete(f'page_{comment.page.id}')
            messages.success(request, 'Comment updated successfully!')
            return redirect('comments:page_detail', page_id=comment.page.id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'comments/edit_comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, comment_id):
    """Soft delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)

    if not comment.can_be_deleted_by(request.user):
        messages.error(request, "You can't delete this comment.")
    else:
        comment.is_deleted = True
        comment.save()
        cache.delete(f'page_{comment.page.id}')
        messages.success(request, "Comment deleted.")

    return redirect('comments:page_detail', page_id=comment.page.id)


@login_required
def create_discussion(request):
    """Create a new discussion/page"""
    from .forms import PageForm  # We'll create this form
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user  # You'll need to add this field to Page model
            page.save()
            messages.success(request, 'Discussion created successfully!')
            return redirect('comments:page_detail', page_id=page.id)
    else:
        form = PageForm()
    
    return render(request, 'comments/create_discussion.html', {'form': form})