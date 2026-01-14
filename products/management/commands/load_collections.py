# app/management/commands/load_collections.py
from django.core.management.base import BaseCommand
from products.models import ItemCollection
from django.conf import settings
from pathlib import Path
#python manage.py load_collections

class Command(BaseCommand):
    help = "Load ItemCollection from collections.txt"
    ItemCollection.objects.all().delete()

    def handle(self, *args, **kwargs):
        file_path = Path(settings.BASE_DIR) / 'collections.txt'

        if not file_path.exists():
            self.stderr.write("collections.txt not found")
            return

        with open(file_path, encoding='utf-8') as f:
            for line in f:
                value = line.strip()
                if value:
                    ItemCollection.objects.get_or_create(collection=value)

        self.stdout.write(self.style.SUCCESS("Collections loaded"))
