from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point as GEOSPoint
from django.contrib.gis.measure import D


class GeoPoint(models.Model):
    """Модель точки на карте с использованием GeoDjango"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points')
    location = gis_models.PointField(
        srid=4326,  # WGS84 coordinate system
        help_text="Географическая точка (широта, долгота)"
    )
    title = models.CharField(max_length=200, help_text="Название точки")
    description = models.TextField(blank=True, help_text="Описание точки")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    @property
    def latitude(self):
        """Получить широту из географической точки"""
        return self.location.y if self.location else None

    @property
    def longitude(self):
        """Получить долготу из географической точки"""
        return self.location.x if self.location else None

    @classmethod
    def create_from_coordinates(cls, user, latitude, longitude, title, description=""):
        """Создать точку из координат широты и долготы"""
        location = GEOSPoint(float(longitude), float(latitude), srid=4326)
        return cls.objects.create(
            user=user,
            location=location,
            title=title,
            description=description
        )

    def __str__(self):
        if self.location:
            return f"{self.title} ({self.location.y:.6f}, {self.location.x:.6f})"
        return f"{self.title} (no location)"


class Message(models.Model):
    """Модель сообщения к точке"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    point = models.ForeignKey(GeoPoint, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(help_text="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['point', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Message by {self.user.username} at {self.point.title}"
