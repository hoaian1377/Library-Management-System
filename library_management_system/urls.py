from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('books/', views.book, name='book'),
    path('borrows/', views.borrow, name='borrow'),
    path('borrowers/', views.borrower, name='borrower'),
    path('reports/', views.report, name='report'),
]
