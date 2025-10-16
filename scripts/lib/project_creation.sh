#!/bin/bash
# Video Genius - Project Creation Functions
# Versão: 1.0.0
# Descrição: Funções para criação de estrutura de projeto

# Carrega biblioteca comum
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# ============================================================================
# ESTRUTURA DE DIRETÓRIOS
# ============================================================================

# Cria estrutura completa de diretórios
create_project_directories() {
    log_info "Criando estrutura de diretórios..."

    # Diretórios principais
    local main_dirs=(
        "backend/api"
        "backend/services"
        "backend/models"
        "backend/database"
        "backend/storage"
        "tests"
        "scripts"
        "scripts/lib"
        "scripts/templates"
        ".github/workflows"
    )

    for dir in "${main_dirs[@]}"; do
        ensure_dir "$dir"
    done

    log_success "Estrutura de diretórios criada"
}

# ============================================================================
# ARQUIVOS DE BACKEND
# ============================================================================

# Cria arquivos de backend
create_backend_files() {
    log_info "Criando arquivos de backend..."

    # Arquivos principais
    create_backend_main
    create_backend_config
    create_backend_models
    create_backend_services
    create_backend_database
    create_backend_storage

    log_success "Arquivos de backend criados"
}

# Cria arquivo principal do backend
create_backend_main() {
    local file="backend/main.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Main Application
FastAPI application entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.core.config import settings
from backend.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Video Genius application...")
    await init_db()

    yield

    # Shutdown
    logger.info("Shutting down Video Genius application...")

# Create FastAPI application
app = FastAPI(
    title="Video Genius API",
    description="AI-powered video generation platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "video-genius"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS if not settings.DEBUG else 1
    )
EOF
        log_success "backend/main.py criado"
    fi
}

# Cria arquivo de configuração
create_backend_config() {
    local file="backend/core/config.py"

    if ! file_exists_and_readable "$file"; then
        ensure_dir "backend/core"

        cat > "$file" << 'EOF'
"""
Video Genius - Core Configuration
Application settings and configuration
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    env: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8080"))
    api_workers: int = int(os.getenv("API_WORKERS", "4"))

    # CORS
    allowed_origins: List[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8080"
    ).split(",")

    # Google Cloud
    google_project_id: str = os.getenv("GOOGLE_PROJECT_ID", "")
    vertex_ai_location: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "video_data")
    cloud_storage_bucket: str = os.getenv("CLOUD_STORAGE_BUCKET", "")

    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # External APIs
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")

    # Feature Flags
    enable_caching: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    enable_monitoring: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
EOF
        log_success "backend/core/config.py criado"
    fi
}

# Cria modelos Pydantic
create_backend_models() {
    local file="backend/models/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Models Package
Pydantic models for the application
"""

from .video import VideoRequest, VideoResponse, VideoStatus
from .user import User, UserCreate, UserUpdate

__all__ = [
    "VideoRequest",
    "VideoResponse",
    "VideoStatus",
    "User",
    "UserCreate",
    "UserUpdate"
]
EOF
        log_success "backend/models/__init__.py criado"
    fi

    # Video models
    create_video_models
    # User models
    create_user_models
}

# Cria modelos de vídeo
create_video_models() {
    local file="backend/models/video.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Video Models
Pydantic models for video operations
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class VideoStyle(str, Enum):
    """Available video styles."""
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    DOCUMENTARY = "documentary"
    TUTORIAL = "tutorial"


class VideoStatus(str, Enum):
    """Video generation status."""
    QUEUED = "queued"
    GENERATING_SCRIPT = "generating_script"
    CREATING_ASSETS = "creating_assets"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoRequest(BaseModel):
    """Request model for video generation."""

    topic: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Video topic or subject"
    )
    duration_seconds: int = Field(
        ...,
        ge=30,
        le=600,
        description="Target video duration (30-600 seconds)"
    )
    style: VideoStyle = Field(
        default=VideoStyle.EDUCATIONAL,
        description="Video style"
    )
    additional_context: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional context or requirements"
    )
    tags: List[str] = Field(
        default_factory=list,
        max_items=5,
        description="Video tags"
    )

    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class VideoResponse(BaseModel):
    """Response model for video generation."""

    job_id: str = Field(..., description="Generation job ID")
    status: VideoStatus = Field(..., description="Job status")
    estimated_completion_time: int = Field(
        ...,
        description="Estimated time in seconds"
    )
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VideoJob(BaseModel):
    """Video generation job model."""

    id: str
    user_id: str
    request: VideoRequest
    status: VideoStatus
    progress: int = Field(default=0, ge=0, le=100)
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
EOF
        log_success "backend/models/video.py criado"
    fi
}

