# TradingAgents - Docker Setup Guide

This directory contains the Docker setup for running TradingAgents with a FastAPI backend and Next.js frontend.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API Key
- Alpha Vantage API Key (optional, for enhanced data)

### Environment Setup

1. Copy your `.env` file in the project root with your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

### Running with Docker

1. **Build and start all services:**
```bash
docker-compose up --build
```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Stop the services:**
```bash
docker-compose down
```

## 📁 Project Structure

```
TradingAgents/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── core/        # Configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # Next.js frontend
│   ├── app/            # Next.js pages
│   ├── components/     # React components
│   ├── lib/            # Utilities and API client
│   ├── hooks/          # Custom React hooks
│   └── Dockerfile
├── tradingagents/      # Core TradingAgents package
└── docker-compose.yml  # Docker orchestration
```

## 🔧 Backend API

### Available Endpoints

- `GET /api/health` - Health check
- `GET /api/config` - Get configuration options
- `POST /api/analyze` - Run trading analysis
- `GET /api/tickers` - Get popular tickers

### Example API Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "analysis_date": "2024-05-10",
    "research_depth": 1
  }'
```

## 🎨 Frontend Features

- **Modern UI**: Built with Next.js, React, and shadcn/ui
- **Type Safety**: Full TypeScript support
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live analysis status
- **Rich Visualizations**: Interactive reports and decisions

## 🛠️ Development

### Running Backend Only
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Running Frontend Only
```bash
cd frontend
npm install
npm run dev
```

## 📊 Using the Application

1. Navigate to http://localhost:3000
2. Click "Start Analysis" or go to the Analysis page
3. Configure your analysis parameters:
   - Stock ticker (e.g., NVDA, AAPL)
   - Analysis date
   - Research depth (1-5)
   - LLM models
4. Click "Run Analysis"
5. Wait for the multi-agent analysis to complete
6. Review the trading decision and detailed reports

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Use environment variables for sensitive data
- The backend validates all inputs using Pydantic
- CORS is configured for frontend-backend communication

## 🐛 Troubleshooting

### Backend Issues
- Check logs: `docker-compose logs backend`
- Verify API keys are set correctly
- Ensure port 8000 is not in use

### Frontend Issues
- Check logs: `docker-compose logs frontend`
- Verify backend is running
- Ensure port 3000 is not in use

### Network Issues
- Restart Docker: `docker-compose down && docker-compose up`
- Check network: `docker network ls`
- Verify services can communicate: `docker-compose exec frontend ping backend`

## 📝 License

This project follows the same license as TradingAgents.

## 🤝 Contributing

See the main README.md for contribution guidelines.
