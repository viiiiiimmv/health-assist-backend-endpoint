#!/bin/bash

# Inside root already (health_chatbot_backend/)
# Create app structure
mkdir -p app/{models,routes,services,utils}
mkdir -p migrations
mkdir -p tests

# Create core files
touch app/__init__.py
touch app/config.py
touch app/extensions.py

# Models
touch app/models/__init__.py
touch app/models/user_model.py
touch app/models/chat_model.py

# Routes
touch app/routes/__init__.py
touch app/routes/auth_routes.py
touch app/routes/chat_routes.py
touch app/routes/user_routes.py

# Services
touch app/services/__init__.py
touch app/services/auth_service.py
touch app/services/chat_service.py
touch app/services/ml_service.py

# Utils
touch app/utils/__init__.py
touch app/utils/jwt_utils.py
touch app/utils/link_utils.py
touch app/utils/datetime_utils.py

# Main entry point
touch app/main.py
touch run.py

# Env + dependencies
touch .env
touch requirements.txt

# Tests
touch tests/test_auth.py
touch tests/test_chat.py
touch tests/test_ml.py

echo "✅ Flask backend structure created inside $(pwd)"