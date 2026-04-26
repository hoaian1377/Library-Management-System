CREATE DATABASE QLS
GO
USE QLS
GO

CREATE TABLE SINHVIEN
(
	SINHVIENID INT PRIMARY KEY IDENTITY(1,1) NOT NULL,
	MSSV VARCHAR(50) NOT NULL UNIQUE,
	HOTEN NVARCHAR(255) NOT NULL,
	EMAIL VARCHAR(50),
	SDT VARCHAR(10),
	LOPHOC VARCHAR(50) NOT NULL
);

CREATE TABLE THELOAI
(
	THELOAIID INT PRIMARY KEY IDENTITY(1,1) NOT NULL,
	TENTHELOAI NVARCHAR(255) NOT NULL UNIQUE 
)

CREATE TABLE TACGIA
(
	TACGIAID INT PRIMARY KEY IDENTITY(1,1) NOT NULL ,
	TENTACGIA NVARCHAR(255) NOT NULL
)

CREATE TABLE SACH
(
	SACHID INT PRIMARY KEY IDENTITY(1,1) NOT NULL,
	TENSACH NVARCHAR(255) NOT NULL UNIQUE,
	NAMXUATBAN INT,
	NHAXUATBAN NVARCHAR(255),
	SOLUONG INT CHECK(SOLUONG >=0),
	THELOAIID INT NOT NULL,
	TACGIAID INT NOT NULL,
	FOREIGN KEY(THELOAIID) REFERENCES THELOAI(THELOAIID),
	FOREIGN KEY(TACGIAID) REFERENCES TACGIA(TACGIAID)
) 


CREATE TABLE NHANVIEN (
    NHANVIENID INT PRIMARY KEY IDENTITY(1,1) NOT NULL,
    MANV VARCHAR(50) NOT NULL UNIQUE,
    HOTEN NVARCHAR(255) NOT NULL,
    EMAIL VARCHAR(100),
    SDT VARCHAR(10),
    CHUCVU NVARCHAR(100), 
    LUONG DECIMAL(10,2),
    NGAYVAOLAM DATE
);

CREATE TABLE TAIKHOAN (
    TAIKHOANID INT PRIMARY KEY IDENTITY(1,1) NOT NULL,
    USERNAME VARCHAR(50) NOT NULL UNIQUE,
    MATKHAU VARCHAR(255) NOT NULL,
	VAITRO NVARCHAR(50) NOT NULL,
    NHANVIENID INT NOT NULL,

    FOREIGN KEY (NHANVIENID) REFERENCES NHANVIEN(NHANVIENID)
);

CREATE TABLE PHIEUMUON
(
    PHIEUMUONID INT PRIMARY KEY IDENTITY(1,1),
    SINHVIENID INT NOT NULL,
    NHANVIENID INT NOT NULL,
    NGAYMUON DATETIME DEFAULT GETDATE(),
    NGAYTRA DATE,
    TRANGTHAI NVARCHAR(50),

    FOREIGN KEY(SINHVIENID) REFERENCES SINHVIEN(SINHVIENID),
    FOREIGN KEY(NHANVIENID) REFERENCES NHANVIEN(NHANVIENID)
);

CREATE TABLE CT_PHIEUMUON
(
    ID INT PRIMARY KEY IDENTITY(1,1),
    PHIEUMUONID INT,
    SACHID INT,
    SOLUONG INT DEFAULT 1,

    FOREIGN KEY(PHIEUMUONID) REFERENCES PHIEUMUON(PHIEUMUONID),
    FOREIGN KEY(SACHID) REFERENCES SACH(SACHID)
);
GO

