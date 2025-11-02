# comments/urls.py

from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('page/<int:page_id>/', views.page_detail, name='page_detail'),
    path('page/<int:page_id>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/vote/', views.vote_comment, name='vote_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('signup/', views.signup, name='signup'),
    path('create/', views.create_discussion, name='create_discussion'), 
]
