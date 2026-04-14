# LBW DRS Web Application

Browser-based interface for the Cricket LBW Decision Review System. Upload cricket videos, mark ball trajectory, and get professional DRS-style analysis.

## Features

- **Drag & Drop Upload** - Easy video upload
- **Frame-by-Frame Navigation** - Precise frame control with slider
- **Interactive Point Marking** - Click to mark ball positions
- **Real-time Overlay** - See marked points on video
- **Professional Output** - Download DRS video and images
- **Responsive Design** - Works on desktop and tablet

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │────▶│  DRS Processing │
│  (HTML/JS/CSS)  │◀────│   (FastAPI)     │◀────│    (OpenCV)     │
│   Port 3000     │     │   Port 8000     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### 1. Install Dependencies

```bash
# From project root
cd web_app/backend
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
python main.py
```

Server runs at: http://localhost:8000  
API Docs at: http://localhost:8000/docs

### 3. Start Frontend Server

Open a new terminal:

```bash
cd web_app/frontend
python -m http.server 3000
```

Frontend runs at: http://localhost:3000

### 4. Use the Application

1. Open http://localhost:3000 in your browser
2. Upload a cricket video (MP4, AVI, MOV, WebM)
3. Use controls to navigate frames
4. Mark points:
   - **Ball Position** - Click on ball in each frame
   - **Pitching Point** - Where ball bounces
   - **Impact Point** - Where ball hits pad
   - **Wickets** - Click top-left then bottom-right of stumps
5. Click "Analyze LBW Decision"
6. Download results

## User Interface

### Marking Modes

| Mode | Color | Description |
|------|-------|-------------|
| Ball Position | 🟡 Yellow | Track ball through frames |
| Pitching | 🟢 Green | Where ball pitches |
| Impact | 🔴 Red | Where ball hits pad |
| Wickets | 🔵 Cyan | Stump boundaries |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play/Pause |
| ← / → | Previous/Next frame |

## API Reference

### Upload Video

```http
POST /upload
Content-Type: multipart/form-data

file: <video_file>
```

**Response:**
```json
{
  "video_id": "uuid-string",
  "filename": "original_name.mp4",
  "message": "Video uploaded successfully"
}
```

### Get Video Info

```http
GET /video/{video_id}/info
```

**Response:**
```json
{
  "video_id": "uuid-string",
  "width": 1280,
  "height": 720,
  "fps": 30.0,
  "total_frames": 300,
  "duration": 10.0
}
```

### Analyze DRS

```http
POST /analyze
Content-Type: application/json

{
  "video_id": "uuid-string",
  "trajectory": [
    {"frame": 10, "x": 500, "y": 300},
    {"frame": 15, "x": 520, "y": 350}
  ],
  "pitching_point": {"frame": 20, "x": 550, "y": 400},
  "impact_point": {"frame": 25, "x": 580, "y": 450},
  "wicket_rect": [600, 300, 650, 500]
}
```

**Response:**
```json
{
  "decision": "OUT",
  "reason": "Hitting stumps",
  "pitching_status": "In Line",
  "impact_status": "In Line",
  "wickets_status": "Hitting",
  "output_video": "/output/uuid_drs.mp4",
  "output_image": "/output/uuid_drs_final.png"
}
```

### Download Output

```http
GET /output/{filename}
```

## Deployment

### Option 1: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "web_app/backend/main.py"]
```

```bash
docker build -t lbw-drs .
docker run -p 8000:8000 lbw-drs
```

### Option 2: Railway.app

1. Connect GitHub repo
2. Set root directory to project root
3. Deploy automatically

### Option 3: Render.com

1. Create new Web Service
2. Connect repository
3. Build command: `pip install -r web_app/backend/requirements.txt`
4. Start command: `python web_app/backend/main.py`

### Option 4: AWS/GCP/Azure

Deploy backend as a container or VM, serve frontend via CDN/S3.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `UPLOAD_DIR` | uploads | Video upload directory |
| `OUTPUT_DIR` | outputs | Generated files directory |

### CORS Configuration

For production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Video not loading
- Ensure video format is supported (MP4, AVI, MOV, WebM)
- Check browser console for errors
- Verify backend is running

### CORS errors
- Ensure backend is running on port 8000
- Check browser console for specific CORS messages

### Processing fails
- Check backend terminal for error messages
- Ensure OpenCV is properly installed
- Verify all points are marked before analyzing

## Future Enhancements

- [ ] WebSocket for real-time processing progress
- [ ] User accounts and history
- [ ] Social media sharing
- [ ] Mobile app (React Native/Flutter)
- [ ] AI-powered automatic ball detection
- [ ] Multiple camera angle support
