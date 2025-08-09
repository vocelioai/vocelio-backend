# schemas/__init__.py
from .voice import *
from .generation import *
from .cloning import *

# schemas/voice.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class VoiceCategory(str, Enum):
    PREMADE = "premade"
    CLONED = "cloned"
    GENERATED = "generated"
    CUSTOM = "custom"

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceAge(str, Enum):
    YOUNG = "young"
    MIDDLE_AGED = "middle_aged"
    ELDERLY = "elderly"

class VoiceSettingsBase(BaseModel):
    stability: float = Field(0.7, ge=0.0, le=1.0, description="Voice stability (0-1)")
    similarity_boost: float = Field(0.8, ge=0.0, le=1.0, description="Voice similarity boost (0-1)")
    style: float = Field(0.2, ge=0.0, le=1.0, description="Voice style enhancement (0-1)")
    use_speaker_boost: bool = Field(True, description="Enable speaker boost")

class VoiceSettingsCreate(VoiceSettingsBase):
    pass

class VoiceSettingsUpdate(BaseModel):
    stability: Optional[float] = Field(None, ge=0.0, le=1.0)
    similarity_boost: Optional[float] = Field(None, ge=0.0, le=1.0)
    style: Optional[float] = Field(None, ge=0.0, le=1.0)
    use_speaker_boost: Optional[bool] = None

class VoiceSettings(VoiceSettingsBase):
    id: int
    voice_id: str
    optimize_streaming_latency: int = 0
    output_format: str = "mp3_44100_128"
    custom_settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VoicePerformanceBase(BaseModel):
    usage_count: int = 0
    total_characters_generated: int = 0
    total_duration_seconds: float = 0.0
    avg_sentiment: float = 0.0
    success_rate: float = 0.0

class VoicePerformance(VoicePerformanceBase):
    id: int
    voice_id: str
    avg_generation_time: float = 0.0
    total_revenue: float = 0.0
    avg_revenue_per_use: float = 0.0
    avg_user_rating: float = 0.0
    total_ratings: int = 0
    last_used_at: Optional[datetime] = None
    last_optimized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VoiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Voice name")
    description: Optional[str] = Field(None, description="Voice description")
    gender: VoiceGender = Field(..., description="Voice gender")
    age: VoiceAge = Field(..., description="Voice age category") 
    accent: Optional[str] = Field(None, max_length=100, description="Voice accent")
    language: str = Field(..., min_length=2, max_length=10, description="Voice language code")
    category: VoiceCategory = Field(..., description="Voice category")
    use_case: Optional[str] = Field(None, max_length=50, description="Primary use case")

class VoiceCreate(VoiceBase):
    quality_score: Optional[float] = Field(0.0, ge=0.0, le=100.0)
    cost_per_char: Optional[float] = Field(0.0, ge=0.0)
    available_for_tiers: Optional[List[str]] = ["free", "starter", "pro", "enterprise"]
    is_public: bool = True

class VoiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    cost_per_char: Optional[float] = Field(None, ge=0.0)
    available_for_tiers: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None

class Voice(VoiceBase):
    voice_id: str
    quality_score: float
    naturalness_score: float
    clarity_score: float
    consistency_score: float
    cost_per_char: float
    available_for_tiers: List[str]
    preview_url: Optional[str] = None
    model_file_path: Optional[str] = None
    is_active: bool
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    settings: Optional[VoiceSettings] = None
    performance: Optional[VoicePerformance] = None

    class Config:
        from_attributes = True

class VoiceListResponse(BaseModel):
    voices: List[Voice]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

class VoiceFilter(BaseModel):
    language: Optional[str] = None
    gender: Optional[VoiceGender] = None
    category: Optional[VoiceCategory] = None
    use_case: Optional[str] = None
    min_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    available_for_tier: Optional[str] = None
    is_active: Optional[bool] = True
    search: Optional[str] = None

# schemas/generation.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationRequestBase(BaseModel):
    voice_id: str = Field(..., description="Voice ID to use for generation")
    text: str = Field(..., min_length=1, max_length=5000, description="Text to generate")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or only whitespace')
        return v.strip()

class GenerationRequestCreate(GenerationRequestBase):
    settings: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    priority: Optional[int] = Field(0, ge=0, le=10)

class GenerationRequest(GenerationRequestBase):
    request_id: str
    settings: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: GenerationStatus
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GenerationResultBase(BaseModel):
    audio_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    character_count: Optional[int] = None
    cost: Optional[float] = None