CREATE TRIGGER TRG_KIEMTRATHEMSACH
ON SACH
AFTER INSERT 
AS
BEGIN
	SET NOCOUNT ON;
	-- check số lượng sách --
	IF EXISTS(
		SELECT 1 
		FROM inserted 
		WHERE SOLUONG <0
		)
	BEGIN 
		RAISERROR (N'Số lượng sách không hợp lệ vui lòng nhập lại!',16,1);
		ROLLBACK TRANSACTION;
		RETURN;
	END
	-- kiểm tra tên rỗng  --
	IF EXISTS(
		SELECT 1
		FROM inserted 
		WHERE TENSACH IS NULL OR LTRIM(RTRIM(TENSACH)) = ''
		)
	BEGIN 
		RAISERROR ( N'Tên sách không hợp lệ!',16,1)
		ROLLBACK TRANSACTION;
		RETURN;
	END;
	-- check năm xuất bản --
	IF EXISTS(
		SELECT 1
		FROM inserted
		WHERE NAMXUATBAN < 1473 OR NAMXUATBAN > YEAR(GETDATE())
		)
	BEGIN 
		RAISERROR( N'Năm nhập vào không hợp lệ!',16,1);
		ROLLBACK TRANSACTION;
		RETURN;
	END;

	IF EXISTS (
		SELECT 1
		FROM SACH s
		JOIN inserted i 
			ON LOWER(s.TENSACH) = LOWER(i.TENSACH)
		   AND s.TACGIAID = i.TACGIAID
		   AND s.SACHID <> i.SACHID
	)
	BEGIN
		RAISERROR( N'Sách đã tồn tại!',16,1);
		ROLLBACK TRANSACTION;
		RETURN;
	END;

END;
GO

CREATE TRIGGER TRG_KIEMTRACAPNHATSACH
ON SACH
AFTER UPDATE
AS
BEGIN
	SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM inserted
        WHERE TENSACH IS NULL OR LTRIM(RTRIM(TENSACH)) = ''
    )
    BEGIN
        RAISERROR (N'Tên sách không hợp lệ!',16,1);
        ROLLBACK TRANSACTION;
        RETURN;
    END
END;
GO 

CREATE TRIGGER TRG_KIEMTRAXOASACH
ON SACH
INSTEAD OF DELETE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS(
        SELECT 1
        FROM deleted d
        JOIN CT_PHIEUMUON ct ON d.SACHID = ct.SACHID
    )
    BEGIN
        RAISERROR (N'Không thể xóa sách đang có trong phiếu mượn!',16,1);
        RETURN;
    END;

    DELETE FROM SACH
    WHERE SACHID IN (SELECT SACHID FROM deleted);
END;
GO

CREATE PROCEDURE SP_THEMSACH
	@TENSACH NVARCHAR(255),
	@NAMXUATBAN INT,
	@NHAXUATBAN NVARCHAR(255),
	@SOLUONG INT,
	@THELOAIID INT,
	@TACGIAID INT
AS 
BEGIN 
	SET NOCOUNT ON;
	IF EXISTS (
        SELECT 1 FROM SACH
        WHERE LOWER(TENSACH) = LOWER(@TENSACH)
          AND TACGIAID = @TACGIAID
    )
    BEGIN
        UPDATE SACH
        SET SOLUONG = SOLUONG + @SOLUONG
        WHERE LOWER(TENSACH) = LOWER(@TENSACH)
          AND TACGIAID = @TACGIAID;

        RETURN;
    END

	INSERT INTO SACH(TENSACH, NAMXUATBAN, NHAXUATBAN, SOLUONG, THELOAIID, TACGIAID)
	VALUES (@TENSACH, @NAMXUATBAN, @NHAXUATBAN, @SOLUONG, @THELOAIID, @TACGIAID);

	SELECT SCOPE_IDENTITY() AS SACHID;
END;
GO

CREATE PROCEDURE SP_THEMTHELOAI
	@TENTHELOAI NVARCHAR(255)
AS
BEGIN
	SET NOCOUNT ON;
	INSERT INTO THELOAI(TENTHELOAI)
	VALUES (@TENTHELOAI)

	SELECT SCOPE_IDENTITY() AS THELOAIID;
END;
GO

CREATE PROCEDURE SP_THEMTACGIA
	@TENTACGIA NVARCHAR(255)
AS 
BEGIN
	SET NOCOUNT ON;
	INSERT INTO TACGIA(TENTACGIA)
	VALUES (@TENTACGIA)

	SELECT SCOPE_IDENTITY() AS TACGIAID
END;
GO

CREATE PROCEDURE SP_XOASACH
	@SACHID INT
