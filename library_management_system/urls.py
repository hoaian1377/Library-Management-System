from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('books/', views.book_list, name='book_list'),
    path('borrows/', views.borrow, name='borrow'),
    path('borrowers/', views.borrower, name='borrower'),
    path('reports/', views.report, name='report'),
    path('login/', views.login_view, name='login_modal'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/verify/', views.forgot_password_verify_view, name='forgot_password_verify'),
    path('forgot-password/reset/', views.forgot_password_reset_view, name='forgot_password_reset'),
    path('logout/', views.logout_view, name='logout')
]
