import os
import json
import time
import random
import logging
import requests
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
]


def get_leaf_categories(parent_id, retries=3):
    """
    Calls Tiki API to get the category tree and recursively extracts all leaf node IDs.
    """
    url = f"https://tiki.vn/api/v2/categories?include=children&parent_id={parent_id}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
    }

    for attempt in range(retries):
        try:
            time.sleep(random.uniform(1.0, 2.0))
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json().get("data", [])

                def extract_leaves(nodes):
                    leaves = []
                    for node in nodes:
                        if node.get("is_leaf") is True or not node.get("children"):
                            leaves.append((node.get("id"), node.get("name")))
                        else:
                            leaves.extend(extract_leaves(node.get("children")))
                    return leaves

                leaf_nodes = extract_leaves(data)
                logger.info(
                    f"Extracted {len(leaf_nodes)} leaf categories for parent {parent_id}"
                )
                return leaf_nodes

            logger.warning(
                f"Failed to fetch category tree (HTTP {response.status_code}). Retry {attempt+1}/{retries}"
            )
        except Exception as e:
            logger.error(f"Error fetching category tree: {e}")

    logger.error(
        f"Could not fetch leaf categories for {parent_id}. Returning root ID only."
    )
    return [(parent_id, "Root")]


def process_single_leaf(
    leaf_id, leaf_name, root_cat_id, root_cat_name, leaf_idx, total_leaves
):
    """Worker function to fetch all pages for a single leaf category."""
    leaf_products = []
    page = 1
    max_retries = 3
    logger.info(
        f"--- [Thread {leaf_idx}/{total_leaves}] Started Crawling Leaf: {leaf_name} (ID: {leaf_id}) ---"
    )

    while True:
        url = f"https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&category={leaf_id}&page={page}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://tiki.vn/",
        }

        success = False
        for attempt in range(max_retries):
            try:
                # Ngủ ngẫu nhiên 4.0 - 8.0 giây để tránh bị Akamai block khi crawl trực tiếp
                sleep_time = random.uniform(4.0, 8.0)
                time.sleep(sleep_time)

                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("data", [])

                    if not items:
                        logger.info(
                            f"[Thread {leaf_idx}] Reached end of leaf {leaf_name} at page {page}."
                        )
                        success = True
                        break

                    # OVERRIDE with ROOT CATEGORY INFO
                    for item in items:
                        item["category_id"] = root_cat_id
                        item["category_name"] = root_cat_name
                        leaf_products.append(item)

                    logger.info(
                        f"[Thread {leaf_idx}] Fetched {len(items)} items from {leaf_name} (Page {page})."
                    )
                    page += 1
                    success = True
                    break
                elif response.status_code == 429:
                    logger.warning(
                        f"[Thread {leaf_idx}] Rate limited (429) on {leaf_name} page {page}. Sleeping 10s..."
                    )
                    time.sleep(10)
                else:
                    logger.warning(
                        f"[Thread {leaf_idx}] HTTP {response.status_code} on {leaf_name} page {page}. Attempt {attempt+1}/{max_retries}"
                    )

            except Exception as e:
                logger.error(f"[Thread {leaf_idx}] Error calling {url}: {e}")
                time.sleep(5)

        if not success:
            logger.error(
                f"[Thread {leaf_idx}] Failed to fetch {leaf_name} page {page} after {max_retries} attempts. ABORTING TASK."
            )
            raise RuntimeError("API Error or IP Blocked. Aborting.")

        if success and "items" in locals() and not items:
            break

    return leaf_products


def crawl_category(root_cat_id, root_cat_name, output_dir):
    """Crawls all leaf categories using multiple threads and aggregates them."""
    output_file = os.path.join(output_dir, f"mock_category_{root_cat_id}.json")

    if os.path.exists(output_file):
        logger.info(
            f"File {output_file} already exists. Skipping root category {root_cat_name}."
        )
        return

    logger.info(
        f"========== Starting crawl for ROOT: {root_cat_name} (ID: {root_cat_id}) =========="
    )
    leaf_categories = get_leaf_categories(root_cat_id)
    all_products = []

    # Run 1 thread sequentially for leaf categories (Safe Mode)
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = []
        for idx, (leaf_id, leaf_name) in enumerate(leaf_categories, 1):
            futures.append(
                executor.submit(
                    process_single_leaf,
                    leaf_id,
                    leaf_name,
                    root_cat_id,
                    root_cat_name,
                    idx,
                    len(leaf_categories),
                )
            )

        for future in as_completed(futures):
            try:
                products = future.result()
                if products:
                    all_products.extend(products)
            except Exception as exc:
                logger.error(
                    f"A leaf crawler thread generated an exception: {exc}. Crashing script to mark Airflow task as failed."
                )

                # Cancel all pending tasks to prevent them from executing
                for f in futures:
                    f.cancel()

                # Shutdown executor immediately
                try:
                    executor.shutdown(wait=False, cancel_futures=True)
                except TypeError:
                    # Fallback for Python < 3.9
                    executor.shutdown(wait=False)

                raise exc

    # Save aggregated data for the Root Category
    if all_products:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        logger.info(
            f"========== Saved TOTAL {len(all_products)} products to {output_file} =========="
        )
    else:
        logger.warning(f"No products found for {root_cat_name}. Skipping save.")


def main():
    parser = argparse.ArgumentParser(description="Tiki Multi-threaded Category Crawler")
    parser.add_argument(
        "--category_ids",
        type=str,
        help="Comma-separated category IDs to crawl. If empty, crawls all 26.",
    )

    # Đường dẫn lưu file crawl trên máy Windows
    parser.add_argument(
        "--output_dir",
        type=str,
        default=r"C:\Users\tranb\OneDrive\Desktop\VCCORP\WEEK_1",
        help="Folder to save crawled JSON files.",
    )

    args = parser.parse_args()

    base_dir = args.output_dir
    os.makedirs(base_dir, exist_ok=True)

    logger.info(f"Saving output JSON files to {base_dir}")

    # Determine which categories to process based on CLI arg
    target_cats = {}

    if args.category_ids:
        ids_to_crawl = [
            int(cid.strip()) for cid in args.category_ids.split(",") if cid.strip()
        ]

        for cid in ids_to_crawl:
            if cid in CATEGORIES:
                target_cats[cid] = CATEGORIES[cid]
            else:
                logger.warning(
                    f"Category ID {cid} is not in the predefined 26 root categories. Skipping."
                )
    else:
        target_cats = CATEGORIES

    logger.info(
        f"Will crawl the following {len(target_cats)} categories: {list(target_cats.values())}"
    )

    for cat_id, cat_name in target_cats.items():
        crawl_category(cat_id, cat_name, base_dir)

    logger.info("🎉 Chunk crawl completed successfully!")


if __name__ == "__main__":
    main()