AS 
BEGIN
	SET NOCOUNT ON;
	DELETE FROM SACH
	WHERE SACHID = @SACHID;
	
	PRINT N' Xóa sách thành công!'
END;
GO

CREATE PROCEDURE SP_CAPNHATSACH
    @SACHID INT,
    @TENSACH NVARCHAR(255),
    @NAMXUATBAN INT,
    @NHAXUATBAN NVARCHAR(255),
    @SOLUONG INT
AS
BEGIN
    UPDATE SACH
    SET TENSACH = @TENSACH,
        NAMXUATBAN = @NAMXUATBAN,
        NHAXUATBAN = @NHAXUATBAN,
        SOLUONG = @SOLUONG
    WHERE SACHID = @SACHID
END
GO

CREATE PROCEDURE SP_MUONSACH
    @SINHVIENID INT,
    @NHANVIENID INT,
    @NGAYTRA DATE
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO PHIEUMUON(SINHVIENID, NHANVIENID, NGAYTRA, TRANGTHAI)
    VALUES (@SINHVIENID, @NHANVIENID, @NGAYTRA, N'Đang mượn');

    SELECT SCOPE_IDENTITY() AS PHIEUID;
END;
GO 

CREATE PROCEDURE SP_THEM_SACH_VAO_PHIEU
    @PHIEUMUONID INT,
    @SACHID INT,
    @SOLUONG INT
AS
BEGIN
    SET NOCOUNT ON;

    -- check tồn tại
    IF NOT EXISTS (SELECT 1 FROM SACH WHERE SACHID = @SACHID)
    BEGIN
        RAISERROR(N'Sách không tồn tại!',16,1);
        RETURN;
    END

    -- check tồn kho
    IF EXISTS (
        SELECT 1 FROM SACH
        WHERE SACHID = @SACHID AND SOLUONG < @SOLUONG
    )
    BEGIN
        RAISERROR(N'Không đủ sách!',16,1);
        RETURN;
    END

    -- trừ kho
    UPDATE SACH
    SET SOLUONG = SOLUONG - @SOLUONG
    WHERE SACHID = @SACHID;

    -- gộp nếu trùng
    IF EXISTS (
        SELECT 1 FROM CT_PHIEUMUON
        WHERE PHIEUMUONID = @PHIEUMUONID AND SACHID = @SACHID
    )
    BEGIN
        UPDATE CT_PHIEUMUON
        SET SOLUONG = SOLUONG + @SOLUONG
        WHERE PHIEUMUONID = @PHIEUMUONID AND SACHID = @SACHID
    END
    ELSE
    BEGIN
        INSERT INTO CT_PHIEUMUON(PHIEUMUONID, SACHID, SOLUONG)
        VALUES (@PHIEUMUONID, @SACHID, @SOLUONG)
    END
END;
GO

CREATE PROCEDURE SP_TRASACH
    @PHIEUMUONID INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (
        SELECT 1 FROM dbo.PHIEUMUON WHERE PHIEUMUONID = @PHIEUMUONID
    )
    BEGIN
        RAISERROR(N'Phiếu không tồn tại!',16,1);
        RETURN;
    END

    IF EXISTS (
        SELECT 1 
        FROM dbo.PHIEUMUON
        WHERE PHIEUMUONID = @PHIEUMUONID 
          AND TRANGTHAI = N'Đã trả'
    )
    BEGIN
        RAISERROR(N'Phiếu này đã trả rồi!',16,1);
        RETURN;
    END

    UPDATE S
    SET S.SOLUONG = S.SOLUONG + CT.SOLUONG
    FROM dbo.SACH S
    JOIN dbo.CT_PHIEUMUON CT 
        ON S.SACHID = CT.SACHID
    WHERE CT.PHIEUMUONID = @PHIEUMUONID
    UPDATE dbo.PHIEUMUON
    SET TRANGTHAI = N'Đã trả'
    WHERE PHIEUMUONID = @PHIEUMUONID;

END;
GO

