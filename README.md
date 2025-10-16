# 🎬 Video Genius

AI-powered video generation platform built with FastAPI and Google Cloud Platform.

## � Biblioteca de Tecnologias

**🚨 IMPORTANTE**: Antes de qualquer desenvolvimento, consulte nossa [Biblioteca de Tecnologias](./biblioteca/) que contém documentação completa e exemplos práticos para:

- **FastAPI**: APIs, endpoints, validação e melhores práticas
- **BigQuery**: Queries SQL, analytics e machine learning
- **Cloud Code**: Desenvolvimento GCP, Kubernetes e Cloud Run

**A biblioteca é obrigatória para todas as tarefas técnicas!** 📖

## �🚀 Features

- 🤖 AI-powered script generation using Vertex AI
- 🎥 Automated video rendering
- ☁️ Cloud storage integration (Google Cloud Storage)
- 📊 Analytics and reporting (BigQuery)
- 🔐 Secure authentication
- 📱 RESTful API

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **AI/ML**: Google Cloud Vertex AI (Gemini)
- **Database**: Google BigQuery
- **Storage**: Google Cloud Storage
- **Deployment**: Google Cloud Run
- **Testing**: pytest, pytest-cov
- **Linting**: ruff, mypy, black

## 📋 Prerequisites

- Python 3.11+
- Google Cloud Platform account
- GitHub CLI (gh)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/video-genius.git
   cd video-genius
   ```

2. **Setup environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud credentials
   ```

4. **Run the application**
   ```bash
   uvicorn backend.api.main:app --reload
   ```

5. **Run tests**
   ```bash
   pytest
   ```

## 📚 API Documentation

Once the application is running, visit:
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_api.py
```

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Production
```bash
# Deploy to Google Cloud Run
gcloud run deploy video-genius \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, email team@video-genius.com or create an issue in this repository.
