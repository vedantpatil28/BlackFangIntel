"""
BlackFang Intelligence - Authentication API Endpoints
"""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from models import (
    UserLogin, Token, RefreshToken, CompanyCreate, CompanyResponse, 
    APIResponse, TokenData
)
from auth import auth_manager, session_manager, security, validate_password_strength
from database import get_company_by_email, db_pool
from config import settings

# Configure router
auth_router = APIRouter()
logger = logging.getLogger(__name__)

@auth_router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """
    Authenticate user and return access tokens
    
    Args:
        login_data: User login credentials
        
    Returns:
        Authentication tokens and user information
    """
    try:
        email = login_data.email.lower().strip()
        password = login_data.password
        
        # Demo authentication for development/testing
        if email == settings.DEMO_EMAIL and password == settings.DEMO_PASSWORD:
            # Create demo user tokens
            token_data = {
                "company_id": 1,
                "email": email,
                "subscription_plan": "professional"
            }
            
            access_token = auth_manager.create_access_token(token_data)
            refresh_token = auth_manager.create_refresh_token(token_data)
            
            # Create session
            await session_manager.create_session(1, refresh_token)
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": auth_manager.access_token_expire_minutes * 60,
                "user": {
                    "id": 1,
                    "name": "Demo Automotive Dealership",
                    "email": email,
                    "company_name": "Demo Motors Pvt Ltd",
                    "subscription_plan": "professional",
                    "monthly_fee": 45000
                }
            }
        
        # Database authentication
        if db_pool:
            async with db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM companies WHERE email = $1 AND is_active = TRUE",
                    email
                )
                
                if user and auth_manager.verify_password(password, user['password_hash']):
                    # Create authentication tokens
                    token_data = {
                        "company_id": user['id'],
                        "email": user['email'],
                        "subscription_plan": user['subscription_plan']
                    }
                    
                    access_token = auth_manager.create_access_token(token_data)
                    refresh_token = auth_manager.create_refresh_token(token_data)
                    
                    # Create session
                    await session_manager.create_session(user['id'], refresh_token)
                    
                    # Update last login timestamp
                    await conn.execute(
                        "UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE id = $1",
                        user['id']
                    )
                    
                    logger.info(f"User {email} authenticated successfully")
                    
                    return {
                        "success": True,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "expires_in": auth_manager.access_token_expire_minutes * 60,
                        "user": {
                            "id": user['id'],
                            "name": user['name'],
                            "email": user['email'],
                            "company_name": user['company_name'],
                            "subscription_plan": user['subscription_plan'],
                            "monthly_fee": user['monthly_fee'],
                            "industry": user['industry']
                        }
                    }
        
        # Authentication failed
        logger.warning(f"Failed authentication attempt for {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_data: RefreshToken):
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token data
        
    Returns:
        New access token
    """
    try:
        # Validate refresh token
        payload = auth_manager.decode_token(refresh_data.refresh_token, "refresh")
        
        # Check if session is still active
        session = await session_manager.validate_session(refresh_data.refresh_token)
        if not session or not session.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid"
            )
        
        # Create new access token
        token_data = {
            "company_id": payload["company_id"],
            "email": payload["email"],
            "subscription_plan": payload.get("subscription_plan")
        }
        
        new_access_token = auth_manager.create_access_token(token_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": auth_manager.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@auth_router.post("/register", response_model=APIResponse)
async def register_company(company_data: CompanyCreate):
    """
    Register new company account
    
    Args:
        company_data: Company registration data
        
    Returns:
        Registration result
    """
    try:
        # Validate password strength
        password_validation = validate_password_strength(company_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "errors": password_validation["errors"]
                }
            )
        
        if not db_pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registration service temporarily unavailable"
            )
        
        email = company_data.email.lower().strip()
        
        async with db_pool.acquire() as conn:
            # Check if email already exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM companies WHERE email = $1",
                email
            )
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email address already registered"
                )
            
            # Hash password
            password_hash = auth_manager.hash_password(company_data.password)
            
            # Determine pricing based on subscription plan
            monthly_fee_map = {
                "basic": settings.BASIC_PLAN_PRICE,
                "professional": settings.PROFESSIONAL_PLAN_PRICE,
                "enterprise": settings.ENTERPRISE_PLAN_PRICE
            }
            monthly_fee = monthly_fee_map.get(company_data.subscription_plan, 45000)
            
            # Create company record
            company_id = await conn.fetchval("""
                INSERT INTO companies (
                    name, email, password_hash, company_name, 
                    industry, subscription_plan, monthly_fee
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """,
                company_data.name,
                email,
                password_hash,
                company_data.company_name,
                company_data.industry,
                company_data.subscription_plan,
                monthly_fee
            )
            
            logger.info(f"New company registered: {email} (ID: {company_id})")
            
            return {
                "success": True,
                "message": "Company registered successfully",
                "data": {
                    "company_id": company_id,
                    "email": email,
                    "subscription_plan": company_data.subscription_plan
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )

@auth_router.post("/logout", response_model=APIResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user and revoke session
    
    Args:
        credentials: JWT credentials
        
    Returns:
        Logout confirmation
    """
    try:
        # Decode token to get user info
        payload = auth_manager.decode_token(credentials.credentials, "access")
        company_id = payload.get("company_id")
        
        # Revoke all sessions for this user
        await session_manager.revoke_all_sessions(company_id)
        
        logger.info(f"User {company_id} logged out successfully")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if there's an error, return success for security
        return {
            "success": True,
            "message": "Logged out successfully"
        }

@auth_router.get("/me", response_model=CompanyResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current user information
    
    Args:
        credentials: JWT credentials
        
    Returns:
        Current user data
    """
    try:
        # Decode token
        payload = auth_manager.decode_token(credentials.credentials, "access")
        company_id = payload.get("company_id")
        
        # Demo user response
        if company_id == 1 and payload.get("email") == settings.DEMO_EMAIL:
            return {
                "id": 1,
                "name": "Demo Automotive Dealership",
                "email": settings.DEMO_EMAIL,
                "company_name": "Demo Motors Pvt Ltd",
                "industry": "Automotive",
                "subscription_plan": "professional",
                "monthly_fee": 45000,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
        
        # Database lookup for real users
        if db_pool:
            async with db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM companies WHERE id = $1 AND is_active = TRUE",
                    company_id
                )
                
                if user:
                    return dict(user)
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve user information"
        )

@auth_router.post("/change-password", response_model=APIResponse)
async def change_password(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Change user password
    
    Args:
        request: HTTP request containing old and new passwords
        credentials: JWT credentials
        
    Returns:
        Password change confirmation
    """
    try:
        # Get request data
        data = await request.json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        
        if not old_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password and new password are required"
            )
        
        # Validate new password strength
        password_validation = validate_password_strength(new_password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "New password does not meet security requirements",
                    "errors": password_validation["errors"]
                }
            )
        
        # Get current user
        payload = auth_manager.decode_token(credentials.credentials, "access")
        company_id = payload.get("company_id")
        
        if not db_pool:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Password change service temporarily unavailable"
            )
        
        async with db_pool.acquire() as conn:
            # Get current user data
            user = await conn.fetchrow(
                "SELECT password_hash FROM companies WHERE id = $1 AND is_active = TRUE",
                company_id
            )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify old password
            if not auth_manager.verify_password(old_password, user['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_password_hash = auth_manager.hash_password(new_password)
            
            # Update password
            await conn.execute("""
                UPDATE companies 
                SET password_hash = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, new_password_hash, company_id)
            
            # Revoke all sessions to force re-login
            await session_manager.revoke_all_sessions(company_id)
            
            logger.info(f"Password changed for user {company_id}")
            
            return {
                "success": True,
                "message": "Password changed successfully. Please login again."
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed due to server error"
        )

@auth_router.post("/validate-token", response_model=Dict[str, Any])
async def validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate JWT token and return token info
    
    Args:
        credentials: JWT credentials
        
    Returns:
        Token validation result
    """
    try:
        payload = auth_manager.decode_token(credentials.credentials, "access")
        
        return {
            "valid": True,
            "company_id": payload.get("company_id"),
            "email": payload.get("email"),
            "subscription_plan": payload.get("subscription_plan"),
            "expires_at": payload.get("exp"),
            "issued_at": payload.get("iat")
        }
        
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail
        }
    except Exception as e:
        return {
            "valid": False,
            "error": "Token validation failed"
        }