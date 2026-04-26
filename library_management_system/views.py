from datetime import date
from functools import wraps
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction, connection
from django.db.models import Max, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Nhanvien, Sach, Taikhoan, Tacgia, Theloai, Sinhvien


ROLE_LABELS = {
    'admin': 'Quản trị viên',
    'staff': 'Nhân viên thư viện',
    'manager': 'Quản lý thư viện',
}

ROLE_PERMISSIONS = {
    'admin': {'books', 'borrows', 'borrowers', 'reports'},
    'staff': {'books', 'borrows', 'borrowers'},
    'manager': {'books', 'borrows', 'borrowers', 'reports'},
}


def _build_url(route_name, **params):
    url = reverse(route_name)
    filtered_params = {key: value for key, value in params.items() if value is not None}
    if not filtered_params:
        return url
    return f"{url}?{urlencode(filtered_params)}"


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _normalize_role(role):
    normalized = (role or 'staff').strip().lower()
    return normalized if normalized in ROLE_PERMISSIONS else 'staff'


def _get_role_label(role):
    return ROLE_LABELS.get(_normalize_role(role), 'Người dùng')


def _get_permissions(role):
    return ROLE_PERMISSIONS.get(_normalize_role(role), ROLE_PERMISSIONS['staff'])


def _hydrate_session_permissions(request):
    if not request.session.get('user'):
        return

    role = _normalize_role(request.session.get('role'))
    permissions = sorted(_get_permissions(role))
    request.session['role'] = role
    request.session['role_label'] = _get_role_label(role)
    request.session['permission_count'] = len(permissions)
    request.session['permissions'] = permissions


def _json_or_redirect(request, ok, message, *, redirect_to='base', modal=None, status=200, extra=None):
    if _is_ajax(request):
        payload = {'ok': ok, 'message': message}
        if extra:
            payload.update(extra)
        return JsonResponse(payload, status=status)

    if message:
        feedback = messages.success if ok else messages.error
        feedback(request, message)

    return redirect(_build_url(redirect_to, auth=modal))


def _require_session_auth(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.session.get('user'):
            _hydrate_session_permissions(request)
            return view_func(request, *args, **kwargs)

        messages.info(request, "Vui lòng đăng nhập để sử dụng chức năng này.")
        return redirect(_build_url('base', auth='login'))

    return wrapped


def _require_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        @_require_session_auth
        def wrapped(request, *args, **kwargs):
            role = _normalize_role(request.session.get('role'))
            if permission in _get_permissions(role):
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                f"Vai trò {_get_role_label(role).lower()} không có quyền truy cập khu vực này."
            )
            return redirect('base')

        return wrapped

    return decorator


def _generate_employee_code():
    next_id = (Nhanvien.objects.aggregate(max_id=Max('nhanvienid')).get('max_id') or 0) + 1
    code = f"NV{next_id:03d}"
    while Nhanvien.objects.filter(manv=code).exists():
        next_id += 1
        code = f"NV{next_id:03d}"
    return code


def _account_matches_password(account, raw_password):
    stored_password = account.matkhau or ''

    try:
        if check_password(raw_password, stored_password):
            return True
    except ValueError:
        pass

    if stored_password == raw_password:
        account.matkhau = make_password(raw_password)
        account.save(update_fields=['matkhau'])
        return True

    return False


def _store_session_user(request, account, remember_me=False):
    role = _normalize_role(account.vaitro)
    permissions = sorted(_get_permissions(role))
    request.session.cycle_key()
    request.session['user'] = account.username
    request.session['display_name'] = account.nhanvienid.hoten
    request.session['role'] = role
    request.session['role_label'] = _get_role_label(role)
    request.session['permission_count'] = len(permissions)
    request.session['permissions'] = permissions
    request.session['user_id'] = account.taikhoanid

    if remember_me:
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        request.session.set_expiry(0)


def _get_account_by_email(email):
    return (
        Taikhoan.objects.select_related('nhanvienid')
        .filter(nhanvienid__email__iexact=email)
        .first()
    )


def base(request):
    _hydrate_session_permissions(request)
    return render(request, 'base.html')


@_require_permission('borrows')
def borrow(request):
    return render(request, 'borrow.html')


@_require_permission('borrowers')
def borrower(request):
    return render(request, 'borrower.html')





def login_view(request):
    if request.method != "POST":
        return redirect(_build_url('base', auth='login'))

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    remember_me = request.POST.get("remember_me") == "on"
    user = Taikhoan.objects.select_related('nhanvienid').filter(username=username).first()

    if user and _account_matches_password(user, password):
        _store_session_user(request, user, remember_me=remember_me)
        messages.success(request, f"Chào mừng {user.nhanvienid.hoten} quay lại.")
        return redirect('base')

    messages.error(request, "Sai tài khoản hoặc mật khẩu.")
    return redirect(_build_url('base', auth='login'))