EXEC SP_THEMTHELOAI N'Công nghệ thông tin';
EXEC SP_THEMTHELOAI N'Kinh tế';
EXEC SP_THEMTHELOAI N'Tâm lý học';
EXEC SP_THEMTHELOAI N'Tiểu thuyết';
EXEC SP_THEMTHELOAI N'Khoa học';
EXEC SP_THEMTHELOAI N'Lịch sử';
EXEC SP_THEMTHELOAI N'Giáo dục';
EXEC SP_THEMTHELOAI N'Văn học';
EXEC SP_THEMTHELOAI N'Kỹ năng sống';
EXEC SP_THEMTHELOAI N'Thiếu nhi';

EXEC SP_THEMTACGIA N'Nguyễn Nhật Ánh';
EXEC SP_THEMTACGIA N'Trần Đăng Khoa';
EXEC SP_THEMTACGIA N'Lê Minh Khuê';
EXEC SP_THEMTACGIA N'Nguyễn Ngọc Tư';
EXEC SP_THEMTACGIA N'Bảo Ninh';
EXEC SP_THEMTACGIA N'Nguyễn Huy Thiệp';
EXEC SP_THEMTACGIA N'Phan Việt';
EXEC SP_THEMTACGIA N'Dương Thu Hương';
EXEC SP_THEMTACGIA N'Tô Hoài';
EXEC SP_THEMTACGIA N'Nam Cao';
EXEC SP_THEMTACGIA N'Xuân Diệu';
EXEC SP_THEMTACGIA N'Hàn Mặc Tử';
EXEC SP_THEMTACGIA N'Nguyễn Du';
EXEC SP_THEMTACGIA N'Hồ Xuân Hương';
EXEC SP_THEMTACGIA N'Chế Lan Viên';
EXEC SP_THEMTACGIA N'Nguyễn Tuân';
EXEC SP_THEMTACGIA N'Vũ Trọng Phụng';
EXEC SP_THEMTACGIA N'Thạch Lam';
EXEC SP_THEMTACGIA N'Nguyễn Công Hoan';
EXEC SP_THEMTACGIA N'Ma Văn Kháng';

INSERT INTO SACH (TENSACH, NAMXUATBAN, NHAXUATBAN, SOLUONG, THELOAIID, TACGIAID)
VALUES
(N'Lập trình C cơ bản', 2010, N'NXB Giáo Dục', 5, 1, 1),
(N'Học Python nâng cao', 2018, N'NXB Trẻ', 10, 1, 2),
(N'Cấu trúc dữ liệu', 2015, N'NXB Giáo Dục', 7, 1, 3),
(N'Kinh tế vi mô', 2012, N'NXB Lao Động', 6, 2, 4),
(N'Kinh tế vĩ mô', 2016, N'NXB Lao Động', 8, 2, 5),
(N'Tâm lý học hành vi', 2019, N'NXB Văn Học', 9, 3, 6),
(N'Đắc nhân tâm', 2005, N'NXB Trẻ', 15, 9, 7),
(N'Mắt biếc', 2010, N'NXB Trẻ', 12, 4, 1),
(N'Dế mèn phiêu lưu ký', 2000, N'NXB Kim Đồng', 20, 10, 9),
(N'Số đỏ', 2008, N'NXB Văn Học', 11, 8, 17),

(N'Giáo trình Java', 2014, N'NXB Giáo Dục', 9, 1, 10),
(N'AI cơ bản', 2020, N'NXB Khoa Học', 6, 1, 11),
(N'Kỹ năng giao tiếp', 2017, N'NXB Trẻ', 13, 9, 12),
(N'Khởi nghiệp', 2019, N'NXB Lao Động', 7, 2, 13),
(N'Tâm lý học đám đông', 2013, N'NXB Văn Học', 6, 3, 14),
(N'Chiến tranh và hòa bình', 2001, N'NXB Văn Học', 4, 6, 15),
(N'Giáo dục hiện đại', 2018, N'NXB Giáo Dục', 5, 7, 16),
(N'Văn học Việt Nam', 2012, N'NXB Văn Học', 8, 8, 17),
(N'Truyện Kiều', 2000, N'NXB Văn Học', 10, 8, 13),
(N'Thơ Xuân Diệu', 2003, N'NXB Văn Học', 6, 8, 11),

