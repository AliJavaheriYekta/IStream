from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from .validators import validate_file_extension, validate_image_extension
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from taggit.managers import TaggableManager

class Stream(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="stream_created")
    user_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, allow_unicode=True, blank=True)
    game = models.CharField(max_length=200, blank=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.user_name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user_name, allow_unicode=True)
        super(Stream, self).save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('streams:my_stream_details', args=[self.user_name])


class Comment(models.Model):
    stream = models.ForeignKey(Stream, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, default=None)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.stream)