def register_view(request):
    if request.method != "POST":
        return redirect(_build_url('base', auth='register'))

    role = request.session.get('role')
    if role not in ['admin', 'manager']:
        return _json_or_redirect(
            request,
            False,
            "Chỉ Quản lý hoặc Admin mới được phép cấp tài khoản.",
            modal='register',
            status=403,
        )

    full_name = request.POST.get("full_name", "").strip()
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    phone = request.POST.get("phone", "").strip()
    password = request.POST.get("password", "")
    confirm_password = request.POST.get("confirm_password", "")

    if not all([full_name, username, email, phone, password, confirm_password]):
        return _json_or_redirect(
            request,
            False,
            "Vui lòng nhập đầy đủ thông tin đăng ký.",
            modal='register',
            status=400,
        )

    if password != confirm_password:
        return _json_or_redirect(
            request,
            False,
            "Mật khẩu xác nhận không khớp.",
            modal='register',
            status=400,
        )

    if len(password) < 6:
        return _json_or_redirect(
            request,
            False,
            "Mật khẩu phải có ít nhất 6 ký tự.",
            modal='register',
            status=400,
        )

    if Taikhoan.objects.filter(username=username).exists():
        return _json_or_redirect(
            request,
            False,
            "Tên đăng nhập đã tồn tại.",
            modal='register',
            status=400,
        )

    if _get_account_by_email(email):
        return _json_or_redirect(
            request,
            False,
            "Email này đã được dùng cho tài khoản khác.",
            modal='register',
            status=400,
        )

    with transaction.atomic():
        nhanvien = Nhanvien.objects.create(
            manv=_generate_employee_code(),
            hoten=full_name,
            email=email,
            sdt=phone,
            chucvu="Thành viên",
            ngayvaolam=date.today(),
        )
        Taikhoan.objects.create(
            username=username,
            matkhau=make_password(password),
            vaitro="staff",
            nhanvienid=nhanvien,
        )

    return _json_or_redirect(
        request,
        True,
        "Đăng ký tài khoản thành công. Vui lòng đăng nhập.",
        modal='login',
        extra={'openModal': 'login'},
    )


def forgot_password_verify_view(request):
    if request.method != "POST":
        return redirect(_build_url('base', auth='forgot'))

    email = request.POST.get("email", "").strip().lower()
    account = _get_account_by_email(email)

    if not account:
        return _json_or_redirect(
            request,
            False,
            "Không tìm thấy tài khoản theo email này.",
            modal='forgot',
            status=404,
        )

    return _json_or_redirect(
        request,
        True,
        "Email hợp lệ. Bạn có thể đặt lại mật khẩu.",
        modal='forgot',
        extra={'email': account.nhanvienid.email},
    )


def forgot_password_reset_view(request):
    if request.method != "POST":
        return redirect(_build_url('base', auth='forgot'))

    email = request.POST.get("email", "").strip().lower()
    new_password = request.POST.get("new_password", "")
    confirm_password = request.POST.get("confirm_password", "")

    if not email:
        return _json_or_redirect(
            request,
            False,
            "Thiếu email xác thực để đặt lại mật khẩu.",
            modal='forgot',
            status=400,
        )

    if new_password != confirm_password:
        return _json_or_redirect(
            request,
            False,
            "Mật khẩu xác nhận không khớp.",
            modal='forgot',
            status=400,
        )

    if len(new_password) < 6:
        return _json_or_redirect(
            request,
            False,
            "Mật khẩu mới phải có ít nhất 6 ký tự.",
            modal='forgot',
            status=400,
        )

    account = _get_account_by_email(email)
    if not account:
        return _json_or_redirect(
            request,
            False,
            "Không tìm thấy tài khoản theo email này.",
            modal='forgot',
            status=404,
        )

    account.matkhau = make_password(new_password)
    account.save(update_fields=['matkhau'])

    return _json_or_redirect(
        request,
        True,
        "Đổi mật khẩu thành công. Vui lòng đăng nhập lại.",
        modal='login',
        extra={'openModal': 'login'},
    )


def logout_view(request):
    request.session.flush()
    messages.success(request, "Bạn đã đăng xuất.")
    return redirect('base')


