from django.shortcuts import render
from django.http import HttpResponse
from .models import Book
# Create your views here.
def base(request):
    return render(request,'base.html')
def book(request):
    books = Book.objects.all() # Lấy tất cả sách từ database
    return render(request,'book.html' , {'books': books}) # Truyền qua HTML
def borrow(request):
    return render(request,'borrow.html')
def borrower(request):
    return render(request,'borrower.html')
def report(request):
    return render(request,'report.html')
