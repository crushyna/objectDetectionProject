import os
from datetime import datetime
from typing import Optional
from .models.cognitivemodel import CognitiveModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
SNAPSHOTS_FOLDER = 'app/static/snapshots'

camera = cv2.VideoCapture(0)


class Session:
    def __init__(self, status: Optional[str] = None, snapshot: Optional[str] = None):
        self.status = status
        self.snapshot = snapshot
        self.snapshot_fullpath = None

    def clear(self):
        self.status = None
        self.snapshot = None
        self.snapshot_fullpath = None


session = Session()


def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, status='start',
                   nav_1='nav-link active',
                   nav_2='nav-link',
                   tab_1='tab-pane active',
                   tab_2='tab-pane'):
    session.clear()
    return templates.TemplateResponse("index.html", {"request": request, "status": status,
                                                     "nav_1": nav_1,
                                                     "nav_2": nav_2,
                                                     "tab_1": tab_1,
                                                     "tab_2": tab_2})


@app.get('/snapshot', response_class=HTMLResponse)
async def get_snapshot(request: Request, status='snapshot',
                       nav_1='nav-link',
                       nav_2='nav-link active',
                       tab_1='tab-pane',
                       tab_2='tab-pane active'):
    current_timestamp: str = datetime.now().strftime('%d%m%y%H%M%S')
    snapshot_filename = f'snapshot_{current_timestamp}.jpg'
    session.snapshot = snapshot_filename
    session.snapshot_fullpath = os.path.join(SNAPSHOTS_FOLDER, session.snapshot)
    success, frame = camera.read()
    cv2.imwrite(session.snapshot_fullpath, frame)
    return templates.TemplateResponse("index.html", {"request": request, "status": status,
                                                     "nav_1": nav_1,
                                                     "nav_2": nav_2,
                                                     "tab_1": tab_1,
                                                     "tab_2": tab_2,
                                                     "snapshot": session.snapshot})


@app.post('/process', response_class=HTMLResponse)
async def process_file(request: Request, status='snapshot'):
    cognitive_model = CognitiveModel(session.snapshot)
    cognitive_model.get_image_desc()
    return templates.TemplateResponse("results.html", {"request": request, "status": status,
                                                       "result_img": session.snapshot,
                                                       "result_desc": cognitive_model.description})
