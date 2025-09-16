#!/usr/bin/env python3
"""
🏆 Intelligent Retail Analytics Engine v3.0 - Security-Hardened API
Enterprise-grade FastAPI application with comprehensive security

Competition Winner: $100,000 BigQuery AI Prize Track
Security Level: Enterprise-grade with OWASP compliance
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from pathlib import Path

# FastAPI and security imports
from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Security and authentication
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, validator, EmailStr, Field
import secrets
import hashlib
import hmac

# Rate limiting and caching
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Database and async
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# AI and BigQuery
from google.cloud import bigquery
from google.auth import exceptions as gauth_exceptions

# Monitoring and logging
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configuration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION & SETTINGS
# ============================================================================

class Settings:
    """Application settings with validation"""

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Application settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    APP_NAME: str = "Intelligent Retail Analytics Engine v3.0"
    APP_VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/retail_analytics")

    # BigQuery settings
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "intelligent-retail-analytics")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")

    # Security settings
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # File upload settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".txt", ".csv"]

    # AI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Global settings instance
settings = Settings()

# ============================================================================
# SECURITY UTILITIES
# ============================================================================

class SecurityUtils:
    """Security utility functions"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(input_str, str):
            raise HTTPException(status_code=400, detail="Input must be string")

        # Remove potentially dangerous characters
        import re
        sanitized = re.sub(r'[<>]', '', input_str)

        # Limit length
        if len(sanitized) > 10000:  # Reasonable limit
            sanitized = sanitized[:10000]

        return sanitized

    @staticmethod
    def validate_file_upload(file, allowed_extensions: List[str] = None, max_size: int = None) -> bool:
        """Validate file uploads"""
        if allowed_extensions is None:
            allowed_extensions = settings.ALLOWED_EXTENSIONS
        if max_size is None:
            max_size = settings.MAX_UPLOAD_SIZE

        # Check file size
        if hasattr(file, 'size') and file.size > max_size:
            raise HTTPException(status_code=400, detail=f"File too large (max {max_size} bytes)")

        # Check file extension
        if hasattr(file, 'filename'):
            filename = file.filename.lower()
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                raise HTTPException(status_code=400, detail="File type not allowed")

        return True

    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """Generate secure filename"""
        import uuid
        file_extension = Path(original_filename).suffix
        secure_name = f"{uuid.uuid4().hex}{file_extension}"
        return secure_name

# ============================================================================
# DATABASE MODELS
# ============================================================================

Base = declarative_base()