@_require_permission('books')
def book_list(request):
    books = Sach.objects.select_related('tacgiaid', 'theloaiid').all().order_by('sachid')

    keyword = request.GET.get('q', '').strip()
    if keyword:
        books = books.filter(tensach__icontains=keyword)

    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        books = books.filter(theloaiid__theloaiid=selected_category)

    selected_author = request.GET.get('author', '').strip()
    if selected_author:
        books = books.filter(tacgiaid__tacgiaid=selected_author)

    authors = Tacgia.objects.all().order_by('tentacgia')
    categories = Theloai.objects.all().order_by('tentheloai')
    return render(request, 'book.html', {
        'books': books,
        'keyword': keyword,
        'selected_category': selected_category,
        'selected_author': selected_author,
        'authors': authors,
        'categories': categories,
    })

def book_add(request):
    if request.method== "POST":
        tensach= request.POST.get("tensach")
        tentheloai= request.POST.get('tentheloai')
        tentacgia=request.POST.get("tentacgia")
        soluong=request.POST.get("soluong")
        namxuatban = request.POST.get("namxuatban")
        nhaxuatban = request.POST.get("nhaxuatban")
        try:
            tacgia = Tacgia.objects.filter(tentacgia=tentacgia).first()
            if not tacgia:
                tacgia = Tacgia.objects.create(tentacgia=tentacgia)

            # 🔥 tìm hoặc tạo thể loại
            theloai = Theloai.objects.filter(tentheloai=tentheloai).first()
            if not theloai:
                theloai = Theloai.objects.create(tentheloai=tentheloai)
            with connection.cursor() as cursor:
                cursor.execute("""
                        EXEC SP_THEMSACH %s, %s, %s, %s, %s, %s
                            """,[tensach, namxuatban, nhaxuatban, soluong, theloai.theloaiid, tacgia.tacgiaid,])
                row = cursor.fetchone()
                sach_id=row[0] if row else None
            messages.success(request, f"Thêm sách thành công! ID = {sach_id}")
            return redirect('book_list')

        except Exception as e:
            print("ERROR:", e)
            messages.error(request, f"Lỗi: {str(e)}")
    return redirect('book_list')

def book_delete(request):
    if request.method == 'POST':
        sachid = request.POST.get('sachid')

        with connection.cursor() as cursor:
            cursor.execute("EXEC SP_XOASACH @SACHID=%s", [sachid])

    return redirect('book_list')

def book_update(request):
    if request.method == "POST":
        sachid = request.POST.get("sachid")
        tensach = request.POST.get("tensach")
        namxuatban = request.POST.get("namxuatban")
        nhaxuatban = request.POST.get("nhaxuatban")
        soluong = request.POST.get("soluong")

        if not sachid:
            return redirect('book_list')

        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC SP_CAPNHATSACH %s, %s, %s, %s, %s",
                [sachid, tensach, namxuatban, nhaxuatban, soluong]
            )

        return redirect('book_list')
    
    
@_require_permission('borrows')
def borrows(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                pm.PHIEUMUONID,
                sv.HOTEN,
                pm.NGAYMUON,
                pm.NGAYTRA,
                pm.TRANGTHAI
            FROM PHIEUMUON pm
            JOIN SINHVIEN sv ON pm.SINHVIENID = sv.SINHVIENID
            ORDER BY pm.PHIEUMUONID DESC
        """)

        borrows = [
            {
                "id": row[0],
                "hoten": row[1],
                "ngaymuon": row[2],
                "ngaytra": row[3],
                "trangthai": row[4],
                "tensach": "Nhiều sách"   # 👈 fix luôn chỗ này
            }
            for row in cursor.fetchall()
        ]

    # load books cho form (giữ nguyên)
    with connection.cursor() as cursor:
        cursor.execute("SELECT SACHID, TENSACH FROM SACH")
        books = [{"sachid": r[0], "tensach": r[1]} for r in cursor.fetchall()]

    return render(request, "borrow.html", {
        "books": books,
        "borrows": borrows
    })

def borrow_books(request):
    if request.method == 'POST':
        try:
            mssv = request.POST.get('mssv', '').strip()
            ngaytra = request.POST.get('ngaytra')
            username = request.session.get('user')

            if not username:
                raise Exception("Chưa đăng nhập")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT NHANVIENID 
                    FROM TAIKHOAN 
                    WHERE USERNAME = %s
                """, [username])

                row = cursor.fetchone()

                if not row:
                    raise Exception("Không tìm thấy nhân viên")

                nhanvien_id = row[0]

            if not mssv:
                raise Exception("Vui lòng nhập MSSV")

            sach_ids = request.POST.getlist('sach_id[]')
            soluongs = request.POST.getlist('soluong[]')

            if not sach_ids or not any(sach_ids):
                raise Exception("Phải chọn ít nhất 1 sách")

            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT SINHVIENID FROM SINHVIEN WHERE MSSV = %s",
                        [mssv]
                    )
                    row = cursor.fetchone()

                    if not row:
                        raise Exception("MSSV không tồn tại!")

                    sinhvien_id = row[0]
                    cursor.execute(
                        "EXEC SP_MUONSACH %s, %s, %s",
                        [sinhvien_id, nhanvien_id, ngaytra]
                    )
                    phieu_id = cursor.fetchone()[0]

                    for sach_id, soluong in zip(sach_ids, soluongs):
                        if not sach_id or not soluong:
                            continue

                        soluong = int(soluong)

                        if soluong <= 0:
                            raise Exception("Số lượng phải > 0")

                        cursor.execute(
                            "EXEC SP_THEM_SACH_VAO_PHIEU %s, %s, %s",
                            [phieu_id, int(sach_id), soluong]
                        )

            messages.success(request, "Tạo phiếu mượn thành công!")

        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")

        return redirect('borrows')
    


