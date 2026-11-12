from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class FeedSample(models.Model):
    """A feed or silage sample submitted by a farmer."""

    class FeedType(models.TextChoices):
        SILAGE = 'silage', 'Silage'
        GREEN_FODDER = 'green_fodder', 'Green fodder'
        DRY_FODDER = 'dry_fodder', 'Dry fodder'
        HAY = 'hay', 'Hay'
        CONCENTRATE = 'concentrate', 'Concentrate'
        OTHER = 'other', 'Other'

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_samples',
    )
    sample_name = models.CharField(max_length=100)
    feed_type = models.CharField(max_length=20, choices=FeedType.choices)
    collection_date = models.DateField(default=timezone.localdate)
    ph_value = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(14)],
    )
    moisture = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    temperature = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(settings.SAMPLE_TEMPERATURE_MIN_C),
            MaxValueValidator(settings.SAMPLE_TEMPERATURE_MAX_C),
        ],
    )
    smell = models.CharField(max_length=100)
    mold_present = models.BooleanField(default=False)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sample_name} ({self.get_feed_type_display()})'


class TestResult(models.Model):
    """A single quality assessment result for a feed sample."""

    sample = models.OneToOneField(
        FeedSample,
        on_delete=models.CASCADE,
        related_name='test_result',
    )
    quality_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    quality_status = models.CharField(max_length=30)
    assessment_explanation = models.TextField(blank=True)
    recommendations = models.TextField()
    tested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tested_at']

    def __str__(self):
        return f'{self.sample.sample_name}: {self.quality_status}'
