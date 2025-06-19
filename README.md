# Personalized Learning Assistant (PLA) - "Athena"

A cross-device web application that transforms fragmented self-study into a continuously adapting, AI-driven learning journey. PLA creates day-by-day study plans, ingests practice-exam documents, delivers on-demand tutoring, and reinforces knowledge via spaced-repetition reminders—all behind a simple checklist interface that feels calming rather than overwhelming.

## 🎯 Project Overview

**Version:** 0.9 - "Athena"  
**Platform:** Web (React + Flask API)  
**Architecture:** Microservices with AI integration  
**Target Launch:** September 5, 2025

### Key Features

- **AI-Powered Study Planning**: Generate personalized 7-day study plans based on topics and target dates
- **Smart Document Ingestion**: Upload PDF/DOCX files to extract Q/A pairs and concepts
- **Interactive AI Tutor**: Chat with GPT-powered tutor with session memory
- **Spaced Repetition System**: Four-tier reminder logic for optimal retention
- **Progress Analytics**: Track mastery, time spent, and efficiency scores
- **Responsive Design**: Works seamlessly across desktop and mobile devices

### Success Metrics

- Reduce learner overwhelm: ≤20% "I feel overwhelmed" responses
- Improve retention: ≥80% quiz scores after 14 days
- Increase plan adherence: ≥70% daily tasks completed
- Engagement: ≥6 median chat turns per session
- Commercial viability: 5,000+ monthly active users

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Flask API     │    │   Core Services │
│                 │    │                 │    │                 │
│ • Login/Signup  │◄──►│ • Auth Routes   │◄──►│ • Planner       │
│ • Planner View  │    │ • Planner Routes│    │ • GPT Handler   │
│ • Chat Interface│    │ • AI Routes     │    │ • File Parser   │
│ • Upload Dialog │    │ • Upload Routes │    │ • Repetition    │
│ • Dashboard     │    │ • Progress Routes│   │   Engine       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       │                 │
                       │ • users         │
                       │ • plans         │
                       │ • tasks         │
                       │ • uploads       │
                       │ • reminders     │
                       │ • chat_logs     │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis +       │
                       │   Celery        │
                       │                 │
                       │ • Async Tasks   │
                       │ • Reminders     │
                       │ • GPT Queue     │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **PostgreSQL** (v13 or higher)
- **Redis** (v6 or higher)
- **Git**

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Personal-Learning-Assistant.git
cd Personal-Learning-Assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### 2. Environment Configuration

Create `.env` files for both frontend and backend:

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/pla_db
REDIS_URL=redis://localhost:6379/0

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# JWT Secret
JWT_SECRET_KEY=your_super_secret_jwt_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_flask_secret_key_here

# Email Configuration (for reminders)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# File Upload
MAX_FILE_SIZE=20971520  # 20MB in bytes
UPLOAD_FOLDER=uploads/
```

**Frontend (.env):**
```bash
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000/ws
```

### 3. Database Setup

```bash
# Start PostgreSQL service
# On macOS: brew services start postgresql
# On Ubuntu: sudo systemctl start postgresql
# On Windows: Start PostgreSQL service from Services

# Create database
createdb pla_db

# Run migrations
flask db upgrade
```

### 4. Redis Setup

```bash
# Start Redis service
# On macOS: brew services start redis
# On Ubuntu: sudo systemctl start redis
# On Windows: Download and start Redis server

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 5. External Service Setup

#### OpenAI API Setup

