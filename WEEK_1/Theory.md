# REPORT: KỸ NĂNG LẬP TRÌNH CƠ BẢN VÀ THAO TÁC VỚI CƠ SỞ DỮ LIỆU SQL SERVER

##### Thực tập sinh: Trần Bách
##### Chủ đề: Python/SQL cơ bản, Linux command line, SQL Server và thực hành xử lý dữ liệu

---

## 1. Mục tiêu

Mục tiêu của báo cáo là tổng hợp và trình bày các kiến thức nền tảng cần thiết để làm việc với lập trình cơ bản và cơ sở dữ liệu. Nội dung tập trung vào các nhóm kỹ năng chính:

- Nắm được cú pháp và tư duy lập trình cơ bản với Python.
- Sử dụng SQL để thao tác, truy vấn và phân tích dữ liệu.
- Làm việc với Linux command line để thao tác file, thư mục, process, phân quyền và shell scripting.
- Làm việc với SQL Server: cài đặt, tạo database, table, kiểu dữ liệu, constraints, transaction, stored procedures, triggers, index và execution plan.
- Thực hành viết script Python để đọc file CSV, làm sạch dữ liệu và ghi dữ liệu vào SQL Server.

---

# 2. Nội dung học tập

## 2.1. Python cơ bản


### 2.1.1. Cú pháp cơ bản

Python sử dụng thụt lề để xác định khối lệnh thay vì dùng dấu `{}` như một số ngôn ngữ khác.

```python
name = "An"
age = 20

if age >= 18:
    print("Đủ tuổi")
else:
    print("Chưa đủ tuổi")
```

### 2.1.2. Cấu trúc dữ liệu trong Python

| Cấu trúc | Mô tả | Ví dụ |
|---|---|---|
| List | Danh sách có thứ tự, có thể thay đổi | `[1, 2, 3]` |
| Tuple | Danh sách có thứ tự, không thể thay đổi | `(1, 2, 3)` |
| Dict | Lưu dữ liệu dạng key-value | `{"name": "An", "age": 20}` |
| Set | Tập hợp không trùng lặp phần tử | `{1, 2, 3}` |

Ví dụ:

```python
student = {
    "id": 1,
    "name": "Nguyen Van A",
    "score": 8.5
}

print(student["name"])
```

### 2.1.3. Xử lý file trong Python

Python hỗ trợ đọc/ghi nhiều loại file như text, CSV và JSON.

#### Đọc file text

```python
with open("data.txt", "r", encoding="utf-8") as file:
    content = file.read()
    print(content)
```

#### Ghi file text

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello Python")
```

#### Đọc file CSV

```python
import csv