(N'SQL Server cơ bản', 2015, N'NXB Giáo Dục', 10, 1, 1),
(N'Django web', 2021, N'NXB Trẻ', 8, 1, 2),
(N'Data Warehouse', 2022, N'NXB Khoa Học', 5, 1, 3),
(N'Kinh tế số', 2020, N'NXB Lao Động', 7, 2, 4),
(N'Đầu tư chứng khoán', 2019, N'NXB Lao Động', 9, 2, 5),
(N'Tâm lý học tình yêu', 2016, N'NXB Văn Học', 6, 3, 6),
(N'Kỹ năng sống', 2018, N'NXB Trẻ', 11, 9, 7),
(N'Ngồi khóc trên cây', 2015, N'NXB Trẻ', 10, 4, 1),
(N'Cho tôi xin một vé đi tuổi thơ', 2012, N'NXB Trẻ', 12, 4, 1),
(N'Chí Phèo', 2004, N'NXB Văn Học', 9, 8, 10),

(N'Lập trình C#', 2016, N'NXB Giáo Dục', 8, 1, 1),
(N'ASP.NET Core', 2021, N'NXB Trẻ', 6, 1, 2),
(N'Big Data', 2022, N'NXB Khoa Học', 5, 1, 3),
(N'Marketing căn bản', 2018, N'NXB Lao Động', 7, 2, 4),
(N'Quản trị doanh nghiệp', 2017, N'NXB Lao Động', 8, 2, 5),
(N'Tâm lý học trẻ em', 2014, N'NXB Văn Học', 6, 3, 6),
(N'Kỹ năng lãnh đạo', 2019, N'NXB Trẻ', 9, 9, 7),
(N'Lão Hạc', 2002, N'NXB Văn Học', 7, 8, 10),
(N'Tắt đèn', 2003, N'NXB Văn Học', 8, 8, 18),
(N'Vợ chồng A Phủ', 2005, N'NXB Văn Học', 6, 8, 9),

(N'Python cho Data', 2022, N'NXB Khoa Học', 10, 1, 2),
(N'Power BI', 2021, N'NXB Khoa Học', 5, 1, 3),
(N'Kinh tế học', 2011, N'NXB Lao Động', 7, 2, 4),
(N'Tài chính doanh nghiệp', 2015, N'NXB Lao Động', 6, 2, 5),
(N'Tâm lý học xã hội', 2018, N'NXB Văn Học', 8, 3, 6),
(N'Kỹ năng thuyết trình', 2017, N'NXB Trẻ', 10, 9, 7),
(N'Truyện ngắn Nam Cao', 2001, N'NXB Văn Học', 9, 8, 10),
(N'Truyện ngắn Thạch Lam', 2002, N'NXB Văn Học', 7, 8, 18),
(N'Truyện Nguyễn Tuân', 2004, N'NXB Văn Học', 6, 8, 16),
(N'Truyện Nguyễn Công Hoan', 2003, N'NXB Văn Học', 5, 8, 19),

(N'Lập trình web', 2020, N'NXB Giáo Dục', 8, 1, 1),
(N'NodeJS', 2021, N'NXB Trẻ', 6, 1, 2),
(N'AI nâng cao', 2023, N'NXB Khoa Học', 4, 1, 3),
(N'Quản trị marketing', 2019, N'NXB Lao Động', 7, 2, 4),
(N'Kinh doanh quốc tế', 2018, N'NXB Lao Động', 6, 2, 5),
(N'Tâm lý học ứng dụng', 2016, N'NXB Văn Học', 8, 3, 6),
(N'Kỹ năng mềm', 2017, N'NXB Trẻ', 9, 9, 7),
(N'Văn học hiện đại', 2012, N'NXB Văn Học', 7, 8, 17),
(N'Văn học cổ điển', 2010, N'NXB Văn Học', 6, 8, 13),
(N'Thơ Hàn Mặc Tử', 2001, N'NXB Văn Học', 5, 8, 12),

