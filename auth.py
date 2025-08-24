"""
BlackFang Intelligence - Authentication and Security
"""

import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings

# Security instance
security = HTTPBearer()

class AuthManager:
    """Comprehensive authentication and security management"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def hash_password(self, password: str) -> str:
        """
        Hash password securely using PBKDF2 with SHA-256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt (format: hash:salt)
        """
        # Generate random salt
        salt = secrets.token_hex(32)
        
        # Hash password with salt using PBKDF2
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations for security
        )
        
        return hashed.hex() + ':' + salt
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against stored hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored hash from database (format: hash:salt)
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            stored_hash, salt = hashed_password.split(':')
            
            # Hash the provided password with stored salt
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            # Constant-time comparison to prevent timing attacks
            return secrets.compare_digest(computed_hash.hex(), stored_hash)
            
        except (ValueError, AttributeError):
            return False
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT access token
        
        Args:
            data: Token payload data
            
        Returns:
            JWT access token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create JWT refresh token
        
        Args:
            data: Token payload data
            
        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Decode and validate JWT token
        
        Args:
            token: JWT token string
            token_type: Expected token type ('access' or 'refresh')
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            # Check expiration (jwt library handles this, but explicit check)
            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def generate_api_key(self, company_id: int, key_name: str) -> str:
        """
        Generate API key for external integrations
        
        Args:
            company_id: Company ID
            key_name: Name/purpose of the API key
            
        Returns:
            Secure API key string
        """
        # Create unique identifier
        timestamp = int(datetime.utcnow().timestamp())
        random_part = secrets.token_hex(16)
        
        # Create API key with company prefix
        api_key = f"bf_{company_id}_{timestamp}_{random_part}"
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate API key format and extract metadata
        
        Args:
            api_key: API key to validate
            
        Returns:
            Dictionary with company_id and creation timestamp, or None if invalid
        """
        try:
            if not api_key.startswith("bf_"):
                return None
            
            parts = api_key.split("_")
            if len(parts) != 4:
                return None
            
            company_id = int(parts[1])
            timestamp = int(parts[2])
            
            return {
                "company_id": company_id,
                "created_at": datetime.fromtimestamp(timestamp),
                "key_format_valid": True
            }
            
        except (ValueError, IndexError):
            return None

# Global auth manager instance
auth_manager = AuthManager()

# Dependency functions for FastAPI
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        User data from token payload
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode the access token
        payload = auth_manager.decode_token(credentials.credentials, "access")
        
        # Extract user information
        company_id = payload.get("company_id")
        if not company_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload - missing company_id"
            )
        
        # Return user data (could be enhanced with database lookup)
        return {
            "id": company_id,
            "email": payload.get("email"),
            "subscription_plan": payload.get("subscription_plan"),
            "token_issued_at": payload.get("iat"),
            "token_expires_at": payload.get("exp")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current active user (extended version for additional checks)
    
    Args:
        current_user: User data from get_current_user
        
    Returns:
        Active user data
        
    Raises:
        HTTPException: If user is not active
    """
    # Here you could add additional checks like:
    # - Database lookup to verify user is still active
    # - Subscription status verification
    # - Rate limiting checks
    # - Permission level verification
    
    # For now, return the user data
    return current_user

async def verify_subscription_access(
    required_plan: str = "basic",
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify user has required subscription level
    
    Args:
        required_plan: Minimum required subscription plan
        current_user: Current user data
        
    Returns:
        User data if access granted
        
    Raises:
        HTTPException: If insufficient subscription level
    """
    user_plan = current_user.get("subscription_plan", "basic")
    
    # Define plan hierarchy
    plan_hierarchy = {
        "basic": 1,
        "professional": 2,
        "enterprise": 3
    }
    
    user_level = plan_hierarchy.get(user_plan, 0)
    required_level = plan_hierarchy.get(required_plan, 1)
    
    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Subscription upgrade required. Current: {user_plan}, Required: {required_plan}"
        )
    
    return current_user

# Utility functions for security
def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "score": 0
    }
    
    # Check length
    if len(password) < 8:
        result["errors"].append("Password must be at least 8 characters long")
        result["valid"] = False
    else:
        result["score"] += 1
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        result["errors"].append("Password must contain at least one uppercase letter")
        result["valid"] = False
    else:
        result["score"] += 1
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        result["errors"].append("Password must contain at least one lowercase letter")
        result["valid"] = False
    else:
        result["score"] += 1
    
    # Check for digits
    if not any(c.isdigit() for c in password):
        result["errors"].append("Password must contain at least one number")
        result["valid"] = False
    else:
        result["score"] += 1
    
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["errors"].append("Password must contain at least one special character")
        result["valid"] = False
    else:
        result["score"] += 1
    
    return result

def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    
    Args:
        length: Token length in bytes
        
    Returns:
        Hex-encoded secure token
    """
    return secrets.token_hex(length)

def create_password_reset_token(email: str) -> str:
    """
    Create password reset token
    
    Args:
        email: User email address
        
    Returns:
        Password reset token
    """
    data = {
        "email": email,
        "purpose": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    }
    
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token
    
    Args:
        token: Password reset token
        
    Returns:
        Email address if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        
        if payload.get("purpose") != "password_reset":
            return None
        
        return payload.get("email")
        
    except jwt.JWTError:
        return None

# Session management for refresh tokens
class SessionManager:
    """Manage user sessions and refresh tokens"""
    
    def __init__(self):
        self.active_sessions = {}  # In production, use Redis
    
    async def create_session(self, company_id: int, refresh_token: str) -> None:
        """Create user session"""
        # In production, store in database or Redis
        self.active_sessions[refresh_token] = {
            "company_id": company_id,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
    
    async def validate_session(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Validate session exists and is active"""
        return self.active_sessions.get(refresh_token)
    
    async def revoke_session(self, refresh_token: str) -> None:
        """Revoke user session"""
        if refresh_token in self.active_sessions:
            self.active_sessions[refresh_token]["is_active"] = False
    
    async def revoke_all_sessions(self, company_id: int) -> None:
        """Revoke all sessions for a user"""
        for session_data in self.active_sessions.values():
            if session_data["company_id"] == company_id:
                session_data["is_active"] = False

# Global session manager instance
session_manager = SessionManager()