# ═══════════════════════════════════════════════════════════════════════════════
# OAuth API Routes - مسارات OAuth للموصلات (مُنفّذ بالكامل مع التشفير)
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from typing import Optional
import logging
from datetime import datetime, timedelta

from .connectors import (
    GoogleConnector, GoogleDriveConnector, MicrosoftOneDriveConnector,
    FacebookConnector, MessengerConnector, InstagramConnector,
    ThreadsConnector, TikTokConnector, SnapchatConnector,
    DiscordConnector, LinkedInConnector, GitHubConnector, RedditConnector
)
from .db_models import Connector as ConnectorModel, OAuthToken, ConnectorStatus
from .auth import get_current_user
from . import crypto
from .db import conn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oauth", tags=["OAuth"])

CONNECTOR_CLASSES = {
    "google": GoogleConnector,
    "google_drive": GoogleDriveConnector,
    "microsoft_onedrive": MicrosoftOneDriveConnector,
    "facebook": FacebookConnector,
    "messenger": MessengerConnector,
    "instagram": InstagramConnector,
    "threads": ThreadsConnector,
    "tiktok": TikTokConnector,
    "snapchat": SnapchatConnector,
    "discord": DiscordConnector,
    "linkedin": LinkedInConnector,
    "github": GitHubConnector,
    "reddit": RedditConnector,
}

@router.get("/{connector_type}/authorize")
async def oauth_authorize(
    connector_type: str,
    connector_id: str = Query(..., description="معرّف الموصل"),
    current_user = Depends(get_current_user),
):
    if connector_type not in CONNECTOR_CLASSES:
        raise HTTPException(status_code=400, detail=f"نوع الموصل '{connector_type}' غير مدعوم")
    
    connector_class = CONNECTOR_CLASSES[connector_type]
    connector_config = {
        "client_id": f"{connector_type.upper()}_CLIENT_ID", # TODO: من الإعدادات
        "redirect_uri": f"http://localhost:8000/api/v1/oauth/{connector_type}/callback",
    }
    
    connector = connector_class(connector_id=connector_id, name=f"{connector_type} Connector", config=connector_config)
    auth_url = connector.get_authorization_url(state=connector_id)
    return RedirectResponse(url=auth_url)

@router.get("/{connector_type}/callback")
async def oauth_callback(
    connector_type: str,
    code: str = Query(..., description="رمز التفويض"),
    state: Optional[str] = Query(None, description="معرّف الموصل"),
    error: Optional[str] = Query(None, description="خطأ OAuth"),
):
    if error:
        return RedirectResponse(url=f"/dashboard?oauth_error={error}")
    
    connector_id = state
    if not connector_id:
        raise HTTPException(status_code=400, detail="Missing state/connector_id")

    connector_class = CONNECTOR_CLASSES[connector_type]
    connector_config = {
        "client_id": f"{connector_type.upper()}_CLIENT_ID",
        "client_secret": f"{connector_type.upper()}_CLIENT_SECRET",
        "redirect_uri": f"http://localhost:8000/api/v1/oauth/{connector_type}/callback",
    }
    
    connector = connector_class(connector_id=connector_id, name=f"{connector_type} Connector", config=connector_config)
    
    try:
        tokens = await connector.exchange_code_for_token(code)
        
        # تشفير الرموز
        access_token_enc = crypto.encrypt(tokens.get("access_token", "").encode())
        refresh_token_enc = crypto.encrypt(tokens.get("refresh_token", "").encode()) if tokens.get("refresh_token") else None
        
        # حفظ في قاعدة البيانات
        with conn() as c:
            
            c.execute(
                "UPDATE connectors SET status = ?, updated_at = ? WHERE id = ?",
                (ConnectorStatus.ACTIVE.value, datetime.utcnow().isoformat(), connector_id)
            )
            # حفظ الرموز
            c.execute(
                """INSERT INTO oauth_tokens 
                   (connector_id, access_token_encrypted, refresh_token_encrypted, expires_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(connector_id) DO UPDATE SET
                   access_token_encrypted=excluded.access_token_encrypted,
                   refresh_token_encrypted=excluded.refresh_token_encrypted,
                   expires_at=excluded.expires_at,
                   updated_at=excluded.updated_at""",
                (
                    connector_id, access_token_enc, refresh_token_enc,
                    (datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))).isoformat(),
                    datetime.utcnow().isoformat(), datetime.utcnow().isoformat()
                )
            )
        
        return RedirectResponse(url=f"/dashboard?oauth_success=true&connector={connector_type}")
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        return RedirectResponse(url=f"/dashboard?oauth_error={str(e)}")