(N'Java nâng cao', 2022, N'NXB Giáo Dục', 8, 1, 1),
(N'Flutter mobile', 2023, N'NXB Trẻ', 6, 1, 2),
(N'Data Engineering', 2024, N'NXB Khoa Học', 4, 1, 3),
(N'Quản trị tài chính', 2019, N'NXB Lao Động', 7, 2, 4),
(N'Khởi nghiệp 4.0', 2021, N'NXB Lao Động', 6, 2, 5),
(N'Tâm lý học hành vi người dùng', 2020, N'NXB Văn Học', 8, 3, 6),
(N'Kỹ năng đàm phán', 2018, N'NXB Trẻ', 9, 9, 7),
(N'Truyện Ma Văn Kháng', 2005, N'NXB Văn Học', 7, 8, 20),
(N'Truyện Dương Thu Hương', 2006, N'NXB Văn Học', 6, 8, 8),
(N'Truyện Phan Việt', 2007, N'NXB Văn Học', 5, 8, 7),

(N'HTML CSS JS', 2021, N'NXB Giáo Dục', 10, 1, 1),
(N'ReactJS', 2022, N'NXB Trẻ', 8, 1, 2),
(N'Machine Learning', 2023, N'NXB Khoa Học', 6, 1, 3),
(N'Quản trị chiến lược', 2018, N'NXB Lao Động', 7, 2, 4),
(N'Kinh tế phát triển', 2017, N'NXB Lao Động', 6, 2, 5),
(N'Tâm lý học tổ chức', 2019, N'NXB Văn Học', 8, 3, 6),
(N'Kỹ năng quản lý thời gian', 2020, N'NXB Trẻ', 9, 9, 7),
(N'Văn học thiếu nhi', 2015, N'NXB Kim Đồng', 10, 10, 9),
(N'Truyện cổ tích Việt Nam', 2010, N'NXB Kim Đồng', 12, 10, 9),
(N'Sách khoa học vui', 2018, N'NXB Khoa Học', 11, 5, 3);


INSERT INTO SINHVIEN (MSSV, HOTEN, EMAIL, SDT, LOPHOC)
VALUES
('SV001', N'Nguyễn Văn An', 'sv001@gmail.com', '090000001', 'CNTT1'),
('SV002', N'Trần Thị Bình', 'sv002@gmail.com', '090000002', 'CNTT1'),
('SV003', N'Lê Văn Cường', 'sv003@gmail.com', '090000003', 'CNTT1'),
('SV004', N'Phạm Thị Dung', 'sv004@gmail.com', '090000004', 'CNTT2'),
('SV005', N'Hoàng Văn Em', 'sv005@gmail.com', '090000005', 'CNTT2'),
('SV006', N'Nguyễn Thị Hạnh', 'sv006@gmail.com', '090000006', 'CNTT2'),
('SV007', N'Đỗ Văn Hùng', 'sv007@gmail.com', '090000007', 'CNTT3'),
('SV008', N'Bùi Thị Lan', 'sv008@gmail.com', '090000008', 'CNTT3'),
('SV009', N'Võ Văn Long', 'sv009@gmail.com', '090000009', 'CNTT3'),
('SV010', N'Dương Thị Mai', 'sv010@gmail.com', '090000010', 'CNTT1'),

('SV011', N'Nguyễn Văn Nam', 'sv011@gmail.com', '090000011', 'CNTT1'),
('SV012', N'Trần Thị Nga', 'sv012@gmail.com', '090000012', 'CNTT2'),
('SV013', N'Lê Văn Phúc', 'sv013@gmail.com', '090000013', 'CNTT2'),
('SV014', N'Phạm Thị Quỳnh', 'sv014@gmail.com', '090000014', 'CNTT3'),
('SV015', N'Hoàng Văn Sơn', 'sv015@gmail.com', '090000015', 'CNTT3'),
('SV016', N'Nguyễn Thị Thảo', 'sv016@gmail.com', '090000016', 'CNTT1'),
('SV017', N'Đỗ Văn Tài', 'sv017@gmail.com', '090000017', 'CNTT2'),
('SV018', N'Bùi Thị Trang', 'sv018@gmail.com', '090000018', 'CNTT3'),
('SV019', N'Võ Văn Tuấn', 'sv019@gmail.com', '090000019', 'CNTT1'),
('SV020', N'Dương Thị Vy', 'sv020@gmail.com', '090000020', 'CNTT2'),

