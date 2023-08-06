from django.contrib import admin

class ImageInline(admin.TabularInline):
    model = None
    readonly_fields = [
        'get_image_url', 'construct_image_tag',
    ]