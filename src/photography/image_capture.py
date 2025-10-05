# image_capture.py
"""
Image capture module. Uses PiCamera if available; otherwise creates a small placeholder image.
Also provides a convenience wrapper to return a safe path.
"""
import time
import logging
from pathlib import Path
import uuid

logger = logging.getLogger("image_capture")

BASE = Path(__file__).resolve().parent
IMAGES_DIR = BASE.joinpath("footage", "images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

try:
    from picamera import PiCamera
    PICAMERA_AVAILABLE = True
except Exception:
    PICAMERA_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

def capture_image(filename: str = None, resolution=(1280,720)) -> str:
    filename = filename or f"image_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"
    out = IMAGES_DIR.joinpath(filename)
    if PICAMERA_AVAILABLE:
        try:
            with PiCamera() as cam:
                cam.resolution = resolution
                cam.capture(str(out))
                logger.info("Captured image to %s", out)
                return str(out)
        except Exception:
            logger.exception("PiCamera capture failed — falling back")
    # fallback to synthetic image if PIL available
    if PIL_AVAILABLE:
        try:
            img = Image.new("RGB", resolution, (60,60,80))
            d = ImageDraw.Draw(img)
            d.text((10,10), f"Kabot simulated {time.ctime()}", fill=(255,255,0))
            img.save(str(out), "JPEG")
            logger.info("Saved simulated image %s", out)
            return str(out)
        except Exception:
            logger.exception("PIL simulated image failed")
    # fallback: create a small binary file placeholder
    out.write_bytes(b"KABOT_PLACEHOLDER_IMAGE")
    logger.info("Wrote placeholder image %s", out)
    return str(out)
