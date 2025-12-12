import boto3
from django.core.management.base import BaseCommand
from products.models import Product
from django.utils import timezone
from ...qr_utils import  extract_qr_data_from_image
import os
# Настройки S3

BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_FOLDER = os.getenv("S3_FOLDER")

CLOUDFRONT_URL = os.getenv("CLOUDFRONT_URL")
s3 = boto3.client('s3')


class Command(BaseCommand):
    help = 'Синхронизация товаров с QR-кодами на AWS S3/CloudFront'

    def handle(self, *args, **options):
        # Подключаемся к S3
        paginator = s3.get_paginator('list_objects_v2')

        aws_files = set()
        for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=S3_FOLDER):
            for obj in page.get('Contents', []):
                key = obj['Key'].replace(S3_FOLDER, '')
                if key.endswith('.png'):
                    aws_files.add(key)

        self.stdout.write(f"Found {(aws_files)} files on AWS")

        # Получаем все записи с заполненным qr_code_url
        products = Product.objects.exclude(qr_code_url__isnull=True)

        deleted_count = 0
        updated_count = 0

        # Синхронизация существующих записей
        for product in products:
            filename = f"{product.name}.png"
            if filename in aws_files:
                print(f"Обработка продукта: {filename}")
                # QR код существует, обновляем URL
                qr_url = CLOUDFRONT_URL + S3_FOLDER + filename
                #if product.qr_code_url != qr_url:
                product.qr_image_url = extract_qr_data_from_image(product.name)
                product.qr_code_url = qr_url
                product.save(update_fields=['qr_image_url', 'qr_code_url'])
                updated_count += 1
            else:
                # QR код отсутствует, удаляем запись
                product.qr_image_url = ''
                product.qr_code_url = ''
                product.save(update_fields=['qr_image_url', 'qr_code_url'])
                deleted_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Sync complete: {updated_count} updated, {deleted_count} deleted."
        ))
        
        for filename in aws_files:
            product_name = filename.replace('.png', '')
            product  = Product.objects.filter(name__iexact=product_name).first()
            print(f"Проверка продукта для файла: {product_name}")
            print(f"Найдено продуктов в БД: {product }")
            if product :
                qr_url = CLOUDFRONT_URL + S3_FOLDER + filename
                product.qr_image_url = extract_qr_data_from_image(product.name)
                product.qr_code_url = qr_url
                product.save(update_fields=['qr_image_url', 'qr_code_url'])
               
             

       
            
