from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("")
@router.get("/live")
async def health_live() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def health_ready() -> Dict[str, Any]:
    # Could check Redis here in a real scenario
    return {"status": "ready", "checks": {"redis": "ok"}}  # Mocked for now
