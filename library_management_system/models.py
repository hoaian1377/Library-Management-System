# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Muonsach(models.Model):
    muonsachid = models.AutoField(db_column='MUONSACHID', primary_key=True)  # Field name made lowercase.
    sachid = models.ForeignKey('Sach', models.DO_NOTHING, db_column='SACHID')  # Field name made lowercase.
    sinhvienid = models.ForeignKey('Sinhvien', models.DO_NOTHING, db_column='SINHVIENID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MUONSACH'


class Nhanvien(models.Model):
    nhanvienid = models.AutoField(db_column='NHANVIENID', primary_key=True)  # Field name made lowercase.
    manv = models.CharField(db_column='MANV', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    hoten = models.CharField(db_column='HOTEN', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sdt = models.CharField(db_column='SDT', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    chucvu = models.CharField(db_column='CHUCVU', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    luong = models.DecimalField(db_column='LUONG', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ngayvaolam = models.DateField(db_column='NGAYVAOLAM', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'NHANVIEN'


class Sach(models.Model):
    sachid = models.AutoField(db_column='SACHID', primary_key=True)  # Field name made lowercase.
    tensach = models.CharField(db_column='TENSACH', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namxuatban = models.IntegerField(db_column='NAMXUATBAN', blank=True, null=True)  # Field name made lowercase.
    nhaxuatban = models.CharField(db_column='NHAXUATBAN', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    soluong = models.IntegerField(db_column='SOLUONG', blank=True, null=True)  # Field name made lowercase.
    theloaiid = models.ForeignKey('Theloai', models.DO_NOTHING, db_column='THELOAIID')  # Field name made lowercase.
    tacgiaid = models.ForeignKey('Tacgia', models.DO_NOTHING, db_column='TACGIAID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SACH'


class Sinhvien(models.Model):
    sinhvienid = models.AutoField(db_column='SINHVIENID', primary_key=True)  # Field name made lowercase.
    mssv = models.CharField(db_column='MSSV', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    hoten = models.CharField(db_column='HOTEN', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    sdt = models.CharField(db_column='SDT', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lophoc = models.CharField(db_column='LOPHOC', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SINHVIEN'


class Tacgia(models.Model):
    tacgiaid = models.AutoField(db_column='TACGIAID', primary_key=True)  # Field name made lowercase.
    tentacgia = models.CharField(db_column='TENTACGIA', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TACGIA'


class Taikhoan(models.Model):
    taikhoanid = models.AutoField(db_column='TAIKHOANID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='USERNAME', unique=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    matkhau = models.CharField(db_column='MATKHAU', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    vaitro = models.CharField(db_column='VAITRO', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    nhanvienid = models.ForeignKey(Nhanvien, models.DO_NOTHING, db_column='NHANVIENID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TAIKHOAN'


class Theloai(models.Model):
    theloaiid = models.AutoField(db_column='THELOAIID', primary_key=True)  # Field name made lowercase.
    tentheloai = models.CharField(db_column='TENTHELOAI', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'THELOAI'
