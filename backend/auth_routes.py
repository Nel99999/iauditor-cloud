from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta, timezone
import httpx
from models import User, UserCreate, UserLogin, Session, Token, Organization, OrganizationCreate
from auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Dependency to get database from request state"""
    return request.app.state.db


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Register a new user with email and password"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create organization if provided
    organization_id = None
    if user_data.organization_name:
        org = Organization(
            name=user_data.organization_name,
            owner_id="",  # Will be updated after user creation
        )
        org_dict = org.model_dump()
        org_dict["created_at"] = org_dict["created_at"].isoformat()
        org_dict["updated_at"] = org_dict["updated_at"].isoformat()
        await db.organizations.insert_one(org_dict)
        organization_id = org.id
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        auth_provider="local",
        organization_id=organization_id,
        role="admin" if organization_id else "viewer",
    )
    
    user_dict = user.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    user_dict["updated_at"] = user_dict["updated_at"].isoformat()
    await db.users.insert_one(user_dict)
    
    # Update organization owner if created
    if organization_id:
        await db.organizations.update_one(
            {"id": organization_id},
            {"$set": {"owner_id": user.id}}
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Return token and user data (without password hash)
    user_response = user.model_dump()
    user_response.pop("password_hash", None)
    
    return Token(access_token=access_token, user=user_response)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Login with email and password"""
    # Find user
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not user.get("password_hash") or not verify_password(
        credentials.password, user["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Return token and user data (without password hash)
    user.pop("password_hash", None)
    
    return Token(access_token=access_token, user=user)


@router.get("/me")
async def get_me(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get current user information"""
    user = await get_current_user(request, db)
    user.pop("password_hash", None)
    return user


@router.post("/logout")
async def logout(response: Response, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Logout user (clear session)"""
    # Get session token from cookie
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        await db.sessions.delete_one({"session_token": session_token})
        
        # Clear cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="none"
        )
    
    return {"message": "Logged out successfully"}


@router.post("/google/callback")
async def google_oauth_callback(
    session_id: str,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Handle Google OAuth callback and create session"""
    # Call Emergent auth service to get session data
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            auth_response.raise_for_status()
            session_data = auth_response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to validate session: {str(e)}",
            )
    
    # Extract user data
    email = session_data.get("email")
    name = session_data.get("name")
    picture = session_data.get("picture")
    session_token = session_data.get("session_token")
    
    if not email or not session_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session data",
        )
    
    # Check if user exists
    user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if not user:
        # Create new user
        new_user = User(
            email=email,
            name=name or email.split("@")[0],
            picture=picture,
            auth_provider="google",
            role="viewer",
        )
        user_dict = new_user.model_dump()
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        user_dict["updated_at"] = user_dict["updated_at"].isoformat()
        await db.users.insert_one(user_dict)
        user = user_dict
    
    # Create session
    session = Session(
        user_id=user["id"],
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    
    session_dict = session.model_dump()
    session_dict["expires_at"] = session_dict["expires_at"].isoformat()
    session_dict["created_at"] = session_dict["created_at"].isoformat()
    await db.sessions.insert_one(session_dict)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    
    # Return user data (without password hash)
    user.pop("password_hash", None)
    
    return {"user": user, "message": "Authentication successful"}