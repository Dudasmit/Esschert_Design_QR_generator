from django.db import models
from urllib.parse import quote
import os
from django.conf import settings
from .qr_utils import extract_qr_data_from_image, check_url_exists 


class Product(models.Model):
    
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=50)
    created_at = models.DateField()
    group = models.CharField(max_length=100)
    show_on_site = models.BooleanField(default=False)
    external_id = models.CharField(max_length=100, unique=True)
    qr_image_url = models.URLField(blank=True, null=True)
    qr_code_url = models.URLField(blank=True, null=True)
    product_url = models.URLField(blank=True, null=True)
    product_image_url = models.URLField(blank=True, null=True)
    
    


    def __str__(self):
        return self.name

class QRTaskStatus(models.Model):
    task_id = models.CharField(max_length=100, unique=True)
    total = models.PositiveIntegerField(default=0)
    processed = models.PositiveIntegerField(default=0)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def progress(self):
        if self.total == 0:
            return 0
        return int((self.processed / self.total) * 100)
    
    