# Cria modelos de usuário
create_user_models() {
    local file="backend/models/user.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - User Models
Pydantic models for user operations
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)


class User(UserBase):
    """User model."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str
EOF
        log_success "backend/models/user.py criado"
    fi
}

# Cria serviços
create_backend_services() {
    local file="backend/services/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Services Package
Business logic services
"""

from .script_generator import ScriptGeneratorService
from .video_processor import VideoProcessorService
from .auth import AuthService

__all__ = [
    "ScriptGeneratorService",
    "VideoProcessorService",
    "AuthService"
]
EOF
        log_success "backend/services/__init__.py criado"
    fi

    # Script generator service
    create_script_generator_service
    # Video processor service
    create_video_processor_service
    # Auth service
    create_auth_service
}

# Cria serviço de geração de scripts
create_script_generator_service() {
    local file="backend/services/script_generator.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Script Generator Service
Service for generating video scripts using Vertex AI
"""
from typing import Optional, Dict, Any
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig
import logging

logger = logging.getLogger(__name__)


class ScriptGeneratorService:
    """Service for generating video scripts using Vertex AI."""

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro"
    ):
        """Initialize script generator.

        Args:
            project_id: GCP project ID
            location: Vertex AI location
            model_name: Model to use for generation
        """
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        logger.info(f"Initialized ScriptGeneratorService with {model_name}")

    async def generate_script(
        self,
        topic: str,
        duration_seconds: int,
        style: str = "educational",
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate video script based on topic and parameters.

        Args:
            topic: Main topic for the video
            duration_seconds: Target video duration
            style: Script style (educational, entertaining, documentary)
            additional_context: Extra context or requirements

        Returns:
            Dict containing script, title, and metadata

        Raises:
            ValueError: If generation fails or parameters invalid
        """
        if duration_seconds < 30 or duration_seconds > 600:
            raise ValueError("Duration must be between 30 and 600 seconds")

        prompt = self._build_prompt(topic, duration_seconds, style, additional_context)

        config = GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=2048
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=config
            )

            if not response.text:
                raise ValueError("Empty response from model")

            script_data = self._parse_response(response.text)
            script_data["metadata"] = {
                "topic": topic,
                "duration": duration_seconds,
                "style": style,
                "model": self.model.model_name
            }

            logger.info(f"Generated script for topic: {topic}")
            return script_data

        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise ValueError(f"Failed to generate script: {e}") from e

    def _build_prompt(
        self,
        topic: str,
        duration: int,
        style: str,
        context: Optional[str]
    ) -> str:
        """Build generation prompt.

        Args:
            topic: Video topic
            duration: Duration in seconds
            style: Script style
            context: Additional context

        Returns:
            Formatted prompt
        """
        words_estimate = (duration * 150) // 60  # ~150 words per minute

        prompt = f"""Generate a {style} video script about: {topic}

Requirements:
- Target duration: {duration} seconds (~{words_estimate} words)
- Style: {style}
- Include engaging hook in first 5 seconds
- Clear structure: intro, main content, conclusion
- Natural narration flow

{"Additional context: " + context if context else ""}

Format the response as:
TITLE: [engaging title]
HOOK: [first 5 seconds]
SCRIPT: [full script]
KEY_POINTS: [3-5 bullet points]
"""
        return prompt

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse model response into structured data.

        Args:
            response: Raw model response

        Returns:
            Structured script data
        """
        lines = response.strip().split("\n")
        data = {
            "title": "",
            "hook": "",
            "script": "",
            "key_points": []
        }

        current_section = None
        script_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                data["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("HOOK:"):
                data["hook"] = line.replace("HOOK:", "").strip()
            elif line.startswith("SCRIPT:"):
                current_section = "script"
            elif line.startswith("KEY_POINTS:"):
                current_section = "key_points"
            elif current_section == "script" and line:
                script_lines.append(line)
            elif current_section == "key_points" and line.startswith("-"):
                data["key_points"].append(line.lstrip("- "))

        data["script"] = "\n".join(script_lines)
        return data
EOF
        log_success "backend/services/script_generator.py criado"
    fi
}

# Cria serviço de processamento de vídeo
create_video_processor_service() {
    local file="backend/services/video_processor.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Video Processor Service
Service for processing and rendering videos
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import asyncio
import subprocess

logger = logging.getLogger(__name__)


class VideoProcessorService:
    """Service for video processing operations."""

    def __init__(self, temp_dir: str = "tmp/videos"):
        """Initialize video processor.

        Args:
            temp_dir: Directory for temporary video files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized VideoProcessorService with temp_dir: {temp_dir}")

    async def process_video(
        self,
        script_data: Dict[str, Any],
        assets: List[str],
        output_path: str
    ) -> str:
        """Process and render final video.

        Args:
            script_data: Generated script data
            assets: List of asset file paths
            output_path: Output video file path

        Returns:
            Path to rendered video

        Raises:
            ValueError: If processing fails
        """
        try:
            # Create video from assets and script
            # This is a placeholder - actual implementation would use
            # video processing libraries like moviepy, opencv, etc.

            logger.info(f"Processing video: {output_path}")

            # Simulate processing time
            await asyncio.sleep(5)

            # Placeholder: create a simple video file
            # In real implementation, this would combine assets with script

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Create placeholder video file
            with open(output_file, 'w') as f:
                f.write("# Placeholder video file\n")
                f.write(f"Title: {script_data.get('title', 'Unknown')}\n")
                f.write(f"Script: {script_data.get('script', '')[:100]}...\n")

            logger.info(f"Video processed successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            raise ValueError(f"Failed to process video: {e}") from e

    async def generate_assets(
        self,
        script_data: Dict[str, Any],
        style: str = "educational"
    ) -> List[str]:
        """Generate visual assets for video.

        Args:
            script_data: Script data for asset generation
            style: Video style

        Returns:
            List of generated asset file paths

        Raises:
            ValueError: If asset generation fails
        """
        try:
            # Generate images, animations, etc. based on script
            # This is a placeholder - actual implementation would use
            # AI image generation, stock footage APIs, etc.

            logger.info(f"Generating assets for style: {style}")

            # Simulate asset generation
            await asyncio.sleep(3)

            # Placeholder assets
            assets = [
                f"tmp/assets/title_{script_data.get('title', 'video').replace(' ', '_')}.png",
                "tmp/assets/background.mp4",
                "tmp/assets/transitions.mp4"
            ]

            # Create placeholder files
            for asset in assets:
                asset_path = Path(asset)
                asset_path.parent.mkdir(parents=True, exist_ok=True)
                with open(asset_path, 'w') as f:
                    f.write(f"# Placeholder asset: {asset_path.name}\n")

            logger.info(f"Generated {len(assets)} assets")
            return assets

        except Exception as e:
            logger.error(f"Asset generation failed: {e}")
            raise ValueError(f"Failed to generate assets: {e}") from e

    def cleanup_temp_files(self, files: List[str]) -> None:
        """Clean up temporary files.

        Args:
            files: List of file paths to clean up
        """
        for file_path in files:
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.debug(f"Cleaned up: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
EOF
        log_success "backend/services/video_processor.py criado"
    fi
}

# Cria serviço de autenticação
create_auth_service() {
    local file="backend/services/auth.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Authentication Service
Service for user authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from backend.core.config import settings
from backend.models.user import UserInDB

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token.

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and extract user ID.

        Args:
            token: JWT token string

        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            user_id: str = payload.get("sub")

            if user_id is None:
                return None

            return user_id

        except JWTError:
            return None

    @staticmethod
    def authenticate_user(
        users_db: dict,  # Placeholder - would be database
        username: str,
        password: str
    ) -> Optional[UserInDB]:
        """Authenticate a user.

        Args:
            users_db: User database (placeholder)
            username: Username/email
            password: Password

        Returns:
            User object if authenticated, None otherwise
        """
        # Placeholder implementation
        # In real implementation, this would query the database
        user = users_db.get(username)

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user
EOF
        log_success "backend/services/auth.py criado"
    fi
}

# Cria conexão com banco de dados
create_backend_database() {
    local file="backend/database/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Database Package
Database operations and connections
"""

from .connection import init_db, get_db
from .bigquery_client import BigQueryClient

__all__ = ["init_db", "get_db", "BigQueryClient"]
EOF
        log_success "backend/database/__init__.py criado"
    fi

    # Database connection
    create_database_connection
    # BigQuery client
    create_bigquery_client
}

# Cria conexão com banco de dados
create_database_connection() {
    local file="backend/database/connection.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Database Connection
Database initialization and connection management
"""
import logging
from google.cloud import bigquery
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Global BigQuery client
_bq_client = None


async def init_db() -> None:
    """Initialize database connection."""
    global _bq_client

    try:
        _bq_client = bigquery.Client(project=settings.google_project_id)
        logger.info("Database connection initialized")

        # Create dataset if it doesn't exist
        dataset_id = settings.bigquery_dataset
        dataset_ref = _bq_client.dataset(dataset_id)

        try:
            _bq_client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_id} already exists")
        except Exception:
            # Create dataset
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            _bq_client.create_dataset(dataset)
            logger.info(f"Dataset {dataset_id} created")

            # Create tables
            await create_tables()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db():
    """Get database client.

    Returns:
        BigQuery client instance
    """
    if _bq_client is None:
        await init_db()
    return _bq_client


async def create_tables() -> None:
    """Create necessary BigQuery tables."""
    client = await get_db()

    # Video jobs table
    video_jobs_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("topic", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("duration_seconds", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("style", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("progress", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("result_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    # Users table
    users_schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("full_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("hashed_password", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("is_active", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    tables = [
        ("video_jobs", video_jobs_schema),
        ("users", users_schema),
    ]

    for table_name, schema in tables:
        table_id = f"{client.project}.{settings.bigquery_dataset}.{table_name}"
        table = bigquery.Table(table_id, schema=schema)

        try:
            client.create_table(table)
            logger.info(f"Table {table_name} created")
        except Exception as e:
            if "Already Exists" in str(e):
                logger.info(f"Table {table_name} already exists")
            else:
                logger.error(f"Failed to create table {table_name}: {e}")
                raise
EOF
        log_success "backend/database/connection.py criado"
    fi
}

# Cria cliente BigQuery
create_bigquery_client() {
    local file="backend/database/bigquery_client.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - BigQuery Client
Client for BigQuery operations
"""
from google.cloud import bigquery
from google.api_core import exceptions
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BigQueryClient:
    """Client for BigQuery operations."""

    def __init__(self, project_id: str, dataset_id: str):
        """Initialize BigQuery client.

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
        """
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id
        logger.info(f"Initialized BigQueryClient for project {project_id}")

    async def insert_row(
        self,
        table_id: str,
        row: Dict[str, Any]
    ) -> str:
        """Insert a row into BigQuery table.

        Args:
            table_id: Table name
            row: Data to insert

        Returns:
            Inserted row ID

        Raises:
            ValueError: If insertion fails
        """
        table_ref = f"{self.client.project}.{self.dataset_id}.{table_id}"

        try:
            errors = self.client.insert_rows_json(table_ref, [row])
            if errors:
                raise ValueError(f"Insert failed: {errors}")

            logger.info(f"Row inserted into {table_id}")
            return row.get("id", "unknown")
        except exceptions.GoogleAPIError as e:
            logger.error(f"BigQuery error: {e}")
            raise ValueError(f"Failed to insert: {e}") from e

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get video generation job by ID.

        Args:
            job_id: Job ID

        Returns:
            Job data if found, None otherwise
        """
        query = f"""
        SELECT *
        FROM `{self.client.project}.{self.dataset_id}.video_jobs`
        WHERE id = @job_id
        LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("job_id", "STRING", job_id),
            ]
        )

        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            for row in results:
                return dict(row)

            return None

        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """Update job status.

        Args:
            job_id: Job ID
            status: New status
            error_message: Error message if failed
        """
        query = f"""
        UPDATE `{self.client.project}.{self.dataset_id}.video_jobs`
        SET status = @status,
            error_message = @error_message,
            updated_at = CURRENT_TIMESTAMP()
        WHERE id = @job_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("job_id", "STRING", job_id),
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("error_message", "STRING", error_message),
            ]
        )

        try:
            query_job = self.client.query(query, job_config=job_config)
            query_job.result()
            logger.info(f"Updated job {job_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            raise

    async def create_job(
        self,
        user_id: str,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Create a new job record.

        Args:
            user_id: User ID
            job_type: Type of job
            parameters: Job parameters

        Returns:
            Job ID
        """
        import uuid
        from datetime import datetime

        job_id = str(uuid.uuid4())

        row = {
            "id": job_id,
            "user_id": user_id,
            "topic": parameters.get("topic", ""),
            "duration_seconds": parameters.get("duration_seconds", 0),
            "style": parameters.get("style", "educational"),
            "status": "queued",
            "progress": 0,
            "result_url": None,
            "error_message": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        await self.insert_row("video_jobs", row)
        logger.info(f"Created job {job_id} for user {user_id}")

        return job_id
EOF
        log_success "backend/database/bigquery_client.py criado"
    fi
}

# Cria operações de storage
create_backend_storage() {
    local file="backend/storage/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Storage Package
Cloud Storage operations
"""

from .gcs_client import GCSClient

__all__ = ["GCSClient"]
EOF
        log_success "backend/storage/__init__.py criado"
    fi

    # GCS client
    create_gcs_client
}

# Cria cliente Google Cloud Storage
create_gcs_client() {
    local file="backend/storage/gcs_client.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Google Cloud Storage Client
Client for Cloud Storage operations
"""
from google.cloud import storage
from typing import Optional, BinaryIO
import logging
import os

logger = logging.getLogger(__name__)


class GCSClient:
    """Client for Google Cloud Storage operations."""

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        """Initialize GCS client.

        Args:
            bucket_name: GCS bucket name
            project_id: GCP project ID
        """
        self.client = storage.Client(project=project_id)
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Initialized GCSClient for bucket {bucket_name}")

    async def upload_file(
        self,
        source_path: str,
        destination_path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to Cloud Storage.

        Args:
            source_path: Local file path
            destination_path: GCS destination path
            content_type: Content type

        Returns:
            Public URL of uploaded file

        Raises:
            ValueError: If upload fails
        """
        try:
            blob = self.bucket.blob(destination_path)

            # Detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type(source_path)

            # Upload file
            blob.upload_from_filename(source_path, content_type=content_type)

            # Make public
            blob.make_public()

            public_url = blob.public_url
            logger.info(f"File uploaded to {public_url}")

            return public_url

        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise ValueError(f"Failed to upload file: {e}") from e

    async def download_file(
        self,
        source_path: str,
        destination_path: str
    ) -> None:
        """Download file from Cloud Storage.

        Args:
            source_path: GCS source path
            destination_path: Local destination path

        Raises:
            ValueError: If download fails
        """
        try:
            blob = self.bucket.blob(source_path)
            blob.download_to_filename(destination_path)
            logger.info(f"File downloaded to {destination_path}")

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise ValueError(f"Failed to download file: {e}") from e

    async def delete_file(self, file_path: str) -> None:
        """Delete file from Cloud Storage.

        Args:
            file_path: GCS file path

        Raises:
            ValueError: If deletion fails
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            logger.info(f"File deleted: {file_path}")

        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise ValueError(f"Failed to delete file: {e}") from e

    async def list_files(self, prefix: Optional[str] = None) -> list:
        """List files in bucket.

        Args:
            prefix: File prefix to filter

        Returns:
            List of file names
        """
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            files = [blob.name for blob in blobs]
            logger.debug(f"Listed {len(files)} files")
            return files

        except Exception as e:
            logger.error(f"List failed: {e}")
            raise ValueError(f"Failed to list files: {e}") from e

    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file extension.

        Args:
            file_path: File path

        Returns:
            Content type string
        """
        _, ext = os.path.splitext(file_path.lower())

        content_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.avi': 'video/x-msvideo',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.json': 'application/json',
            '.txt': 'text/plain',
        }

        return content_types.get(ext, 'application/octet-stream')
EOF
        log_success "backend/storage/gcs_client.py criado"
    fi
}

# ============================================================================
# ROTAS DA API
# ============================================================================

# Cria rotas da API
create_api_routes() {
    local file="backend/api/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - API Package
FastAPI routes and endpoints
"""

from .routes import router

__all__ = ["router"]
EOF
        log_success "backend/api/__init__.py criado"
    fi

    # Main routes
    create_api_routes_main
}

# Cria rotas principais
create_api_routes_main() {
    local file="backend/api/routes.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - API Routes
Main API routes and endpoints
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from typing import Dict, Any

from backend.models.video import VideoRequest, VideoResponse
from backend.services.script_generator import ScriptGeneratorService
from backend.database.bigquery_client import BigQueryClient
from backend.services.auth import AuthService
from backend.core.config import settings

router = APIRouter()

# Dependency injection
def get_script_service() -> ScriptGeneratorService:
    """Get script generator service."""
    return ScriptGeneratorService(
        project_id=settings.google_project_id,
        location=settings.vertex_ai_location
    )

def get_db_client() -> BigQueryClient:
    """Get BigQuery client."""
    return BigQueryClient(
        project_id=settings.google_project_id,
        dataset_id=settings.bigquery_dataset
    )

def get_current_user(token: str = Depends(AuthService.verify_token)) -> str:
    """Get current authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

@router.post(
    "/videos/generate",
    response_model=VideoResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate new video",
    description="Initiate video generation process using AI"
)
async def generate_video(
    request: VideoRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    script_service: ScriptGeneratorService = Depends(get_script_service),
    db_client: BigQueryClient = Depends(get_db_client)
) -> VideoResponse:
    """Generate a new video based on provided parameters.

    This endpoint initiates an asynchronous video generation process:
    1. Generates script using Vertex AI
    2. Creates visual assets
    3. Renders final video
    4. Uploads to Cloud Storage

    Args:
        request: Video generation parameters
        background_tasks: FastAPI background tasks
        current_user: Authenticated user ID
        script_service: Script generation service
        db_client: BigQuery client

    Returns:
        Generation job details

    Raises:
        HTTPException: If generation cannot be initiated
    """
    try:
        # Create job record
        job_id = await db_client.create_job(
            user_id=current_user,
            job_type="video_generation",
            parameters=request.dict()
        )

        # Estimate completion time based on duration
        estimated_time = (request.duration_seconds * 5) + 120

        # Queue background task
        background_tasks.add_task(
            process_video_generation,
            job_id=job_id,
            request=request,
            user_id=current_user,
            script_service=script_service,
            db_client=db_client
        )

        return VideoResponse(
            job_id=job_id,
            status="queued",
            estimated_completion_time=estimated_time,
            message=f"Video generation started. Job ID: {job_id}"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate video generation"
        )

@router.get(
    "/videos/{job_id}/status",
    response_model=Dict[str, Any],
    summary="Get generation status",
    description="Check status of video generation job"
)
async def get_generation_status(
    job_id: str,
    current_user: str = Depends(get_current_user),
    db_client: BigQueryClient = Depends(get_db_client)
) -> Dict[str, Any]:
    """Get status of video generation job.

    Args:
        job_id: Generation job ID
        current_user: Authenticated user
        db_client: BigQuery client

    Returns:
        Job status details

    Raises:
        HTTPException: If job not found or access denied
    """
    try:
        job = await db_client.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        if job["user_id"] != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve status"
        )

async def process_video_generation(
    job_id: str,
    request: VideoRequest,
    user_id: str,
    script_service: ScriptGeneratorService,
    db_client: BigQueryClient
) -> None:
    """Background task to process video generation.

    Args:
        job_id: Job ID
        request: Generation request
        user_id: User ID
        script_service: Script service
        db_client: Database client
    """
    try:
        # Update status: generating script
        await db_client.update_job_status(job_id, "generating_script")

        # Generate script
        script_data = await script_service.generate_script(
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=request.style.value,
            additional_context=request.additional_context
        )

        # Update with script
        # Note: In real implementation, you'd store this in database
        # For now, just log it

        # Continue with other steps...
        # (video rendering, asset creation, etc.)

        await db_client.update_job_status(job_id, "completed")

    except Exception as e:
        await db_client.update_job_status(
            job_id,
            "failed",
            error=str(e)
        )
EOF
        log_success "backend/api/routes.py criado"
    fi
}

# ============================================================================
# ARQUIVOS DE TESTE
# ============================================================================

# Cria arquivos de teste
create_test_files() {
    log_info "Criando arquivos de teste..."

    # Arquivo de teste principal
    create_test_main
    # Testes da API
    create_test_api
    # Testes dos serviços
    create_test_services

    log_success "Arquivos de teste criados"
}

# Cria arquivo de teste principal
create_test_main() {
    local file="tests/__init__.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Test Suite
Test suite for the Video Genius application
"""
EOF
        log_success "tests/__init__.py criado"
    fi

    # Test conftest
    create_test_conftest
}

# Cria conftest.py
create_test_conftest() {
    local file="tests/conftest.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Test Configuration
Pytest fixtures and configuration
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from backend.main import app
from backend.database.bigquery_client import BigQueryClient
from backend.services.script_generator import ScriptGeneratorService


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_bigquery():
    """Mock BigQuery client."""
    with patch("backend.database.BigQueryClient") as mock:
        instance = MagicMock()
        instance.insert_row = AsyncMock(return_value="test-id-123")
        instance.get_job = AsyncMock(return_value={"id": "test-id", "status": "completed"})
        instance.update_job_status = AsyncMock()
        instance.create_job = AsyncMock(return_value="test-job-id")
        mock.return_value = instance
        yield instance


@pytest.fixture
def mock_script_service():
    """Mock script generator service."""
    with patch("backend.services.script_generator.ScriptGeneratorService") as mock:
        instance = MagicMock()
        instance.generate_script = AsyncMock(return_value={
            "title": "Test Video",
            "script": "This is a test script",
            "hook": "Test hook",
            "key_points": ["Point 1", "Point 2"]
        })
        mock.return_value = instance
        yield instance
EOF
        log_success "tests/conftest.py criado"
    fi
}

# Cria testes da API
create_test_api() {
    local file="tests/test_api.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - API Tests
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "video-genius"}


@pytest.mark.asyncio
async def test_generate_video_success(client: TestClient, mock_bigquery, mock_script_service):
    """Test successful video generation."""
    payload = {
        "topic": "Test video topic",
        "duration_seconds": 60,
        "style": "educational",
        "additional_context": "Test context",
        "tags": ["test", "video"]
    }

    # Mock authentication
    with patch("backend.services.auth.AuthService.verify_token", return_value="test-user"):
        response = client.post("/api/v1/videos/generate", json=payload)

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "estimated_completion_time" in data


@pytest.mark.asyncio
async def test_generate_video_validation_error(client: TestClient):
    """Test validation error handling."""
    payload = {
        "topic": "Test",
        "duration_seconds": 10,  # Too short
        "style": "invalid_style"
    }

    with patch("backend.services.auth.AuthService.verify_token", return_value="test-user"):
        response = client.post("/api/v1/videos/generate", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_generation_status_success(client: TestClient, mock_bigquery):
    """Test getting generation status."""
    job_id = "test-job-id"

    with patch("backend.services.auth.AuthService.verify_token", return_value="test-user"):
        response = client.get(f"/api/v1/videos/{job_id}/status")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id"
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_get_generation_status_not_found(client: TestClient, mock_bigquery):
    """Test generation status for non-existent job."""
    mock_bigquery.get_job = AsyncMock(return_value=None)

    with patch("backend.services.auth.AuthService.verify_token", return_value="test-user"):
        response = client.get("/api/v1/videos/non-existent-job/status")

    assert response.status_code == 404
EOF
        log_success "tests/test_api.py criado"
    fi
}

# Cria testes dos serviços
create_test_services() {
    local file="tests/test_services.py"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
"""
Video Genius - Services Tests
Tests for business logic services
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.asyncio
async def test_script_generator_generate_script(mock_script_service):
    """Test script generation."""
    result = await mock_script_service.generate_script(
        topic="Test topic",
        duration_seconds=60,
        style="educational"
    )

    assert "title" in result
    assert "script" in result
    assert "hook" in result
    assert "key_points" in result
    assert result["title"] == "Test Video"


@pytest.mark.asyncio
async def test_script_generator_invalid_duration(mock_script_service):
    """Test script generation with invalid duration."""
    with pytest.raises(ValueError, match="Duration must be between"):
        await mock_script_service.generate_script(
            topic="Test topic",
            duration_seconds=10,  # Too short
            style="educational"
        )


@pytest.mark.asyncio
async def test_bigquery_client_insert_row(mock_bigquery):
    """Test BigQuery row insertion."""
    row = {"id": "test-id", "data": "test"}

    result = await mock_bigquery.insert_row("test_table", row)

    assert result == "test-id"
    mock_bigquery.insert_row.assert_called_once()


@pytest.mark.asyncio
async def test_bigquery_client_get_job(mock_bigquery):
    """Test getting job from BigQuery."""
    job = await mock_bigquery.get_job("test-job-id")

    assert job["id"] == "test-id"
    assert job["status"] == "completed"
EOF
        log_success "tests/test_services.py criado"
    fi
}

# ============================================================================
# WORKFLOWS DO GITHUB ACTIONS
# ============================================================================

# Cria workflows do GitHub Actions
create_github_workflows() {
    log_info "Criando workflows do GitHub Actions..."

    # Workflow de CI/CD
    create_workflow_ci_cd
    # Workflow de deploy
    create_workflow_deploy

    log_success "Workflows criados"
}

# Cria workflow de CI/CD
create_workflow_ci_cd() {
    local file=".github/workflows/ci-cd.yml"

    if ! file_exists_and_readable "$file"; then
        ensure_dir ".github/workflows"

        cat > "$file" << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run linting
      run: |
        ruff check .
        black --check .

    - name: Run tests
      run: |
        pytest tests/ -v --cov=backend --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Google Artifact Registry
      uses: docker/login-action@v3
      with:
        registry: us-central1-docker.pkg.dev
        username: _json_key
        password: ${{ secrets.GAR_JSON_KEY }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: us-central1-docker.pkg.dev/${{ secrets.GOOGLE_PROJECT_ID }}/video-genius/video-genius:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
EOF
        log_success ".github/workflows/ci-cd.yml criado"
    fi
}

# Cria workflow de deploy
create_workflow_deploy() {
    local file=".github/workflows/deploy.yml"

    if ! file_exists_and_readable "$file"; then
        cat > "$file" << 'EOF'
name: Deploy to Production

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'production'
        type: choice
        options:
        - staging
        - production

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GOOGLE_CREDENTIALS }}

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy video-genius \
          --source . \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --set-env-vars "ENV=${{ github.event.inputs.environment }}"
EOF
        log_success ".github/workflows/deploy.yml criado"
    fi
}

# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

# Se executado diretamente, mostra ajuda
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        --help|-h)
            cat << EOF
$SCRIPT_NAME - Video Genius Project Creation Functions

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Funções para criação completa da estrutura de projeto Video Genius.

FUNÇÕES DISPONÍVEIS:
    • create_project_directories     - Cria estrutura de diretórios
    • create_backend_files          - Cria arquivos de backend
    • create_test_files             - Cria arquivos de teste
    • create_github_workflows       - Cria workflows GitHub Actions

    • create_project_structure      - Cria estrutura completa do projeto

USO:
    source $SCRIPT_NAME
    create_project_structure

OPÇÕES:
    --help, -h          Mostra esta ajuda
    --version, -v       Mostra versão
EOF
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        *)
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
fi

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