class GenerationResult(GenerationResultBase):
    result_id: str
    request_id: str
    voice_id: str
    audio_file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    quality_score: Optional[float] = None
    similarity_score: Optional[float] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GenerationResponse(BaseModel):
    request_id: str
    status: GenerationStatus
    result: Optional[GenerationResult] = None
    message: str = "Generation request submitted successfully"

class BatchGenerationRequest(BaseModel):
    voice_id: str
    texts: List[str] = Field(..., min_items=1, max_items=100)
    settings: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class BatchGenerationResponse(BaseModel):
    batch_id: str
    request_ids: List[str]
    total_requests: int
    estimated_completion_time: Optional[float] = None

class VoiceTestRequest(BaseModel):
    voice_id: str
    test_phrases: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class VoiceTestResult(BaseModel):
    voice_id: str
    overall_score: float
    clarity: float
    naturalness: float
    consistency: float
    emotion_range: float
    recommendation: str
    tested_phrases: int
    generation_time: float
    sample_urls: List[str]

class VoiceComparisonRequest(BaseModel):
    voice_ids: List[str] = Field(..., min_items=2, max_items=5)
    sample_text: str = Field(..., min_length=10, max_length=500)
    settings: Optional[Dict[str, Any]] = None

class VoiceComparisonResult(BaseModel):
    comparison_id: str
    sample_text: str
    voices: List[Dict[str, Any]]
    winner_voice_id: str
    comparison_metrics: Dict[str, float]

# schemas/cloning.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class CloneStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CloneRequestBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Clone name")
    description: Optional[str] = Field(None, description="Clone description")

class CloneRequestCreate(CloneRequestBase):
    user_id: str = Field(..., description="User ID requesting the clone")
    processing_options: Optional[Dict[str, Any]] = None

class CloneRequest(CloneRequestBase):
    request_id: str
    clone_id: Optional[str] = None
    user_id: str
    session_id: Optional[str] = None
    original_filename: Optional[str] = None
    uploaded_file_path: Optional[str] = None
    file_format: Optional[str] = None
    processing_options: Optional[Dict[str, Any]] = None
    upload_progress: float = 0.0
    processing_progress: float = 0.0
    created_at: datetime
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VoiceCloneBase(BaseModel):
    name: str
    description: Optional[str] = None

class VoiceCloneCreate(VoiceCloneBase):
    source_user_id: str
    training_epochs: Optional[int] = Field(1000, ge=100, le=5000)
    learning_rate: Optional[float] = Field(0.0001, ge=0.00001, le=0.01)
    batch_size: Optional[int] = Field(32, ge=8, le=128)

class VoiceCloneUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[CloneStatus] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)

class VoiceClone(VoiceCloneBase):
    clone_id: str
    voice_id: Optional[str] = None
    source_user_id: str
    source_file_path: Optional[str] = None
    source_file_size: Optional[int] = None
    source_duration: Optional[float] = None
    training_epochs: int
    learning_rate: float
    batch_size: int
    similarity_score: Optional[float] = None
    quality_score: Optional[float] = None
    training_loss: Optional[float] = None
    validation_loss: Optional[float] = None
    status: CloneStatus
    progress_percentage: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CloneResultBase(BaseModel):
    final_similarity_score: Optional[float] = None
    final_quality_score: Optional[float] = None
    naturalness_score: Optional[float] = None
    consistency_score: Optional[float] = None

class CloneResult(CloneResultBase):
    result_id: str
    clone_id: str
    model_file_path: Optional[str] = None
    sample_audio_path: Optional[str] = None
    total_training_time: Optional[float] = None
    final_loss: Optional[float] = None
    convergence_epoch: Optional[int] = None
    test_samples_count: Optional[int] = None
    avg_test_score: Optional[float] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CloneResponse(BaseModel):
    clone_id: str
    status: CloneStatus
    progress_percentage: float
    message: str
    estimated_completion_time: Optional[float] = None

class CloneListResponse(BaseModel):
    clones: List[VoiceClone]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

# Common response schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    service: str = "voice-lab"
    timestamp: datetime
    version: str = "1.0.0"
    uptime_seconds: Optional[float] = None

class ServiceInfoResponse(BaseModel):
    service: str
    version: str
    status: str
    features: List[str]
    endpoints: Dict[str, str]
    limits: Dict[str, Any]