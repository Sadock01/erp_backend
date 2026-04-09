from django.contrib import admin
from .models import AnalyticsCache


@admin.register(AnalyticsCache)
class AnalyticsCacheAdmin(admin.ModelAdmin):
    list_display = ['cache_key', 'cache_type', 'expires_at', 'created_at']
    list_filter = ['cache_type', 'created_at']
    search_fields = ['cache_key']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
