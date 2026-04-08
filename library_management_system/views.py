from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Taikhoan, Sach
# Create your views here.
def base(request):
    return render(request,'base.html')
def borrow(request):
    return render(request,'borrow.html')
def borrower(request):
    return render(request,'borrower.html')
def report(request):
    return render(request,'report.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = Taikhoan.objects.filter(username=username, matkhau=password).first()
        if user:
            request.session['user'] = username
            return redirect('base')
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")

    return render(request, "login_modal.html")
  
def logout_view(request):
    request.session.flush()
    return redirect('base')


######################### Sach #######################

def book_list(request):
    books = Sach.objects.select_related('tacgiaid').all()

    # SEARCH
    keyword = request.GET.get('q')
    if keyword:
        books = books.filter(ten_sach__icontains=keyword)

    return render(request, 'book.html', {
        'books': books
    })
