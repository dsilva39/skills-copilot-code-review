"""
Announcement endpoints for the High School Management System API
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


def _to_utc_iso(date_value: datetime) -> str:
    """Convert datetime value to normalized UTC ISO string."""
    return date_value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: Optional[str], field_name: str, required: bool = False) -> Optional[datetime]:
    if value is None or value == "":
        if required:
            raise HTTPException(status_code=400, detail=f"{field_name} is required")
        return None

    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} format")

    raw_value = value.strip()
    try:
        normalized = raw_value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name} format") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def _require_teacher(username: Optional[str]) -> Dict[str, Any]:
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    return teacher


def _serialize_announcement(announcement_doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": announcement_doc.get("_id"),
        "message": announcement_doc.get("message", ""),
        "starts_at": announcement_doc.get("starts_at"),
        "expires_at": announcement_doc.get("expires_at"),
        "created_at": announcement_doc.get("created_at"),
        "updated_at": announcement_doc.get("updated_at"),
    }


@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get active announcements that should be shown on the public interface."""
    now_iso = _to_utc_iso(datetime.now(timezone.utc))
    query = {
        "expires_at": {"$gte": now_iso},
        "$or": [
            {"starts_at": None},
            {"starts_at": {"$exists": False}},
            {"starts_at": {"$lte": now_iso}},
        ],
    }

    announcements = announcements_collection.find(query).sort("expires_at", 1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.get("", response_model=List[Dict[str, Any]])
def get_all_announcements(teacher_username: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    """List all announcements (requires authenticated teacher)."""
    _require_teacher(teacher_username)
    announcements = announcements_collection.find({}).sort("created_at", -1)
    return [_serialize_announcement(announcement) for announcement in announcements]


@router.post("", response_model=Dict[str, Any])
def create_announcement(payload: Dict[str, Any], teacher_username: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Create a new announcement (requires authenticated teacher)."""
    _require_teacher(teacher_username)

    message = str(payload.get("message", "")).strip()
    if not message:
        raise HTTPException(status_code=400, detail="Announcement message is required")

    starts_at = _parse_datetime(payload.get("starts_at"), "starts_at")
    expires_at = _parse_datetime(payload.get("expires_at"), "expires_at", required=True)

    if starts_at and starts_at > expires_at:
        raise HTTPException(status_code=400, detail="starts_at cannot be later than expires_at")

    now_utc = datetime.now(timezone.utc)
    announcement_doc = {
        "_id": str(uuid4()),
        "message": message,
        "starts_at": _to_utc_iso(starts_at) if starts_at else None,
        "expires_at": _to_utc_iso(expires_at),
        "created_at": _to_utc_iso(now_utc),
        "updated_at": _to_utc_iso(now_utc),
    }

    announcements_collection.insert_one(announcement_doc)
    return _serialize_announcement(announcement_doc)


@router.put("/{announcement_id}", response_model=Dict[str, Any])
def update_announcement(announcement_id: str, payload: Dict[str, Any], teacher_username: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Update an existing announcement (requires authenticated teacher)."""
    _require_teacher(teacher_username)

    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")

    message = str(payload.get("message", "")).strip()
    if not message:
        raise HTTPException(status_code=400, detail="Announcement message is required")

    starts_at = _parse_datetime(payload.get("starts_at"), "starts_at")
    expires_at = _parse_datetime(payload.get("expires_at"), "expires_at", required=True)

    if starts_at and starts_at > expires_at:
        raise HTTPException(status_code=400, detail="starts_at cannot be later than expires_at")

    updated_doc = {
        "message": message,
        "starts_at": _to_utc_iso(starts_at) if starts_at else None,
        "expires_at": _to_utc_iso(expires_at),
        "updated_at": _to_utc_iso(datetime.now(timezone.utc)),
    }

    announcements_collection.update_one({"_id": announcement_id}, {"$set": updated_doc})

    merged = {**existing, **updated_doc}
    return _serialize_announcement(merged)


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, teacher_username: Optional[str] = Query(None)) -> Dict[str, str]:
    """Delete announcement by id (requires authenticated teacher)."""
    _require_teacher(teacher_username)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