@require_POST
def book_return(request):
    phieu_id = request.POST.get('phieu_id')  

    if not phieu_id:
        messages.error(request, "Thiếu mã phiếu mượn!")
        return redirect('borrows')

    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC SP_TRASACH %s", [phieu_id])

        messages.success(request, "Đã trả sách thành công!")

    except Exception as e:
        messages.error(request, f"Lỗi: {str(e)}")

    return redirect('borrows')

def borrow_detail(request, phieu_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                SV.MSSV,
                SV.HOTEN,
                S.TENSACH,
                CT.SOLUONG
            FROM PHIEUMUON PM
            JOIN SINHVIEN SV ON PM.SINHVIENID = SV.SINHVIENID
            JOIN CT_PHIEUMUON CT ON PM.PHIEUMUONID = CT.PHIEUMUONID
            JOIN SACH S ON CT.SACHID = S.SACHID
            WHERE PM.PHIEUMUONID = %s
        """, [phieu_id])

        data = [
            {
                "mssv": row[0],
                "hoten": row[1],
                "tensach": row[2],
                "soluong": row[3],
            }
            for row in cursor.fetchall()
        ]

    return JsonResponse({"data": data})





def borrower_add(request):
    if request.method == "POST":
        try:
            mssv = request.POST.get("mssv")
            hoten = request.POST.get("hoten")
            email = request.POST.get("email")
            sdt = request.POST.get("sdt")
            lop = request.POST.get("lop")

            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO SINHVIEN (MSSV, HOTEN, EMAIL, SDT, LOP, TRANGTHAI)
                    VALUES (%s, %s, %s, %s, %s, 1)
                """, [mssv, hoten, email, sdt, lop])

            messages.success(request, "Thêm sinh viên thành công")

        except Exception as e:
            messages.error(request, f"Lỗi: {str(e)}")

    return redirect('borrower')

def borrower(request):
    keyword = request.GET.get('keyword', '')

    # 🔍 Tìm kiếm
    sinhviens = Sinhvien.objects.all()
    if keyword:
        sinhviens = sinhviens.filter(
            Q(mssv__icontains=keyword) |
            Q(hoten__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(lophoc__icontains=keyword)
        )

    if request.method == 'POST':
        action = request.POST.get('action')

        mssv = request.POST.get('mssv')
        hoten = request.POST.get('hoten')
        email = request.POST.get('email')
        sdt = request.POST.get('sdt')
        lophoc = request.POST.get('lophoc')

        try:
            if action == 'add':
                Sinhvien.objects.create(
                    mssv=mssv,
                    hoten=hoten,
                    email=email,
                    sdt=sdt,
                    lophoc=lophoc
                )
                messages.success(request, "Thêm người mượn thành công!")
            elif action == 'update':
                sv = get_object_or_404(Sinhvien, mssv=mssv)
                sv.hoten = hoten
                sv.email = email
                sv.sdt = sdt
                sv.lophoc = lophoc
                sv.save()
                messages.success(request, "Cập nhật người mượn thành công!")
            elif action == 'delete':
                sv = get_object_or_404(Sinhvien, mssv=mssv)
                sv.delete()
                messages.success(request, "Xóa người mượn thành công!")
        except Exception as e:
            error_msg = str(e)
            if 'UNIQUE KEY constraint' in error_msg:
                messages.error(request, f"Lỗi: Mã số '{mssv}' đã tồn tại trong hệ thống!")
            elif 'REFERENCE constraint' in error_msg:
                messages.error(request, "Lỗi: Không thể xóa người mượn này vì đang có phiếu mượn sách!")
            else:
                messages.error(request, f"Lỗi: {error_msg}")

        return redirect('borrower')

    context = {
        'sinhviens': sinhviens,
        'keyword': keyword
    }

    return render(request, 'borrower.html', context)