with open("students.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
```

#### Đọc file JSON

```python
import json

with open("students.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    print(data)
```


## 2.2. SQL cơ bản

SQL là ngôn ngữ dùng để thao tác với cơ sở dữ liệu quan hệ. SQL cho phép người dùng tạo bảng, thêm dữ liệu, sửa dữ liệu, xóa dữ liệu và truy vấn dữ liệu.

### 2.2.1. Các nhóm câu lệnh SQL

| Nhóm lệnh | Ý nghĩa | Ví dụ |
|---|---|---|
| DDL | Định nghĩa cấu trúc database | `CREATE`, `ALTER`, `DROP` |
| DML | Thao tác dữ liệu | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| DCL | Quản lý quyền | `GRANT`, `REVOKE` |
| TCL | Quản lý transaction | `COMMIT`, `ROLLBACK` |

### 2.2.2. SELECT

```sql
SELECT student_id, full_name, email
FROM dbo.Students;
```

### 2.2.3. INSERT

```sql
INSERT INTO dbo.Students (full_name, email, age, gender)
VALUES (N'Nguyen Van A', 'a@gmail.com', 20, 'M');
```

### 2.2.4. UPDATE

```sql
UPDATE dbo.Students
SET email = 'new_email@gmail.com'
WHERE student_id = 1;
```

### 2.2.5. DELETE

```sql
DELETE FROM dbo.Students
WHERE student_id = 1;
```

### 2.2.6. JOIN

JOIN dùng để kết hợp dữ liệu từ nhiều bảng dựa trên điều kiện liên kết.

#### INNER JOIN

Trả về các bản ghi có dữ liệu khớp ở cả hai bảng.

```sql
SELECT s.full_name, c.course_name
FROM dbo.Students AS s
INNER JOIN dbo.Enrollments AS e ON s.student_id = e.student_id
INNER JOIN dbo.Courses AS c ON e.course_id = c.course_id;
```

#### LEFT JOIN

Trả về toàn bộ bản ghi từ bảng bên trái và dữ liệu khớp từ bảng bên phải.

```sql
SELECT s.full_name, c.course_name
FROM dbo.Students AS s
LEFT JOIN dbo.Enrollments AS e ON s.student_id = e.student_id
LEFT JOIN dbo.Courses AS c ON e.course_id = c.course_id;
```

#### RIGHT JOIN

Trả về toàn bộ bản ghi từ bảng bên phải và dữ liệu khớp từ bảng bên trái.

```sql
SELECT s.full_name, c.course_name
FROM dbo.Students AS s
RIGHT JOIN dbo.Enrollments AS e ON s.student_id = e.student_id
RIGHT JOIN dbo.Courses AS c ON e.course_id = c.course_id;
```

#### FULL OUTER JOIN

SQL Server hỗ trợ `FULL OUTER JOIN`, trả về tất cả bản ghi khi có dữ liệu ở một trong hai bảng.

```sql
SELECT s.full_name, e.enrollment_id
FROM dbo.Students AS s
FULL OUTER JOIN dbo.Enrollments AS e
    ON s.student_id = e.student_id;
```

### 2.2.7. Aggregation, GROUP BY và HAVING

Các hàm tổng hợp thường dùng:

| Hàm | Ý nghĩa |
|---|---|
| COUNT() | Đếm số lượng bản ghi |
| SUM() | Tính tổng |
| AVG() | Tính trung bình |
| MIN() | Tìm giá trị nhỏ nhất |
| MAX() | Tìm giá trị lớn nhất |

Ví dụ:

```sql
SELECT c.course_name, COUNT(e.student_id) AS total_students
FROM dbo.Courses AS c
LEFT JOIN dbo.Enrollments AS e ON c.course_id = e.course_id
GROUP BY c.course_name;
```

`HAVING` dùng để lọc sau khi đã `GROUP BY`.

```sql
SELECT c.course_name, COUNT(e.student_id) AS total_students
FROM dbo.Courses AS c
LEFT JOIN dbo.Enrollments AS e ON c.course_id = e.course_id
GROUP BY c.course_name
HAVING COUNT(e.student_id) >= 2;
```

### 2.2.8. Subquery

Subquery là câu truy vấn nằm bên trong một câu truy vấn khác.

```sql
SELECT s.full_name, e.final_score
FROM dbo.Students AS s
INNER JOIN dbo.Enrollments AS e ON s.student_id = e.student_id
WHERE e.final_score > (
    SELECT AVG(final_score)
    FROM dbo.Enrollments
    WHERE final_score IS NOT NULL
);
```

### 2.2.9. Index

Index giúp tăng tốc độ truy vấn dữ liệu, đặc biệt với các cột thường xuyên dùng trong `WHERE`, `JOIN`, `ORDER BY`.

```sql
CREATE INDEX IX_Students_Email
ON dbo.Students(email);
```

Tuy nhiên, không nên tạo quá nhiều index vì index làm tăng chi phí ghi dữ liệu khi `INSERT`, `UPDATE`, `DELETE`.

---

## 2.3. Linux command line

Linux command line là kỹ năng quan trọng đối với lập trình viên, data engineer và backend developer. Người dùng có thể thao tác với file, thư mục, process, phân quyền và viết script tự động hóa.

### 2.3.1. Các lệnh thao tác file và thư mục

| Lệnh | Ý nghĩa | Ví dụ |
|---|---|---|
| `ls` | Liệt kê file/thư mục | `ls -la` |
| `cd` | Chuyển thư mục | `cd /home/user` |
| `pwd` | Hiển thị thư mục hiện tại | `pwd` |
| `mkdir` | Tạo thư mục | `mkdir data` |
| `rm` | Xóa file/thư mục | `rm file.txt` |
| `cp` | Copy file/thư mục | `cp a.txt b.txt` |
| `mv` | Di chuyển hoặc đổi tên | `mv old.txt new.txt` |
| `grep` | Tìm kiếm nội dung trong file | `grep "error" log.txt` |
| `find` | Tìm file/thư mục | `find . -name "*.csv"` |
| `chmod` | Phân quyền file | `chmod 755 script.sh` |

### 2.3.2. Quản lý process

| Lệnh | Ý nghĩa |
|---|---|
| `ps` | Xem danh sách process |
| `top` | Theo dõi process theo thời gian thực |
| `kill` | Dừng process theo PID |

Ví dụ:

```bash
ps aux | grep python
kill 1234
```

### 2.3.3. Quản lý người dùng và phân quyền

```bash
sudo adduser intern
sudo passwd intern
sudo usermod -aG sudo intern
```

Một số quyền cơ bản trong Linux:

| Quyền | Ý nghĩa |
|---|---|
| r | Read - quyền đọc |
| w | Write - quyền ghi |
| x | Execute - quyền thực thi |

Ví dụ phân quyền file script:

```bash
chmod +x run.sh
```

### 2.3.4. Shell scripting cơ bản

Shell script giúp tự động hóa các thao tác lặp lại.

```bash
#!/bin/bash

echo "Start processing data"
python3 import_csv_to_sqlserver.py
echo "Done"
```

---

## 2.4. SQL Server

SQL Server là hệ quản trị cơ sở dữ liệu quan hệ do Microsoft phát triển. SQL Server thường được sử dụng trong các hệ thống doanh nghiệp, ứng dụng quản lý, hệ thống báo cáo, data warehouse và các bài toán xử lý dữ liệu có cấu trúc.

SQL Server hỗ trợ:

- Tạo database và table.
- Các kiểu dữ liệu phổ biến như `INT`, `VARCHAR`, `NVARCHAR`, `DATE`, `DATETIME`, `DECIMAL`, `BIT`.
- Constraints như `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`.
- Transaction với `BEGIN TRANSACTION`, `COMMIT`, `ROLLBACK`.
- Stored procedure.
- Trigger.
- Index và execution plan.

### 2.4.1. Cài đặt SQL Server

Có thể sử dụng một trong các cách sau:

- Cài SQL Server Developer Edition trên Windows.
- Cài SQL Server Express nếu chỉ cần học và thực hành nhẹ.
- Cài SQL Server Management Studio (SSMS) để viết query, quản lý database và vẽ Database Diagram.
- Cài Azure Data Studio nếu muốn giao diện nhẹ hơn.

Sau khi cài đặt, có thể kết nối bằng SSMS với các thông tin cơ bản:

| Thành phần | Ví dụ |
|---|---|
| Server name | `localhost` hoặc `localhost\\SQLEXPRESS` |
| Authentication | Windows Authentication hoặc SQL Server Authentication |
| Login | `sa` nếu dùng SQL Authentication |
| Password | Mật khẩu đã cấu hình khi cài SQL Server |

### 2.4.2. Tạo database trong SQL Server

```sql
CREATE DATABASE TrainingDB;
GO

USE TrainingDB;
GO
```

### 2.4.3. Kiểu dữ liệu phổ biến trong SQL Server

| Kiểu dữ liệu | Ý nghĩa | Ví dụ |
|---|---|---|
| `INT` | Số nguyên | `age INT` |
| `DECIMAL(5,2)` | Số thập phân chính xác | `score DECIMAL(5,2)` |
| `VARCHAR(100)` | Chuỗi không Unicode | `email VARCHAR(100)` |
| `NVARCHAR(100)` | Chuỗi Unicode, phù hợp tiếng Việt | `full_name NVARCHAR(100)` |
| `DATE` | Ngày tháng | `date_of_birth DATE` |
| `DATETIME2` | Ngày giờ | `created_at DATETIME2` |
| `BIT` | Đúng/sai | `is_active BIT` |

### 2.4.4. Constraints trong SQL Server

Constraints giúp đảm bảo dữ liệu hợp lệ và giữ đúng quan hệ giữa các bảng.

| Constraint | Ý nghĩa |
|---|---|
| `PRIMARY KEY` | Khóa chính, định danh duy nhất mỗi bản ghi |
| `FOREIGN KEY` | Khóa ngoại, tạo quan hệ giữa các bảng |
| `NOT NULL` | Không cho phép giá trị rỗng |
| `UNIQUE` | Không cho phép trùng lặp |
| `CHECK` | Kiểm tra điều kiện dữ liệu |
| `DEFAULT` | Gán giá trị mặc định |

Ví dụ:

```sql
CREATE TABLE dbo.Students (
    student_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INT CHECK (age >= 0),
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
```

### 2.4.5. Transaction trong SQL Server

Transaction giúp đảm bảo một nhóm thao tác được thực hiện đầy đủ hoặc không thực hiện gì nếu có lỗi.

```sql
BEGIN TRANSACTION;

UPDATE dbo.Accounts
SET balance = balance - 100000
WHERE account_id = 1;

UPDATE dbo.Accounts
SET balance = balance + 100000
WHERE account_id = 2;

COMMIT TRANSACTION;
```

### 2.4.6. Stored procedure trong SQL Server

Stored procedure là đoạn SQL được lưu sẵn trong database và có thể gọi lại nhiều lần.

```sql
CREATE OR ALTER PROCEDURE dbo.GetStudentsByAge
    @input_age INT
AS
BEGIN
    SELECT student_id, full_name, email, age
    FROM dbo.Students
    WHERE age = @input_age;
END;
GO
```

Gọi procedure:

```sql
EXEC dbo.GetStudentsByAge @input_age = 20;
```

### 2.4.7. Trigger trong SQL Server

Trigger là đoạn lệnh tự động chạy khi có sự kiện `INSERT`, `UPDATE` hoặc `DELETE` trên bảng.

```sql
CREATE TABLE dbo.StudentLogs (
    log_id INT IDENTITY(1,1) PRIMARY KEY,
    student_id INT,
    action_name VARCHAR(50),
    created_at DATETIME2 DEFAULT SYSDATETIME()
);
GO

CREATE OR ALTER TRIGGER dbo.trg_AfterStudentInsert
ON dbo.Students
AFTER INSERT
AS
BEGIN
    INSERT INTO dbo.StudentLogs(student_id, action_name)
    SELECT student_id, 'INSERT'
    FROM inserted;
END;
GO
```

# 3. Thực hành Python: đọc CSV, làm sạch dữ liệu và load vào SQL Server

## 3.1. Dữ liệu đầu vào CSV

Giả sử có file `students.csv`:

```csv
student_code,full_name,email,age,gender,city
SV010,Nguyen Van K,k@gmail.com,20,M,Ha Noi
SV011,Tran Thi L,l@gmail.com,,F,Da Nang
SV012,Le Van M,,22,M,Hai Phong
SV013,Pham Thi N,n@gmail.com,twenty,F,Ha Noi
SV014,Hoang Van O,o@gmail.com,23,M,Ho Chi Minh
```

Một số lỗi dữ liệu trong file:

- `SV011` bị thiếu `age`.
- `SV012` bị thiếu `email`.
- `SV013` có `age = twenty`, sai kiểu dữ liệu.

## 3.2. Cài đặt thư viện Python

Cài thư viện cần thiết:

```bash
pip install pandas sqlalchemy pyodbc
```

Máy cần cài thêm ODBC Driver cho SQL Server. Trên Windows thường dùng:

- ODBC Driver 17 for SQL Server
- hoặc ODBC Driver 18 for SQL Server


## 3.3. Script Python load CSV vào SQL Server

```python
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus


# 1. Đọc file CSV

file_path = "students.csv"
df = pd.read_csv(file_path)

print("Dữ liệu ban đầu:")
print(df)

# 2. Làm sạch dữ liệu
# Chuẩn hóa tên cột
df.columns = [col.strip().lower() for col in df.columns]

# Xử lý chuỗi rỗng thành NaN
df = df.replace(r"^\s*$", pd.NA, regex=True)

# Xử lý email bị thiếu
df["email"] = df["email"].fillna("unknown@example.com")

# Chuyển age sang số, nếu lỗi thì thành NaN
df["age"] = pd.to_numeric(df["age"], errors="coerce")

# Loại bỏ dòng không có age hoặc age không hợp lệ
df = df.dropna(subset=["age"])


# Chỉ giữ gender hợp lệ
df["gender"] = df["gender"].str.upper()
df = df[df["gender"].isin(["M", "F"])]

# Chỉ giữ các cột cần import
df = df[["student_code", "full_name", "email", "age", "gender", "city"]]

print("Dữ liệu sau khi làm sạch:")
print(df)

# 3. Kết nối SQL Server


# Cách 1: Windows Authentication
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=TrainingDB;"
    "Trusted_Connection=yes;"
)

# Nếu dùng SQL Server Authentication, dùng mẫu này:
# connection_string = (
#     "DRIVER={ODBC Driver 17 for SQL Server};"
#     "SERVER=localhost;"
#     "DATABASE=TrainingDB;"
#     "UID=sa;"
#     "PWD=your_password;"
# )

connection_url = "mssql+pyodbc:///?odbc_connect=" + quote_plus(connection_string)
engine = create_engine(connection_url, fast_executemany=True)

```

---


# 4. Tối ưu truy vấn bằng index và execution plan trong SQL Server

## 4.1. Khi nào cần dùng index?

Index nên được sử dụng cho các cột:

- Thường xuất hiện trong điều kiện `WHERE`.
- Thường dùng để `JOIN` giữa các bảng.
- Thường dùng trong `ORDER BY` hoặc `GROUP BY`.
- Có số lượng bản ghi lớn.

Ví dụ tạo index cho email sinh viên:

```sql
CREATE INDEX IX_Students_Email
ON dbo.Students(email);
```

Tạo index cho khóa ngoại trong bảng `Enrollments`:

```sql
CREATE INDEX IX_Enrollments_StudentId
ON dbo.Enrollments(student_id);

CREATE INDEX IX_Enrollments_CourseId
ON dbo.Enrollments(course_id);
```

Tạo index cho điểm cuối kỳ:

```sql
CREATE INDEX IX_Enrollments_FinalScore
ON dbo.Enrollments(final_score);
```

## 4.2. Xem execution plan trong SQL Server

Có 2 cách phổ biến:

### Cách 1: Dùng SSMS

1. Mở query trong SSMS.
2. Bấm `Ctrl + M` để bật `Include Actual Execution Plan`.
3. Chạy query.
4. Xem tab `Execution Plan`.

### Cách 2: Dùng câu lệnh SQL

```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

SELECT *
FROM dbo.Students
WHERE email = 'a@gmail.com';

SET STATISTICS IO OFF;
SET STATISTICS TIME OFF;
```

Nếu chưa có index, SQL Server có thể phải quét bảng bằng `Table Scan` hoặc `Clustered Index Scan`. Sau khi tạo index phù hợp, SQL Server có thể dùng `Index Seek`, thường hiệu quả hơn khi bảng có nhiều dữ liệu.


# 5. Kết quả đạt được

Sau khi hoàn thành nội dung học và thực hành, người học đạt được các kết quả sau:

- Hiểu được cú pháp và cấu trúc dữ liệu cơ bản trong Python.
- Biết cách đọc/ghi file text, CSV và JSON.
- Biết cách viết function và sử dụng module trong Python.
- Sử dụng được các câu lệnh SQL cơ bản như `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- Hiểu và viết được các câu truy vấn dùng `JOIN`, `GROUP BY`, `HAVING`, subquery.
- Biết cách cài đặt và thao tác cơ bản với SQL Server.
- Biết cách tạo database, table, primary key, foreign key và dữ liệu mẫu trong SQL Server.
- Hiểu các khái niệm constraints, transaction, stored procedure và trigger.
- Biết dùng Linux command line để thao tác file, thư mục, process và phân quyền.
- Viết được script Python để đọc CSV, làm sạch dữ liệu và ghi vào SQL Server.
- Biết cách tạo index và dùng execution plan để phân tích hiệu năng truy vấn.
