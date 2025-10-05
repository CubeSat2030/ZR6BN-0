"""
Helper to collect files (logs + images + videos) and queue them for upload using DownlinkManager.
This will embed small files as base64 JSON and mark larger files for external handling.
"""
import logging
import base64
from pathlib import Path
from typing import List
from src.logger.utils import DATA_DIR

logger = logging.getLogger("network.upload_utils")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def list_all_files() -> List[Path]:
    files = []
    # logger data
    for p in DATA_DIR.rglob("*"):
        if p.is_file():
            files.append(p)
    # images and videos
    footage = PROJECT_ROOT.joinpath("photography","footage")
    if footage.exists():
        for p in footage.rglob("*"):
            if p.is_file():
                files.append(p)
    return files

def queue_all_files_for_upload(downlink):
    files = list_all_files()
    total = len(files)
    logger.info("Queueing %d files for upload", total)
    for idx, p in enumerate(files, start=1):
        try:
            size = p.stat().st_size
            if size <= 200*1024:
                b = p.read_bytes()
                payload = {"file": str(p.relative_to(PROJECT_ROOT)), "size": size, "content_b64": base64.b64encode(b).decode("ascii")}
                downlink.queue_payload({"file_upload": payload, "timestamp": time.time()})
            else:
                # large file: queue metadata, downlink should implement specialized file transfer
                downlink.queue_payload({"file_upload": {"file": str(p.relative_to(PROJECT_ROOT)), "size": size, "method": "external"}, "timestamp": time.time()})
            logger.info("Queued %s (%d/%d)", p, idx, total)
        except Exception:
            logger.exception("Failed to queue %s", p)
