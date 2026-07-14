# -*- coding: utf-8 -*-
"""
Script thu thập danh mục con (children categories) từ API Tiki
theo danh sách parent_id cho trước, sau đó upload từng file JSON lên MinIO.

API: https://tiki.vn/api/v2/categories?include=children&parent_id={parent_id}

Kết quả:
- Mỗi parent_id -> 1 object JSON upload thẳng lên MinIO (không lưu local):
    bucket:  list-category
    object:  {YYYY-MM-DD}/categories_parent_id_{parent_id}.json

Cài thư viện cần thiết trước khi chạy:
    pip install requests minio
"""

import io
import json
import os
import random
import time
from datetime import date

import requests
from minio import Minio
from minio.error import S3Error

# ====== CẤU HÌNH CHUNG ======

API_URL = "https://tiki.vn/api/v2/categories"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

SLEEP_MIN = 2  # giây, thời gian nghỉ tối thiểu giữa các request
SLEEP_MAX = 4  # giây, thời gian nghỉ tối đa giữa các request
TIMEOUT = 15

# ====== CẤU HÌNH MINIO ======
# Có thể override qua biến môi trường (docker-compose .env), mặc định lấy
# đúng theo thông tin bạn cung cấp.

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Bucket cố định theo yêu cầu (khác với MINIO_BUCKET_RAW trong .env)
MINIO_BUCKET_LIST_CATEGORY = "list-category"  # bucket name không được chứa "_"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

CATEGORIES = {
    8322: "Nhà Sách Tiki",
    1883: "Nhà Cửa - Đời Sống",
    1789: "Điện Thoại - Máy Tính Bảng",
    2549: "Đồ Chơi - Mẹ & Bé",
    1815: "Thiết Bị Số - Phụ Kiện Số",
    1882: "Điện Gia Dụng",
    1520: "Làm Đẹp - Sức Khỏe",
    8594: "Ô Tô - Xe Máy - Xe Đạp",
    931: "Thời trang nữ",
    4384: "Bách Hóa Online",
    1975: "Thể Thao - Dã Ngoại",
    915: "Thời trang nam",
    17166: "Cross Border - Hàng Quốc Tế",
    1846: "Laptop - Máy Vi Tính - Linh kiện",
    1686: "Giày - Dép nam",
    4221: "Điện Tử - Điện Lạnh",
    1703: "Giày - Dép nữ",
    1801: "Máy Ảnh - Máy Quay Phim",
    27498: "Phụ kiện thời trang",
    44792: "NGON",
    8371: "Đồng hồ và Trang sức",
    6000: "Balo và Vali",
    11312: "Voucher - Dịch vụ",
    976: "Túi thời trang nữ",
    27616: "Túi thời trang nam",
    15078: "Chăm sóc nhà cửa",
}


def ensure_bucket(bucket_name: str) -> None:
    """Tạo bucket trên MinIO nếu chưa tồn tại."""
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"[MinIO] Đã tạo bucket mới: {bucket_name}")
        else:
            print(f"[MinIO] Bucket đã tồn tại: {bucket_name}")
    except S3Error as e:
        print(f"[MinIO][LỖI] Không thể kiểm tra/tạo bucket '{bucket_name}': {e}")
        raise


def upload_json_to_minio(bucket_name: str, object_name: str, data: dict) -> bool:
    """Upload một dict dạng JSON lên MinIO dưới dạng object."""
    try:
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        stream = io.BytesIO(payload)
        minio_client.put_object(
            bucket_name,
            object_name,
            data=stream,
            length=len(payload),
            content_type="application/json",
        )
        print(f"  -> [MinIO] Đã upload: {bucket_name}/{object_name}")
        return True
    except S3Error as e:
        print(f"  -> [MinIO][LỖI] Upload thất bại '{object_name}': {e}")
        return False


def fetch_category(parent_id: int) -> dict | None:
    """Gọi API lấy children category theo parent_id."""
    params = {"include": "children", "parent_id": parent_id}
    try:
        resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  [LỖI] parent_id={parent_id}: {e}")
        return None


def main():
    # Đảm bảo bucket tồn tại trước khi upload
    ensure_bucket(MINIO_BUCKET_LIST_CATEGORY)

    # Folder theo ngày hôm nay, ví dụ: 2026-07-09
    today_folder = date.today().strftime("%Y-%m-%d")

    total = len(CATEGORIES)
    for idx, (parent_id, name) in enumerate(CATEGORIES.items(), start=1):
        print(f"[{idx}/{total}] Đang lấy: {parent_id} - {name}")

        data = fetch_category(parent_id)

        if data is not None:
            filename = f"categories_parent_id_{parent_id}.json"

            # Upload thẳng lên MinIO: list-category/{today}/{filename}
            object_name = f"{today_folder}/{filename}"
            upload_json_to_minio(MINIO_BUCKET_LIST_CATEGORY, object_name, data)
        else:
            print(f"  -> Bỏ qua parent_id={parent_id} do lỗi request")

        # Nghỉ ngẫu nhiên giữa các request để tránh bị chặn API
        if idx < total:
            delay = random.uniform(SLEEP_MIN, SLEEP_MAX)
            print(f"  ... nghỉ {delay:.1f}s trước khi tiếp tục")
            time.sleep(delay)

    print(
        "\nHoàn tất! Toàn bộ file JSON đã upload lên MinIO "
        f"bucket '{MINIO_BUCKET_LIST_CATEGORY}/{today_folder}/'."
    )


if __name__ == "__main__":
    main()
