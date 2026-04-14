# LBW DRS Web Application

Web-based interface for the Cricket LBW Decision Review System.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │
│  (HTML/JS/CSS)  │◀────│   (FastAPI)     │
└─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │  DRS Processing │
                        │   (OpenCV)      │
                        └─────────────────┘
```

## Quick Start

### 1. Start Backend Server

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs at: http://localhost:8000

### 2. Open Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit: http://localhost:3000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload video file |
| `/video/{id}/info` | GET | Get video metadata |
| `/video/{id}/frame/{num}` | GET | Get specific frame |
| `/analyze` | POST | Process and generate DRS output |
| `/output/{filename}` | GET | Download output files |

## Deployment Options

### Option 1: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r backend/requirements.txt
EXPOSE 8000
CMD ["python", "backend/main.py"]
```

### Option 2: Cloud Platforms

- **Railway.app** - Easy Python deployment
- **Render.com** - Free tier available
- **AWS EC2** - Full control
- **Google Cloud Run** - Serverless

### Option 3: Vercel + Railway

- Frontend on Vercel (free)
- Backend on Railway (free tier)

## Future Enhancements

1. **Real-time Processing** - WebSocket for progress updates
2. **User Accounts** - Save analysis history
3. **Social Sharing** - Share results on social media
4. **Mobile App** - React Native / Flutter wrapper
5. **AI Ball Detection** - Automatic ball tracking with ML
