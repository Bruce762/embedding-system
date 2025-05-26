from django.contrib import admin
from .models import TestModel, DHT

@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(DHT)
class DHTAdmin(admin.ModelAdmin):
    list_display = ('temperature', 'humidity', 'recorded_at')
    list_filter = ('recorded_at',)
