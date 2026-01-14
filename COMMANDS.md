# Быстрая справка по командам

## Основные команды

### Запуск и остановка
```bash
docker-compose up -d              # Запустить в фоне
docker-compose up                 # Запустить с логами
docker-compose down               # Остановить
docker-compose restart            # Перезапустить
docker-compose ps                 # Статус сервисов
```

### Логи
```bash
docker-compose logs -f            # Все логи
docker-compose logs -f web        # Логи web
docker-compose logs -f db         # Логи БД
docker-compose logs -f pgadmin    # Логи pgAdmin
```

### Django команды
```bash
docker-compose exec web python manage.py migrate         # Миграции
docker-compose exec web python manage.py makemigrations  # Создать миграции
docker-compose exec web python manage.py test            # Тесты
docker-compose exec web python manage.py createsuperuser # Админ
docker-compose exec web bash                             # Shell
```

### База данных
```bash
docker-compose exec db psql -U geo_points_user -d geo_points
```

### Очистка
```bash
docker-compose down -v            # Удалить volumes (удалит данные!)
docker-compose build --no-cache   # Пересобрать без кеша
```