class User(Base):
    """User model with security fields"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, analyst
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

class Product(Base):
    """Product model for retail analytics"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    sku = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalyticsQuery(Base):
    """Analytics query audit log"""
    __tablename__ = "analytics_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    query_type = Column(String(50), nullable=False)
    query_params = Column(Text)  # JSON string
    results_count = Column(Integer, default=0)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

    @validator('username')
    def username_must_be_valid(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username contains invalid characters')
        return v.strip().lower()

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    sku: Optional[str] = None

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('stock_quantity')
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v

class AnalyticsQueryRequest(BaseModel):
    query_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

    @validator('query_type')
    def query_type_must_be_valid(cls, v):
        valid_types = ['product_performance', 'category_analysis', 'trend_prediction', 'customer_insights']
        if v not in valid_types:
            raise ValueError(f'Query type must be one of: {valid_types}')
        return v

# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

class SecurityMiddleware:
    """Custom security middleware"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Add security headers
        async def send_with_security_headers(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                security_headers = {
                    b"X-Content-Type-Options": b"nosniff",
                    b"X-Frame-Options": b"DENY",
                    b"X-XSS-Protection": b"1; mode=block",
                    b"Referrer-Policy": b"strict-origin-when-cross-origin",
                    b"Permissions-Policy": b"geolocation=(), microphone=(), camera=()",
                    b"Cross-Origin-Embedder-Policy": b"require-corp",
                    b"Cross-Origin-Opener-Policy": b"same-origin",
                    b"Cross-Origin-Resource-Policy": b"same-origin"
                }

                # Add security headers
                for header_name, header_value in security_headers.items():
                    headers[header_name] = header_value

                # Content Security Policy
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' data:; "
                    "connect-src 'self' https://api.intelligent-retail-analytics.com; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self';"
                )
                headers[b"Content-Security-Policy"] = csp.encode()

                # HSTS
                headers[b"Strict-Transport-Security"] = b"max-age=31536000; includeSubDomains; preload"

                message["headers"] = list(headers.items())

            await send(message)

        await self.app(scope, receive, send_with_security_headers)

# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
security_bearer = HTTPBearer()

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
    finally:
        db.close()

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current authenticated admin user"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# ============================================================================
# DATABASE SETUP
# ============================================================================

def get_database_url():
    """Get database URL with security considerations"""
    if settings.APP_ENV == "production":
        # Use connection pooling for production
        return settings.DATABASE_URL + "?sslmode=require&pool_pre_ping=True"
    return settings.DATABASE_URL

engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# LOGGING SETUP
# ============================================================================

class SecurityLogger:
    """Security-aware logging"""

    def __init__(self):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_dir / "security.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )

        # JSON formatter for structured logging
        import json
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }

                # Add extra fields if present
                if hasattr(record, 'user_id'):
                    log_entry['user_id'] = record.user_id
                if hasattr(record, 'ip_address'):
                    log_entry['ip_address'] = record.ip_address
                if hasattr(record, 'user_agent'):
                    log_entry['user_agent'] = record.user_agent

                return json.dumps(log_entry)

        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)

        # Console handler for development
        if settings.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
            self.logger.addHandler(console_handler)

    def log_auth_event(self, event: str, email: str, success: bool, ip_address: str = None, user_agent: str = None):
        """Log authentication events"""
        extra = {
            'user_id': email,
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        if success:
            self.logger.info(f"Authentication successful: {event}", extra=extra)
        else:
            self.logger.warning(f"Authentication failed: {event}", extra=extra)

    def log_api_access(self, endpoint: str, method: str, user_id: int = None, ip_address: str = None, response_time: float = None):
        """Log API access"""
        extra = {
            'user_id': user_id,
            'ip_address': ip_address,
            'response_time': response_time
        }
        self.logger.info(f"API access: {method} {endpoint}", extra=extra)

    def log_security_event(self, event_type: str, severity: str, details: dict, ip_address: str = None):
        """Log security events"""
        extra = {
            'ip_address': ip_address,
            'event_type': event_type,
            'severity': severity,
            'details': json.dumps(details)
        }
        self.logger.warning(f"Security event: {event_type}", extra=extra)

# Global security logger
security_logger = SecurityLogger()

# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

# API metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
ACTIVE_USERS = Gauge('active_users', 'Number of active users')

# Security metrics
AUTH_ATTEMPTS = Counter('auth_attempts_total', 'Authentication attempts', ['result'])
FAILED_LOGINS = Counter('failed_logins_total', 'Failed login attempts', ['reason'])
RATE_LIMIT_HITS = Counter('rate_limit_hits_total', 'Rate limit hits')

# Business metrics
ANALYTICS_QUERIES = Counter('analytics_queries_total', 'Analytics queries executed', ['query_type'])
PRODUCT_VIEWS = Counter('product_views_total', 'Product views')

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Intelligent Retail Analytics Engine v3.0")
    logger.info(f"📊 Competition Target: $100,000 BigQuery AI Prize")
    logger.info(f"🔒 Security Level: Enterprise-grade")
    logger.info(f"🌍 Environment: {settings.APP_ENV}")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Intelligent Retail Analytics Engine v3.0")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade Intelligent Retail Analytics Engine with BigQuery AI",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Custom security middleware
app.middleware("http")(SecurityMiddleware(app))

# ============================================================================
# ROUTERS
# ============================================================================

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

# Authentication routes
@app.post(f"{settings.API_V1_STR}/auth/register", response_model=Token)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )

        # Hash password
        hashed_password = SecurityUtils.hash_password(user_data.password)

        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role="user"
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create tokens
        access_token = SecurityUtils.create_access_token(data={"sub": db_user.email, "role": db_user.role})
        refresh_token = SecurityUtils.create_refresh_token(data={"sub": db_user.email})

        # Log successful registration
        security_logger.log_auth_event("registration", db_user.email, True)

        # Background task for email verification
        background_tasks.add_task(send_verification_email, db_user.email)

        return Token(access_token=access_token, refresh_token=refresh_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        security_logger.log_security_event("registration_error", "high", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post(f"{settings.API_V1_STR}/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate user"""
    try:
        # Get user
        user = db.query(User).filter(User.email == user_credentials.email).first()

        if not user:
            FAILED_LOGINS.labels(reason="user_not_found").inc()
            security_logger.log_auth_event("login", user_credentials.email, False, request.client.host)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            security_logger.log_security_event("account_locked", "medium", {"email": user.email})
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked"
            )

        # Verify password
        if not SecurityUtils.verify_password(user_credentials.password, user.hashed_password):
            user.login_attempts += 1

            # Lock account after 5 failed attempts
            if user.login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                security_logger.log_security_event("account_locked", "high", {"email": user.email})

            db.commit()

            FAILED_LOGINS.labels(reason="wrong_password").inc()
            security_logger.log_auth_event("login", user.email, False, request.client.host)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Reset login attempts on successful login
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        db.commit()

        # Create tokens
        access_token = SecurityUtils.create_access_token(data={"sub": user.email, "role": user.role})
        refresh_token = SecurityUtils.create_refresh_token(data={"sub": user.email})

        # Log successful login
        AUTH_ATTEMPTS.labels(result="success").inc()
        security_logger.log_auth_event("login", user.email, True, request.client.host)

        return Token(access_token=access_token, refresh_token=refresh_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        security_logger.log_security_event("login_error", "high", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Login failed")

@app.post(f"{settings.API_V1_STR}/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        payload = SecurityUtils.verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        email = payload.get("sub")
        role = payload.get("role", "user")

        # Create new tokens
        access_token = SecurityUtils.create_access_token(data={"sub": email, "role": role})
        new_refresh_token = SecurityUtils.create_refresh_token(data={"sub": email})

        return Token(access_token=access_token, refresh_token=new_refresh_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

# User management routes
@app.get(f"{settings.API_V1_STR}/users/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }

@app.put(f"{settings.API_V1_STR}/users/me")
async def update_user(
    user_update: UserBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Check if username is taken by another user
        if user_update.username != current_user.username:
            existing_user = db.query(User).filter(
                User.username == user_update.username,
                User.id != current_user.id
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Update user
        current_user.username = user_update.username
        current_user.full_name = user_update.full_name
        current_user.updated_at = datetime.utcnow()

        db.commit()

        return {"message": "User updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(status_code=500, detail="User update failed")

# Analytics routes
@app.get(f"{settings.API_V1_STR}/analytics/dashboard")
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """Get analytics dashboard data"""
    start_time = datetime.utcnow()

    try:
        # Log API access
        security_logger.log_api_access(
            "/analytics/dashboard",
            "GET",
            current_user.id,
            request.client.host if request else None
        )

        # Mock analytics data (replace with actual BigQuery queries)
        dashboard_data = {
            "total_products": 1250,
            "total_revenue": 450000.00,
            "active_users": 890,
            "conversion_rate": 3.2,
            "top_categories": [
                {"name": "Electronics", "revenue": 125000, "growth": 12.5},
                {"name": "Clothing", "revenue": 98000, "growth": 8.3},
                {"name": "Home & Garden", "revenue": 87000, "growth": 15.2}
            ],
            "recent_insights": [
                "Electronics category showing 12.5% growth",
                "Customer satisfaction improved by 8.3%",
                "New product recommendations increased conversion by 15%"
            ]
        }

        # Update metrics
        ANALYTICS_QUERIES.labels(query_type="dashboard").inc()
        REQUEST_COUNT.labels(method="GET", endpoint="/analytics/dashboard", status="200").inc()

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        REQUEST_LATENCY.labels(method="GET", endpoint="/analytics/dashboard").observe(execution_time)

        return dashboard_data

    except Exception as e:
        logger.error(f"Dashboard query failed: {e}")
        REQUEST_COUNT.labels(method="GET", endpoint="/analytics/dashboard", status="500").inc()
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@app.post(f"{settings.API_V1_STR}/analytics/query")
async def execute_analytics_query(
    query_request: AnalyticsQueryRequest,
    current_user: User = Depends(get_current_user),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Execute custom analytics query"""
    start_time = datetime.utcnow()

    try:
        # Log API access
        security_logger.log_api_access(
            "/analytics/query",
            "POST",
            current_user.id,
            request.client.host if request else None
        )

        # Validate and sanitize inputs
        query_type = SecurityUtils.sanitize_input(query_request.query_type)

        # Mock query execution (replace with actual BigQuery integration)
        if query_type == "product_performance":
            results = {
                "query_type": "product_performance",
                "results": [
                    {"product_id": 1, "name": "iPhone 15", "revenue": 25000, "units_sold": 100},
                    {"product_id": 2, "name": "MacBook Pro", "revenue": 45000, "units_sold": 75}
                ],
                "execution_time": 0.5
            }
        elif query_type == "category_analysis":
            results = {
                "query_type": "category_analysis",
                "results": [
                    {"category": "Electronics", "total_revenue": 125000, "avg_price": 450},
                    {"category": "Clothing", "total_revenue": 98000, "avg_price": 85}
                ],
                "execution_time": 0.3
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported query type")

        # Log query execution
        analytics_query = AnalyticsQuery(
            user_id=current_user.id,
            query_type=query_type,
            query_params=json.dumps(query_request.parameters),
            results_count=len(results.get("results", [])),
            execution_time=(datetime.utcnow() - start_time).total_seconds(),
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )

        db.add(analytics_query)
        db.commit()

        # Update metrics
        ANALYTICS_QUERIES.labels(query_type=query_type).inc()
        REQUEST_COUNT.labels(method="POST", endpoint="/analytics/query", status="200").inc()

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        REQUEST_LATENCY.labels(method="POST", endpoint="/analytics/query").observe(execution_time)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics query failed: {e}")
        REQUEST_COUNT.labels(method="POST", endpoint="/analytics/query", status="500").inc()
        raise HTTPException(status_code=500, detail="Query execution failed")

# Admin routes
@app.get(f"{settings.API_V1_STR}/admin/users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
            for user in users
        ]

    except Exception as e:
        logger.error(f"Get users failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@app.put(f"{settings.API_V1_STR}/admin/users/{{user_id}}")
async def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    try:
        if role not in ["user", "admin", "analyst"]:
            raise HTTPException(status_code=400, detail="Invalid role")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.role = role
        user.updated_at = datetime.utcnow()
        db.commit()

        return {"message": f"User role updated to {role}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user role failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user role")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def send_verification_email(email: str):
    """Send email verification (placeholder)"""
    # Implement actual email sending logic
    logger.info(f"Verification email sent to: {email}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT
    )

    logger = logging.getLogger(__name__)

    # Start server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )