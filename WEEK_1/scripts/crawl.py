import io
import json
import os
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from minio import Minio

load_dotenv()


TIKI_BASE_URL = "https://tiki.vn/api/personalish/v1/blocks/listings"

TIKI_PARAMS = {
    "limit": 40,
    # "include": "advertisement",
    "aggregations": 2,
    "version": "home-persionalized",
    "trackity_id": "a70494ca-ade3-e960-071f-177343beefd7",
    "category": 1815,
    "page": 1,
    "urlKey": "thiet-bi-kts-phu-kien-so",
}


MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_RAW")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


SLEEP_MIN_SECONDS = 1.5
SLEEP_MAX_SECONDS = 4.0
REQUEST_TIMEOUT = 30


def create_minio_client():
    """
    Tạo client kết nối MinIO.
    """

    client = Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )

    return client


def ensure_bucket_exists(client):
    """
    Kiểm tra bucket đã tồn tại chưa.
    Nếu chưa có thì tạo bucket.
    """

    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        print(f"Created bucket: {MINIO_BUCKET}")
    else:
        print(f"Bucket already exists: {MINIO_BUCKET}")


def crawl_tiki_until_empty():
    """
    Crawl Tiki cho đến khi hết dữ liệu.
    """

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://tiki.vn/",
    }

    page = 1
    all_products = []

    while True:
        print(f"Fetching page {page}...")

        # Copy params để không sửa trực tiếp biến TIKI_PARAMS gốc
        params = TIKI_PARAMS.copy()
        params["page"] = page

        response = requests.get(
            TIKI_BASE_URL,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            print(f"Request failed at page {page}. Status code: {response.status_code}")
            break

        json_response = response.json()

        # Tiki thường trả danh sách sản phẩm trong key "data"
        products = json_response.get("data", [])

        # Nếu data rỗng nghĩa là hết danh mục
        if not products:
            print(f"No more data at page {page}. Stop crawling.")
            break

        print(f"Page {page}: {len(products)} products")

        all_products.extend(products)

        page += 1

        # Nghỉ random để tránh gọi API quá nhanh
        sleep_time = random.uniform(SLEEP_MIN_SECONDS, SLEEP_MAX_SECONDS)
        print(f"Sleep {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    return all_products


def upload_json_to_minio(products):
    """
    Upload dữ liệu lên MinIO
    """

    # Lấy ngày theo giờ Việt Nam
    vietnam_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    crawl_date = vietnam_time.strftime("%Y-%m-%d")

    data_to_save = {
        "source": "tiki",
        "category_id": 1815,
        "url_key": "thiet-bi-kts-phu-kien-so",
        "crawl_date": crawl_date,
        "total_products": len(products),
        "products": products,
    }

    json_bytes = json.dumps(
        data_to_save,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")

    client = create_minio_client()
    ensure_bucket_exists(client)

    # Tên file trong MinIO
    object_name = f"{crawl_date}/{crawl_date}.json"

    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=io.BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json",
    )

    print(f"Uploaded to MinIO: s3://{MINIO_BUCKET}/{object_name}")


def main():
    products = crawl_tiki_until_empty()

    if not products:
        print("No products crawled. Nothing to upload.")
        return

    upload_json_to_minio(products)

    print("Done.")


if __name__ == "__main__":
    main()
