from django.contrib import admin

from django.db.models import Count

from .models import Feed, Contact, Entry

admin.site.register(Feed)
admin.site.register(Contact)
admin.site.register(Entry)
# Register your models here.
