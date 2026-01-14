#!/bin/bash

# Geo Points API - Quick Start Script

echo "🚀 Starting Geo Points API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp docker-env-example.txt .env
    echo "✅ .env file created."
fi

# Build and start services
docker-compose build
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "✅ Services are running!"
echo ""
echo "🌐 API:        http://localhost:8000"
echo "🔐 Admin:      http://localhost:8000/admin/"
echo "🗄️  pgAdmin:    http://localhost:5050"
echo ""
echo "👤 Django:     admin / admin123"
echo "👨‍💼 pgAdmin:    admin@geo-points.com / admin123"
echo ""
echo "📋 Useful commands:"
echo "  docker-compose logs -f                                    # View logs"
echo "  docker-compose exec web python manage.py test            # Run tests"
echo "  docker-compose exec web python manage.py migrate         # Run migrations"
echo "  docker-compose exec web bash                             # Access shell"
echo "  docker-compose down                                      # Stop services"
