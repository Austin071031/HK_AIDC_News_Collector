
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from hk_aidc_news.db import get_session
from hk_aidc_news.models.analyst_action import AnalystAction
from hk_aidc_news.models.cluster import Cluster

router = APIRouter(prefix="/api/clusters", tags=["actions"])

class ActionPayload(BaseModel):
    is_hidden: bool = False
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: Optional[list] = None

@router.post("/{cluster_id}/actions")
def submit_action(
    cluster_id: int, 
    payload: ActionPayload, 
    db: Session = Depends(get_session)
) -> dict:
    cluster = db.get(Cluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    action = db.scalar(select(AnalystAction).where(AnalystAction.cluster_id == cluster_id))
    if not action:
        action = AnalystAction(cluster_id=cluster_id)
        db.add(action)
        
    action.is_hidden = payload.is_hidden
    action.is_favorite = payload.is_favorite
    action.notes = payload.notes
    action.tags = ",".join(payload.tags) if payload.tags else ""
    
    db.commit()
    
    return {"status": "ok"}