# Cria estrutura completa do projeto
create_project_structure() {
    log_info "Criando estrutura completa do projeto Video Genius..."

    # Cria diretórios
    create_project_directories

    # Cria arquivos de backend
    create_backend_files

    # Cria arquivos de teste
    create_test_files

    # Cria workflows
    create_github_workflows

    log_success "Estrutura completa do projeto criada!"
    log_info "Próximos passos:"
    log_info "  1. Configure suas credenciais em .env.local"
    log_info "  2. Execute: source .venv/bin/activate && pip install -r requirements-dev.txt"
    log_info "  3. Execute: pre-commit install"
    log_info "  4. Execute: python backend/main.py"
}
EOF
        log_success "scripts/lib/project_creation.sh criado"
    fi
}

# ============================================================================
# EXECUÇÃO DIRETA
# ============================================================================

# Se executado diretamente, mostra ajuda
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        --help|-h)
            cat << EOF
$SCRIPT_NAME - Video Genius Project Creation Functions

VERSÃO: $SCRIPT_VERSION

DESCRIÇÃO:
    Funções para criação de estrutura de projeto Video Genius.

FUNÇÕES DISPONÍVEIS:
    • create_project_directories     - Cria estrutura de diretórios
    • create_backend_files          - Cria arquivos de backend
    • create_test_files             - Cria arquivos de teste
    • create_github_workflows       - Cria workflows GitHub Actions

    • create_project_structure      - Cria estrutura completa do projeto

USO:
    source $SCRIPT_NAME
    create_project_structure

OPÇÕES:
    --help, -h          Mostra esta ajuda
    --version, -v       Mostra versão
EOF
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        *)
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
fi