('SV021', N'Nguyễn Văn Bảo', 'sv021@gmail.com', '090000021', 'CNTT3'),
('SV022', N'Trần Thị Chi', 'sv022@gmail.com', '090000022', 'CNTT1'),
('SV023', N'Lê Văn Dũng', 'sv023@gmail.com', '090000023', 'CNTT2'),
('SV024', N'Phạm Thị Giang', 'sv024@gmail.com', '090000024', 'CNTT3'),
('SV025', N'Hoàng Văn Hải', 'sv025@gmail.com', '090000025', 'CNTT1'),
('SV026', N'Nguyễn Thị Hương', 'sv026@gmail.com', '090000026', 'CNTT2'),
('SV027', N'Đỗ Văn Khoa', 'sv027@gmail.com', '090000027', 'CNTT3'),
('SV028', N'Bùi Thị Linh', 'sv028@gmail.com', '090000028', 'CNTT1'),
('SV029', N'Võ Văn Minh', 'sv029@gmail.com', '090000029', 'CNTT2'),
('SV030', N'Dương Thị Ngọc', 'sv030@gmail.com', '090000030', 'CNTT3'),

('SV031', N'Nguyễn Văn Oanh', 'sv031@gmail.com', '090000031', 'CNTT1'),
('SV032', N'Trần Thị Phương', 'sv032@gmail.com', '090000032', 'CNTT2'),
('SV033', N'Lê Văn Quang', 'sv033@gmail.com', '090000033', 'CNTT3'),
('SV034', N'Phạm Thị Sen', 'sv034@gmail.com', '090000034', 'CNTT1'),
('SV035', N'Hoàng Văn Tín', 'sv035@gmail.com', '090000035', 'CNTT2'),
('SV036', N'Nguyễn Thị Uyên', 'sv036@gmail.com', '090000036', 'CNTT3'),
('SV037', N'Đỗ Văn Vinh', 'sv037@gmail.com', '090000037', 'CNTT1'),
('SV038', N'Bùi Thị Xuân', 'sv038@gmail.com', '090000038', 'CNTT2'),
('SV039', N'Võ Văn Yên', 'sv039@gmail.com', '090000039', 'CNTT3'),
('SV040', N'Dương Thị Ánh', 'sv040@gmail.com', '090000040', 'CNTT1'),

('SV041', N'Nguyễn Văn Đức', 'sv041@gmail.com', '090000041', 'CNTT2'),
('SV042', N'Trần Thị Hoa', 'sv042@gmail.com', '090000042', 'CNTT3'),
('SV043', N'Lê Văn Khánh', 'sv043@gmail.com', '090000043', 'CNTT1'),
('SV044', N'Phạm Thị Loan', 'sv044@gmail.com', '090000044', 'CNTT2'),
('SV045', N'Hoàng Văn Phong', 'sv045@gmail.com', '090000045', 'CNTT3'),
('SV046', N'Nguyễn Thị Quyên', 'sv046@gmail.com', '090000046', 'CNTT1'),
('SV047', N'Đỗ Văn Sơn', 'sv047@gmail.com', '090000047', 'CNTT2'),
('SV048', N'Bùi Thị Tâm', 'sv048@gmail.com', '090000048', 'CNTT3'),
('SV049', N'Võ Văn Trung', 'sv049@gmail.com', '090000049', 'CNTT1'),
('SV050', N'Dương Thị Yến', 'sv050@gmail.com', '090000050', 'CNTT2');
GO

-- CREATE ADMIN ACCOUNT
INSERT INTO NHANVIEN (MANV, HOTEN, EMAIL, SDT, CHUCVU, LUONG, NGAYVAOLAM)
VALUES ('NV001', N'Admin System', 'admin@library.com', '0987654321', N'Quản trị viên', 20000000, GETDATE());

INSERT INTO TAIKHOAN (USERNAME, MATKHAU, VAITRO, NHANVIENID)
VALUES ('admin', 'pbkdf2_sha256$870000$y0WnEwEszv5xQ8aZ5C407C$E4r6G8w4vOIt1fGv8E9V+R5xO3Hh6KqY7h1sT5M0sX0=', 'admin', SCOPE_IDENTITY());
GO