1. **Create OpenAI Account**: Visit [OpenAI Platform](https://platform.openai.com/)
2. **Generate API Key**: Go to API Keys section and create a new key
3. **Add to Environment**: Copy the key to your `.env` file
4. **Set Usage Limits**: Configure usage limits to control costs

```bash
# Test OpenAI connection
python scripts/test_openai.py
```

#### Email Service Setup (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**: 
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Add to Environment**: Use the generated password in `.env`

#### File Storage Setup

```bash
# Create upload directory
mkdir uploads
mkdir uploads/exams
mkdir uploads/temp

# Set permissions
chmod 755 uploads
```

### 6. Start Development Servers

```bash
# Terminal 1: Start Flask API
cd backend
flask run

# Terminal 2: Start React Frontend
cd frontend
npm start

# Terminal 3: Start Celery Worker
cd backend
celery -A app.celery worker --loglevel=info

# Terminal 4: Start Celery Beat (for scheduled tasks)
cd backend
celery -A app.celery beat --loglevel=info
```

### 7. Verify Installation

1. **Frontend**: Visit `http://localhost:3000`
2. **Backend API**: Visit `http://localhost:5000/api/health`
3. **Database**: Check connection with `flask db current`
4. **Redis**: Verify with `redis-cli ping`

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/test_auth.py
python -m pytest tests/test_planner.py
python -m pytest tests/test_ai.py

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Load testing
python scripts/load_test.py
```

### Frontend Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e

# Run with coverage
npm test -- --coverage
```

### API Testing

```bash
# Test all endpoints
python scripts/test_api.py

# Test specific endpoints
curl -X GET http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 📊 Monitoring & Analytics

### Application Monitoring

```bash
# Start monitoring dashboard
python scripts/monitor.py

# View logs
tail -f logs/app.log

# Check system health
python scripts/health_check.py
```

### Database Monitoring

```bash
# Connect to database
psql pla_db

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public';

# Monitor slow queries
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### Redis Monitoring

```bash
# Monitor Redis
redis-cli monitor

# Check memory usage
redis-cli info memory

# View active keys
redis-cli keys "*"
```

## 🔧 Development Workflow

### Code Structure

```
Personal-Learning-Assistant/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API calls and utilities
│   │   ├── hooks/          # Custom React hooks
│   │   └── utils/          # Helper functions
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # Flask API
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Helper functions
│   │   └── config.py       # Configuration
│   ├── migrations/         # Database migrations
│   ├── tests/              # Test files
│   └── requirements.txt
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── README.md
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/ai-chat-enhancement

# Make changes and commit
git add .
git commit -m "feat: enhance AI chat with session memory"

# Push and create PR
git push origin feature/ai-chat-enhancement
```

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Add user preferences table"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set production values in `.env.production`
2. **Database**: Use managed PostgreSQL service (AWS RDS, Google Cloud SQL)
3. **Redis**: Use managed Redis service (AWS ElastiCache, Google Cloud Memorystore)
4. **File Storage**: Use cloud storage (AWS S3, Google Cloud Storage)
5. **SSL**: Configure HTTPS with Let's Encrypt or managed certificates

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Cloud Deployment (AWS)

```bash
# Deploy to AWS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t pla-backend .
docker tag pla-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/pla-backend:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/pla-backend:latest
```

## 🔒 Security Considerations

### OWASP Top 10 Compliance

- **Input Validation**: All user inputs are validated and sanitized
- **Authentication**: JWT tokens with secure expiration
- **Authorization**: Role-based access control
- **SQL Injection**: Parameterized queries with SQLAlchemy
- **XSS Protection**: React's built-in XSS protection
- **CSRF Protection**: CSRF tokens for state-changing operations
- **File Upload Security**: Virus scanning and file type validation
- **HTTPS**: Enforced in production
- **Security Headers**: Implemented via Flask-Talisman

### Data Privacy

- **Encryption**: All sensitive data encrypted at rest
- **PII Protection**: Personal data minimized and protected
- **Audit Logging**: All data access logged
- **Data Retention**: Automatic cleanup of old data
- **GDPR Compliance**: User data export and deletion capabilities

## 📈 Performance Optimization

### API Performance

- **Caching**: Redis caching for frequently accessed data
- **Database Indexing**: Optimized indexes for common queries
- **Connection Pooling**: Database connection pooling
- **Async Processing**: Celery for background tasks
- **Rate Limiting**: API rate limiting to prevent abuse

### Frontend Performance

- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Webpack optimization
- **CDN**: Static assets served via CDN
- **Caching**: Browser caching strategies
- **Image Optimization**: Compressed and optimized images

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U username -d pla_db
```

**Redis Connection Error:**
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping
```

**OpenAI API Error:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API call
python scripts/test_openai.py
```

**Celery Worker Issues:**
```bash
# Check Celery status
celery -A app.celery inspect active

# Restart workers
pkill -f celery
celery -A app.celery worker --loglevel=info
```

### Log Analysis

```bash
# View application logs
tail -f logs/app.log

# Search for errors
grep -i error logs/app.log

# Monitor real-time logs
tail -f logs/app.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/TypeScript
- Write comprehensive tests for new features
- Update documentation for API changes
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/Personal-Learning-Assistant/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Personal-Learning-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Personal-Learning-Assistant/discussions)
- **Email**: support@personal-learning-assistant.com

## 🗺️ Roadmap

### Phase 1: Foundation & Core AI (July 15, 2025)
- [x] Project setup and architecture
- [ ] User authentication system
- [ ] Basic AI planner
- [ ] GPT integration for explanations
- [ ] Chat tutor interface

### Phase 2: Content Ingestion & Reinforcement (August 10, 2025)
- [ ] File upload and parsing
- [ ] Spaced repetition system
- [ ] Quiz generation
- [ ] Basic analytics dashboard

### Phase 3: Public Launch & Optimization (September 5, 2025)
- [ ] Performance optimization
- [ ] Security hardening
- [ ] Accessibility improvements
- [ ] Public MVP launch

### Phase 4: Post-Launch & Expansion (October 15, 2025)
- [ ] Mobile responsiveness
- [ ] Premium tier features
- [ ] A/B testing framework
- [ ] Advanced analytics

---

**Built with ❤️ by Carl Paolino & Team**