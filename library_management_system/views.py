from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def base(request):
    return render(request,'base.html')
def book(request):
    return render(request,'book.html')
def borrow(request):
    return render(request,'borrow.html')
def borrower(request):
    return render(request,'borrower.html')
def report(request):
    return render(request,'report.html')