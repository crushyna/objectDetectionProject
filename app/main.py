import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
SNAPSHOTS_FOLDER = 'app/static/snapshots'

camera = cv2.VideoCapture(0)


class Session(BaseModel):
    status: Optional[str]


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
async def homepage(request: Request, status='start'):
    return templates.TemplateResponse("index.html", {"request": request, "status": status})


@app.get('/snapshot', response_class=HTMLResponse)
def get_snapshot(request: Request, status='snapshot'):
    current_timestamp: str = datetime.now().strftime('%d%m%y')
    snapshot_filename = f'snapshot_{current_timestamp}.jpg'
    success, frame = camera.read()
    cv2.imwrite(os.path.join(SNAPSHOTS_FOLDER, snapshot_filename), frame)
    return templates.TemplateResponse("index.html", {"request": request, "status": status})