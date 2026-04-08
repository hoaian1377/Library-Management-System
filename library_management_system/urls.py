from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('books/', views.book_list, name='book_list'),
    path('borrows/', views.borrow, name='borrow'),
    path('borrowers/', views.borrower, name='borrower'),
    path('reports/', views.report, name='report'),
    path('login/', views.login_view, name='login_modal'),
    path('logout/', views.logout_view, name='logout')
]
