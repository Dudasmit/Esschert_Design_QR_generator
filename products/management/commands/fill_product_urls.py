import os
from django.core.management.base import BaseCommand
from urllib.parse import quote
from products.models import Product  # 👈 замени на реальное имя приложения и модели


class Command(BaseCommand):
    help = "Заполняет поля product_url и product_image_url для всех записей"

    def handle(self, *args, **options):
        self.stdout.write("🔄 Начинаем обновление записей...")

        objects = Product.objects.all()
        updated = 0

        for obj in objects:
            obj.product_url = f"{os.getenv("QR_REDIRECT_URL")}{obj.name}"
            obj.product_image_url = (
                f"https://dhznjqezv3l9q.cloudfront.net/report_Image/normal/{quote(obj.name)}_01.png"
            )
            updated += 1

        # массовое обновление для производительности
        Product.objects.bulk_update(objects, ["product_url", "product_image_url"])

        self.stdout.write(self.style.SUCCESS(f"✅ Обновлено {updated} записей."))
