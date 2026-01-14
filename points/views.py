from django.shortcuts import render
from django.db import models
from django.contrib.gis.geos import Point as GEOSPoint
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import GeoPoint, Message
from .serializers import (
    PointSerializer, PointCreateSerializer,
    MessageSerializer, MessageCreateSerializer
)


class PointViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с точками"""
    permission_classes = [IsAuthenticated]
    queryset = GeoPoint.objects.all()

    def get_queryset(self):
        return GeoPoint.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create']:
            return PointCreateSerializer
        return PointSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск точек в заданном радиусе с использованием GeoDjango"""
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 1.0))  # км
        except (TypeError, ValueError):
            return Response(
                {'error': 'Неверные параметры: latitude, longitude (float), radius (float, optional)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Валидация координат
        if not (-90 <= latitude <= 90):
            return Response({'error': 'Широта должна быть между -90 и 90'}, status=status.HTTP_400_BAD_REQUEST)
        if not (-180 <= longitude <= 180):
            return Response({'error': 'Долгота должна быть между -180 и 180'}, status=status.HTTP_400_BAD_REQUEST)
        if radius <= 0:
            return Response({'error': 'Радиус должен быть положительным'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем точку поиска
        search_point = GEOSPoint(longitude, latitude, srid=4326)

        # Используем GeoDjango для поиска точек в радиусе
        points = self.get_queryset().filter(
            location__distance_lte=(search_point, D(km=radius))
        ).annotate(
            distance=models.functions.Cast(
                Distance('location', search_point),
                models.DecimalField(max_digits=10, decimal_places=3)
            )
        ).order_by('distance')

        # Сериализуем результаты
        serializer = self.get_serializer(points, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с сообщениями"""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()

    def get_queryset(self):
        return Message.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create']:
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск сообщений в заданном радиусе с использованием GeoDjango"""
        try:
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = float(request.query_params.get('radius', 1.0))  # км
        except (TypeError, ValueError):
            return Response(
                {'error': 'Неверные параметры: latitude, longitude (float), radius (float, optional)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Валидация координат
        if not (-90 <= latitude <= 90):
            return Response({'error': 'Широта должна быть между -90 и 90'}, status=status.HTTP_400_BAD_REQUEST)
        if not (-180 <= longitude <= 180):
            return Response({'error': 'Долгота должна быть между -180 и 180'}, status=status.HTTP_400_BAD_REQUEST)
        if radius <= 0:
            return Response({'error': 'Радиус должен быть положительным'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем точку поиска
        search_point = GEOSPoint(longitude, latitude, srid=4326)

        # Используем GeoDjango для поиска сообщений в радиусе через точки
        messages = self.get_queryset().select_related('point').filter(
            point__location__distance_lte=(search_point, D(km=radius))
        ).annotate(
            distance=models.functions.Cast(
                Distance('point__location', search_point),
                models.DecimalField(max_digits=10, decimal_places=3)
            )
        ).order_by('distance')

        # Сериализуем результаты
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
