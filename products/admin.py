from django.contrib import admin
from django.utils.html import format_html
from urllib.parse import quote
from .models import Product

#admin.site.register(Product)


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
