from django.contrib import admin

from django.db.models import Count

from .models import Feed, Subscriber, Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = [ 'feed','__str__','timestamp' ]
    list_filder = ['feed']
    ordering = ['-timestamp', 'title']
    list_filter = ['feed']

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['name','email']

class FeedAdmin(admin.ModelAdmin):
    list_display = ['title','url','last_fetch', 'enabled']
    ordering = ['title']
    actions = [ 'fetch_feed']

    def fetch_feed(self, request, queryset):
        for obj in queryset:
            obj.fetch()

admin.site.register(Feed, FeedAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Entry, EntryAdmin)
# Register your models here.
