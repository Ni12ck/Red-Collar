from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GeoPoint, Message
from django.db.models import Count


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PointSerializer(serializers.ModelSerializer):
    """Сериализатор для точки"""
    user = UserSerializer(read_only=True)
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    messages_count = serializers.SerializerMethodField()

    class Meta:
        model = GeoPoint
        fields = [
            'id', 'user', 'location', 'latitude', 'longitude', 'title',
            'description', 'created_at', 'updated_at', 'messages_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'location']

    def get_latitude(self, obj):
        return obj.latitude

    def get_longitude(self, obj):
        return obj.longitude

    def get_messages_count(self, obj):
        if hasattr(obj, 'messages_count'):
            return obj.messages_count
        return obj.messages.count()


class PointCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания точки"""
    latitude = serializers.FloatField(min_value=-90, max_value=90, write_only=True)
    longitude = serializers.FloatField(min_value=-180, max_value=180, write_only=True)

    class Meta:
        model = GeoPoint
        fields = ['latitude', 'longitude', 'title', 'description']

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        return GeoPoint.create_from_coordinates(
            user=self.context['request'].user,
            latitude=latitude,
            longitude=longitude,
            title=validated_data['title'],
            description=validated_data.get('description', '')
        )


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщения"""
    user = UserSerializer(read_only=True)
    point_title = serializers.CharField(source='point.title', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'point', 'point_title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания сообщения"""
    class Meta:
        model = Message
        fields = ['point', 'content']
