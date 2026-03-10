# Health Chatbot Backend Documentation

## Base URL
```
http://localhost:5000/api
```

## Environment Setup

### Requirements
- Python 3.10+
- Virtual environment recommended

### Installation
```bash
pip install -r requirements.txt
```

### Environment Configuration
Create a `.env` file with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=<your_secret>
JWT_SECRET_KEY=<your_jwt_secret>
MONGO_URI=mongodb://localhost:27017/healthchatbot
GOOGLE_CLIENT_ID=<your_client_id>
GOOGLE_CLIENT_SECRET=<your_client_secret>
GOOGLE_DISCOVERY_URL=https://accounts.google.com/.well-known/openid-configuration
ML_MODEL_URL=http://localhost:6000/predict
```

## API Documentation

### Authentication Routes

#### 1. Register User
- **Endpoint**: `/user/register`
- **Method**: POST
- **Description**: Register a new user (local auth only)

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "mypassword123",
  "auth_provider": "local"
}
```

**Response**:
```json
{
  "id": "<user_id>",
  "name": "John Doe",
  "email": "john@example.com",
  "auth_provider": "local",
  "created_at": "2025-08-26T10:00:00"
}
```

**Errors**: `400` Email exists or validation errors

#### 2. Login User
- **Endpoint**: `/auth/login`
- **Method**: POST

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "mypassword123"
}
```

**Response**:
```json
{
  "message": "Login successful",
  "user": { ...user details... },
  "access_token": "<JWT_TOKEN>"
}
```

### User Routes

#### 1. Get User Profile
- **Endpoint**: `/user/profile`
- **Method**: GET
- **Protected**: Yes (JWT required)

**Response**:
```json
{
  "id": "<user_id>",
  "name": "John Doe",
  "email": "john@example.com",
  "auth_provider": "local",
  "created_at": "2025-08-26T10:00:00"
}
```

#### 2. Update User Profile
- **Endpoint**: `/user/profile`
- **Method**: PUT
- **Protected**: Yes

**Request Body** (optional fields):
```json
{
  "name": "John Smith",
  "password": "newpassword123"
}
```

### Chat Routes

#### 1. Create Chat
- **Endpoint**: `/chat`
- **Method**: POST
- **Protected**: Yes

**Response**:
```json
{
  "chat_id": "<chat_id>",
  "shareable_link": "<uuid>"
}
```

#### 2. Add Message to Chat
- **Endpoint**: `/chat/<chat_id>/message`
- **Method**: POST
- **Protected**: Yes

**Request Body**:
```json
{
  "text": "I feel dizzy"
}
```

#### 3. Get Chat History
- **Endpoint**: `/chat/history`
- **Method**: GET
- **Protected**: Yes
- **Query Parameter**: `archived=true` to include archived chats

**Response**:
```json
{
  "chats": [
    {
      "chat_id": "<chat_id>",
      "created_at": "...",
      "last_message": "...",
      "shareable_link": "...",
      "archived": false
    }
  ]
}
```

#### 4. Get Chat by Shareable Link
- **Endpoint**: `/chat/share/<link>`
- **Method**: GET
- **Protected**: No

**Response**:
```json
{
  "chat_id": "<chat_id>",
  "messages": [...],
  "created_at": "...",
  "shareable_link": "..."
}
```

#### 5. Archive Chat
- **Endpoint**: `/chat/<chat_id>/archive`
- **Method**: POST
- **Protected**: Yes

**Response**:
```json
{
  "message": "Chat archived successfully"
}
```

#### 6. Delete Chat
- **Endpoint**: `/chat/<chat_id>`
- **Method**: DELETE
- **Protected**: Yes

**Response**:
```json
{
  "message": "Chat deleted successfully"
}
```

### ML Model Integration

#### Test ML Model
- **Endpoint**: `/chat/test-ml`
- **Method**: POST
- **Protected**: Yes

**Request Body**:
```json
{
  "text": "I feel nauseous and dizzy."
}
```

## Important Notes
- All timestamps are in UTC
- Passwords are hashed and never returned
- JWT required for all protected endpoints
- Shareable links allow read-only access
- Archived chats can be filtered via `/chat/history?archived=true`
- ML Model URL is configurable in `.env`
- Use Postman/Insomnia to test routes easily
