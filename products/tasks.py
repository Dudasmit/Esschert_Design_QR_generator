from celery import shared_task
from .models import Product,QRTaskStatus
from datetime import date
import os
from .qr_utils import create_and_save_qr_code_eps, extract_qr_data_from_image
from django.conf import settings
import boto3
from .filters import ProductFilter
from .inriver import get_inriver_header
import requests
import json

from django.utils import timezone


BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_FOLDER = os.getenv("S3_FOLDER")
IN_RIVER_URL = os.getenv("IN_RIVER_URL")    
AWS_REGION=os.getenv("AWS_REGION")

AWS_URL = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{S3_FOLDER}"

s3 = boto3.client("s3")

@shared_task(bind=True)
def generate_qr_for_products(self, product_ids=None, select_all=False, include_barcode=False, domain=None, filter_data=None):
    """
    Генерация QR-кодов для товаров.
    :param product_ids: список id выбранных товаров
    :param select_all: если True — обрабатываем все товары по фильтру
    :param include_barcode: включать штрихкод в QR
    :param domain: домен для ссылок
    :param filter_data: фильтр для select_all (dict)
    """
    
    if select_all:
        
        products = ProductFilter(filter_data or {}, queryset=Product.objects.all()).qs
    else:
        products = Product.objects.filter(id__in=product_ids or [])
     
     
    total = products.count()
    print(f"🚀 Generating shared_task", self.request.id)

    # 🔹 Create/update task status entry
    task_status, _ = QRTaskStatus.objects.get_or_create(task_id=self.request.id)
    task_status.total = total
    task_status.processed = 0
    task_status.done = False
    task_status.save()
            
    print(f"🚀 Generating {total} QR codes...")
    
    
    for i, product in enumerate(products, start=1):
        try:
            qr_text = product.name
            if include_barcode:
                qr_text += f"\n{product.barcode}"
            print(f"🔧 Generating QR for product ID {product.id}, Name: {product.name}")

            # create a QR code using your function
            result = create_and_save_qr_code_eps(
                s3,
                f"https://{domain}/01/0",
                product.name,
                product.barcode,
                include_barcode,
                S3_FOLDER
            )

            if not isinstance(result, dict):
                continue

            # update or create a product record with a QR code URL
            Product.objects.update_or_create(
                external_id=product.external_id,
                defaults={
                    'name': product.name,
                    'barcode': product.barcode,
                    'created_at': date.today(),
                    'group': 'inriver',
                    'show_on_site': True,
                    'qr_code_url': f"{AWS_URL}{product.name}.png",
                    'qr_image_url': extract_qr_data_from_image(product.name,AWS_URL),
                }
            )
        except Exception as e:
            print(f"⚠️ Ошибка при обработке {product.id}: {e}")
            
        task_status.processed = i
        task_status.save(update_fields=["processed"])
        
    task_status.done = True
    task_status.save(update_fields=["done"])







@shared_task(bind=True)
def sync_products_from_inriver_task(self,entity_ids):
    created_count = 0
    updated_count = 0
    skipped_count = 0

    

    total = len(entity_ids)
    print(f"🚀 Generating shared_task", self.request.id)


   # 🔹 Create/update task status entry
    task_status, _ = QRTaskStatus.objects.get_or_create(task_id=self.request.id)
    task_status.total = total
    task_status.processed = 0
    task_status.done = False
    task_status.save()
    
    print(f"🚀 Generating {total} QR codes...")
    
    for i, ext_id in enumerate(entity_ids, start=1):
        if Product.objects.filter(external_id=ext_id).exists():
            skipped_count += 1
            continue

        try:
            resp = requests.get(
                f"{IN_RIVER_URL}/api/v1.0.0/entities/{int(ext_id)}/fieldvalues",
                headers=get_inriver_header()
            )

            if resp.status_code != 200 or resp.text == "[]":
                continue

            json_data = resp.json()

            product_name = next((i["value"] for i in json_data if i["fieldTypeId"] == "ItemCode"), None)

            product, created = Product.objects.update_or_create(
                external_id=ext_id,
                defaults={
                    'name': product_name,
                    'barcode': next((i["value"] for i in json_data if i["fieldTypeId"] == "ItemGTIN"), None),
                    'created_at': timezone.now(),
                    'group': 'inriver',
                    'show_on_site': True,
                    'product_url': f"{os.getenv('QR_REDIRECT_URL')}{product_name}",
                    'product_image_url': f"https://dhznjqezv3l9q.cloudfront.net/report_Image/normal/{product_name}_01.png"
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
                
            task_status.processed = i
            task_status.save(update_fields=["processed"])
        


        except Exception as e:
            print("Error fetching entity:", ext_id, e)
            
    task_status.done = True
    task_status.save(update_fields=["done"])



    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count
    }
