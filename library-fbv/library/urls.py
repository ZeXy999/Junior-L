from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.book_list, name='book-list'),
    path('add/', views.book_create, name='book-create'),
    path('search-ajax/', views.book_search_ajax, name='book-search-ajax'),
    path('<int:pk>/', views.book_detail, name='book-detail'),
    path('<int:pk>/edit/', views.book_update, name='book-edit'),
    path('<int:pk>/delete/', views.book_delete, name='book-delete'),
    path('<int:pk>/toggle-availability/', views.book_toggle_availability,
         name='book-toggle-availability'),
]
