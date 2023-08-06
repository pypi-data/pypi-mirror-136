from django.db import models
from django.utils.html import mark_safe
from django.conf import settings


class BaseImageModel(models.Model):
    upload_to = getattr(settings, 'WYSISWYG_IMG_UPLOAD_TO', '')
    image_width = getattr(settings, 'WYSISWYG_IMG_IMAGE_WIDTH', 150)

    image = models.ImageField(upload_to=upload_to, verbose_name='image')

    def __str__(self):
        return f'image id: {self.pk}'

    def get_image_url(self):
        return mark_safe(f'<h3>{self.image.url}</h3>')
    get_image_url.short_description = 'link to paste'

    def construct_image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="{self.image_width}" height="auto"/>')
    construct_image_tag.short_description = 'thumbnail'
