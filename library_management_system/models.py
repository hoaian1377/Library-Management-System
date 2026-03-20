from django.db import models

class Book(models.Model):
 ma_sach = models.CharField(max_length=20, unique=True)
 ten_sach = models.CharField(max_length=255)
 tac_gia = models.CharField(max_length=255)
 the_loai = models.CharField(max_length=100, blank=True)
 nam_xuat_ban = models.PositiveIntegerField(null=True, blank=True)
 so_luong = models.PositiveIntegerField(default=0)
 mo_ta = models.TextField(blank=True)
 TRANG_THAI_CHOICES = [
    ("available", "Có sẵn"),
    ("borrowed_out", "Đang mượn hết"),
    ("inactive", "Ngưng phát hành"),
    ("damaged", "Mất/Hỏng"),
]
 trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default="available")

 created_at = models.DateTimeField(auto_now_add=True)
 updated_at = models.DateTimeField(auto_now=True)

 class Meta:
    ordering = ["-created_at"]

 def __str__(self):
    return f"{self.ma_sach} - {self.ten_sach}"
