from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[3]

PHOTO_DIR = APP_DIR / "data" / "object_photos"
VIDEO_DIR = APP_DIR / "data" / "object_videos"

PHOTO_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
VIDEO_EXTENSIONS = [".mp4"]


def resolve_object_photo(object_id: str) -> Path | None:
    for ext in PHOTO_EXTENSIONS:
        path = PHOTO_DIR / f"{object_id}{ext}"
        if path.exists():
            return path
    return None


def resolve_object_video(object_id: str) -> Path | None:
    for ext in VIDEO_EXTENSIONS:
        path = VIDEO_DIR / f"{object_id}{ext}"
        if path.exists():
            return path
    return None