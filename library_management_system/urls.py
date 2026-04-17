from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/delete/', views.book_delete, name='book_delete'),
    path('books/update/', views.book_update, name='book_update'),
    path('borrows/', views.borrows, name='borrows'),
    path('borrow/create/', views.borrow_books, name='borrow_books'),
    path('borrow/reutrn/', views.book_return, name='book_return'),
    path('borrow/detail/<int:phieu_id>/', views.borrow_detail, name='borrow_detail'),
    path('borrowers/', views.borrower, name='borrower'),
    path('reports/', views.report, name='report'),
    path('login/', views.login_view, name='login_modal'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/verify/', views.forgot_password_verify_view, name='forgot_password_verify'),
    path('forgot-password/reset/', views.forgot_password_reset_view, name='forgot_password_reset'),
    path('logout/', views.logout_view, name='logout')
]
