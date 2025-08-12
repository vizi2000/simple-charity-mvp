from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any
import json
import qrcode
from io import BytesIO
import os

from ..models import Organization, CharityGoal

router = APIRouter(prefix="/api", tags=["organization"])

def load_organization() -> Organization:
    """Load organization data from JSON file"""
    try:
        with open("app/data/organization.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return Organization(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load organization data: {str(e)}")

@router.get("/organization")
async def get_organization() -> Organization:
    """Get the organization details"""
    return load_organization()

@router.get("/organization/goal/{goal_id}")
async def get_goal(goal_id: str) -> CharityGoal:
    """Get specific charity goal details"""
    org = load_organization()
    goal = next((g for g in org.goals if g.id == goal_id), None)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.get("/organization/stats")
async def get_stats() -> Dict[str, Any]:
    """Get organization statistics"""
    org = load_organization()
    total_target = sum(goal.target_amount for goal in org.goals)
    total_collected = sum(goal.collected_amount for goal in org.goals)
    
    return {
        "total_target": total_target,
        "total_collected": total_collected,
        "progress_percentage": round((total_collected / total_target * 100) if total_target > 0 else 0, 2),
        "goals_count": len(org.goals),
        "goals": [
            {
                "id": goal.id,
                "name": goal.name,
                "target": goal.target_amount,
                "collected": goal.collected_amount,
                "progress": round((goal.collected_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0, 2)
            }
            for goal in org.goals
        ]
    }

@router.get("/organization/qr/{goal_id}")
async def generate_qr_code(goal_id: str) -> Response:
    """Generate QR code for a specific charity goal"""
    org = load_organization()
    goal = next((g for g in org.goals if g.id == goal_id), None)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Generate URL for the goal donation page
    frontend_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    donation_url = f"{frontend_url}/cel/{goal_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(donation_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#2C4770", back_color="white")
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=qr-{goal_id}.png"
        }
    )