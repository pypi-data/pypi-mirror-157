from django.urls import path

from bugtrack import views

urlpatterns = [
    path('bug/', views.bugs, name='bugs'),
    path('bug/new/', views.bug_new, name='bug_new'),
    path('bug/<int:bug_id>)/', views.bug, name='bug'),
    path('bug/<int:bug_id>/edit/', views.bug_edit, name='bug_edit'),
    path('download_document/<int:document_id>/', \
            views.download_document, name='download_document'),
    path('ajax_get_category_select/', views.ajax_get_category_select, \
            name='ajax_get_category_select'),
]