"""
LBW DRS Web API
FastAPI backend for processing cricket videos
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import uuid
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from drs_international import generate_international_drs_output

app = FastAPI(
    title="LBW DRS API",
    description="Cricket LBW Decision Review System API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TrajectoryPoint(BaseModel):
    frame: int
    x: int
    y: int


class DRSRequest(BaseModel):
    video_id: str
    trajectory: List[TrajectoryPoint]
    pitching_point: Optional[TrajectoryPoint]
    impact_point: Optional[TrajectoryPoint]
    wicket_rect: List[int]  # [x1, y1, x2, y2]


class DRSResponse(BaseModel):
    decision: str
    reason: str
    pitching_status: str
    impact_status: str
    wickets_status: str
    output_video: str
    output_image: str


@app.get("/")
def root():
    return {"message": "LBW DRS API", "version": "1.0.0"}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload a cricket video for analysis"""
    
    # Validate file type
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.webm')):
        raise HTTPException(400, "Invalid file type. Supported: mp4, avi, mov, webm")
    
    # Generate unique ID
    video_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{video_id}{file_ext}")
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "video_id": video_id,
        "filename": file.filename,
        "message": "Video uploaded successfully"
    }


@app.get("/video/{video_id}/frame/{frame_num}")
async def get_frame(video_id: str, frame_num: int):
    """Get a specific frame from the video"""
    import cv2
    
    # Find video file
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.webm']:
        path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(path):
            video_path = path
            break
    
    if not video_path:
        raise HTTPException(404, "Video not found")
    
    # Extract frame
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise HTTPException(400, "Could not read frame")
    
    # Save frame temporarily
    frame_path = os.path.join(OUTPUT_DIR, f"{video_id}_frame_{frame_num}.jpg")
    cv2.imwrite(frame_path, frame)
    
    return FileResponse(frame_path, media_type="image/jpeg")


@app.get("/video/{video_id}/info")
async def get_video_info(video_id: str):
    """Get video metadata"""
    import cv2
    
    # Find video file
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.webm']:
        path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")
        if os.path.exists(path):
            video_path = path
            break
    
    if not video_path:
        raise HTTPException(404, "Video not found")
    
    cap = cv2.VideoCapture(video_path)
    info = {
        "video_id": video_id,
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    }
    cap.release()
    
    return info


@app.post("/analyze", response_model=DRSResponse)
async def analyze_drs(request: DRSRequest):
    """Process the video with marked points and generate DRS output"""
    
    # Find video file
    video_path = None
    for ext in ['.mp4', '.avi', '.mov', '.webm']:
        path = os.path.join(UPLOAD_DIR, f"{request.video_id}{ext}")
        if os.path.exists(path):
            video_path = path
            break
    
    if not video_path:
        raise HTTPException(404, "Video not found")
    
    # Prepare trajectory data
    trajectory_data = {
        "video_path": video_path,
        "trajectory": [[p.frame, p.x, p.y] for p in request.trajectory],
        "pitching_point": [request.pitching_point.frame, request.pitching_point.x, request.pitching_point.y] if request.pitching_point else None,
        "impact_point": [request.impact_point.frame, request.impact_point.x, request.impact_point.y] if request.impact_point else None,
        "wicket_rect": request.wicket_rect
    }
    
    # Output paths
    output_video = os.path.join(OUTPUT_DIR, f"{request.video_id}_drs.mp4")
    
    # Generate DRS output
    try:
        results = generate_international_drs_output(video_path, output_video, trajectory_data)
    except Exception as e:
        raise HTTPException(500, f"Processing error: {str(e)}")
    
    output_image = output_video.replace('.mp4', '_final.png')
    
    return DRSResponse(
        decision=results['decision'],
        reason=results['reason'],
        pitching_status=results['pitching_status'],
        impact_status=results['impact_status'],
        wickets_status=results['wickets_status'],
        output_video=f"/output/{request.video_id}_drs.mp4",
        output_image=f"/output/{request.video_id}_drs_final.png"
    )


@app.get("/output/{filename}")
async def get_output(filename: str):
    """Download generated output files"""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    media_type = "video/mp4" if filename.endswith('.mp4') else "image/png"
    return FileResponse(file_path, media_type=media_type)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
