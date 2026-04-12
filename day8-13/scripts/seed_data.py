"""
scripts/seed_data.py — Tạo dữ liệu mẫu để test.

Chạy: python scripts/seed_data.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.users.models import User
from apps.inventory.models import Category, Product


def main() -> None:
    print("🌱 Đang tạo dữ liệu mẫu...")

    # ── Superuser ─────────────────────────────────────────────────────
    if not User.objects.filter(email="admin@shop.com").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@shop.com",
            password="admin123",
            role=User.Role.ADMIN,
        )
        print("✅ Admin: admin@shop.com / admin123")

    # ── Customer ──────────────────────────────────────────────────────
    if not User.objects.filter(email="khach@shop.com").exists():
        User.objects.create_user(
            username="khachhang",
            email="khach@shop.com",
            password="khach123",
        )
        print("✅ Khách hàng: khach@shop.com / khach123")

    # ── Categories ────────────────────────────────────────────────────
    cat_data = [
        ("Điện tử", "Thiết bị điện tử, smartphone, laptop"),
        ("Thời trang", "Quần áo, giày dép, phụ kiện"),
        ("Thực phẩm", "Đồ ăn, thức uống"),
    ]
    categories = {}
    for name, desc in cat_data:
        cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
        categories[name] = cat
    print(f"✅ {len(cat_data)} danh mục")

    # ── Products ──────────────────────────────────────────────────────
    products = [
        ("iPhone 15 Pro", 28_990_000, 50, categories["Điện tử"]),
        ("Samsung Galaxy S24", 22_990_000, 30, categories["Điện tử"]),
        ("Laptop Dell XPS 13", 35_000_000, 15, categories["Điện tử"]),
        ("Áo thun basic", 199_000, 200, categories["Thời trang"]),
        ("Quần jeans slim", 499_000, 100, categories["Thời trang"]),
        ("Cà phê Highlands", 55_000, 500, categories["Thực phẩm"]),
    ]
    for name, price, stock, cat in products:
        Product.objects.get_or_create(
            name=name,
            defaults={"price": price, "stock": stock, "category": cat, "is_active": True},
        )
    print(f"✅ {len(products)} sản phẩm")

    print("\n🚀 Xong! Truy cập:")
    print("   Django Admin : http://127.0.0.1:8000/admin")
    print("   API Docs     : http://127.0.0.1:8000/api/docs/")


if __name__ == "__main__":
    main()