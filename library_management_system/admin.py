from django.contrib import admin
from .models import Book
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
 list_display = ("ma_sach", "ten_sach", "tac_gia", "so_luong", "trang_thai", "updated_at")
 search_fields = ("ma_sach", "ten_sach", "tac_gia")
 list_filter = ("trang_thai", "the_loai")
 ordering = ("-updated_at",)  
# Register your models here.
