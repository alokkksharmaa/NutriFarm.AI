from django.contrib import admin

from .models import FeedSample, TestResult


@admin.register(FeedSample)
class FeedSampleAdmin(admin.ModelAdmin):
    list_display = (
        'sample_name',
        'farmer',
        'feed_type',
        'created_at',
        'mold_present',
    )
    list_filter = ('feed_type', 'mold_present', 'created_at')
    search_fields = ('sample_name', 'farmer__username', 'farmer__email')
    readonly_fields = ('created_at',)


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('sample', 'quality_score', 'quality_status', 'tested_at')
    list_filter = ('quality_status', 'tested_at')
    search_fields = ('sample__sample_name', 'sample__farmer__username')
    readonly_fields = ('tested_at',)
