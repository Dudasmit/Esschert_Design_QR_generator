from django.contrib import admin
from django.utils.html import format_html
from urllib.parse import quote
from .models import Product, ItemCollection, QRTaskStatus


admin.site.register(ItemCollection)

@admin.register(QRTaskStatus)
class QRTaskStatusAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'total', 'processed', 'progress', 'done', 'created_at')
    list_filter = ('done', 'created_at')
    search_fields = ('task_id',)

    def progress(self, obj):
        return f"{obj.progress}%"
    progress.short_description = 'Progress'

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barcode', 'image_preview', 'created_at', 'show_on_site')
    list_filter = ('show_on_site', 'group', 'created_at')
    search_fields = ('name', 'barcode', 'external_id', 'group')

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.product_image_url:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:contain;" />',
                obj.product_image_url
            )
        return "-"
    image_preview.short_description = 'Изображение'
