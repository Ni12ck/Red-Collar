import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import GeoPoint, Message


class PointAPITestCase(APITestCase):
    """Тесты для API точек"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Очищаем базу данных перед каждым тестом
        User.objects.all().delete()
        GeoPoint.objects.all().delete()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123',
            email='other@example.com'
        )

        # Создаем токен для аутентификации
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Создаем тестовые точки
        self.point1 = GeoPoint.create_from_coordinates(
            user=self.user,
            latitude=55.7558,
            longitude=37.6176,
            title='Красная площадь',
            description='Главная площадь Москвы'
        )
        self.point2 = GeoPoint.create_from_coordinates(
            user=self.user,
            latitude=55.7642,
            longitude=37.6026,
            title='Большой театр',
            description='Исторический театр'
        )

    def test_create_point(self):
        """Тест создания точки"""
        data = {
            'latitude': 55.7520,
            'longitude': 37.6175,
            'title': 'Москва',
            'description': 'Столица России'
        }
        response = self.client.post('/api/points/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GeoPoint.objects.filter(user=self.user).count(), 3)

    def test_create_point_invalid_coordinates(self):
        """Тест создания точки с неверными координатами"""
        data = {
            'latitude': 91,  # Неверная широта
            'longitude': 37.6175,
            'title': 'Invalid Point'
        }
        response = self.client.post('/api/points/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_points(self):
        """Тест получения списка точек пользователя"""
        response = self.client.get('/api/points/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем результаты с учетом пагинации
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 2)

    def test_point_detail(self):
        """Тест получения детальной информации о точке"""
        response = self.client.get(f'/api/points/{self.point1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Красная площадь')

    def test_update_point(self):
        """Тест обновления точки"""
        data = {'title': 'Обновленная Красная площадь'}
        response = self.client.patch(f'/api/points/{self.point1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.point1.refresh_from_db()
        self.assertEqual(self.point1.title, 'Обновленная Красная площадь')

    def test_delete_point(self):
        """Тест удаления точки"""
        response = self.client.delete(f'/api/points/{self.point1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GeoPoint.objects.filter(user=self.user).count(), 1)

    def test_search_points_nearby(self):
        """Тест поиска точек в радиусе"""
        # Поиск рядом с Красной площадью (радиус 1 км)
        response = self.client.get('/api/points/search/', {
            'latitude': 55.7558,
            'longitude': 37.6176,
            'radius': 1.0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должна найтись хотя бы одна точка
        self.assertGreater(len(response.data), 0)

    def test_search_points_invalid_params(self):
        """Тест поиска с неверными параметрами"""
        response = self.client.get('/api/points/search/', {
            'latitude': 'invalid',
            'longitude': 37.6176,
            'radius': 1.0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        """Тест доступа без аутентификации"""
        self.client.credentials()  # Убираем токен
        response = self.client.get('/api/points/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MessageAPITestCase(APITestCase):
    """Тесты для API сообщений"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Очищаем базу данных перед каждым тестом
        User.objects.all().delete()
        GeoPoint.objects.all().delete()
        Message.objects.all().delete()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        # Создаем токен для аутентификации
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Создаем тестовую точку
        self.point = GeoPoint.create_from_coordinates(
            user=self.user,
            latitude=55.7558,
            longitude=37.6176,
            title='Тестовая точка'
        )

        # Создаем тестовое сообщение
        self.message = Message.objects.create(
            user=self.user,
            point=self.point,
            content='Тестовое сообщение'
        )

    def test_create_message(self):
        """Тест создания сообщения"""
        data = {
            'point': self.point.id,
            'content': 'Новое сообщение'
        }
        response = self.client.post('/api/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.filter(user=self.user).count(), 2)

    def test_list_messages(self):
        """Тест получения списка сообщений пользователя"""
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем результаты с учетом пагинации
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_message_detail(self):
        """Тест получения детальной информации о сообщении"""
        response = self.client.get(f'/api/messages/{self.message.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Тестовое сообщение')

    def test_search_messages_nearby(self):
        """Тест поиска сообщений в радиусе"""
        response = self.client.get('/api/messages/search/', {
            'latitude': 55.7558,
            'longitude': 37.6176,
            'radius': 1.0
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AuthenticationTestCase(APITestCase):
    """Тесты для аутентификации"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Очищаем базу данных перед каждым тестом
        User.objects.all().delete()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_token_obtain(self):
        """Тест получения JWT токена"""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        """Тест обновления JWT токена"""
        # Сначала получаем токен
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']

        # Обновляем токен
        response = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
