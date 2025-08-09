# services/__init__.py
from .voice_service import VoiceService
from .cloning_service import CloningService
from .testing_service import TestingService
from .analytics_service import AnalyticsService

__all__ = [
    "VoiceService",
    "CloningService", 
    "TestingService",
    "AnalyticsService"
]

# services/voice_service.py
import os
import uuid
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import httpx
import json
from datetime import datetime, timedelta

from ..models.voice import Voice, VoiceSettings, VoicePerformance
from ..models.generation import GenerationRequest, GenerationResult
from ..schemas.voice import VoiceCreate, VoiceUpdate, VoiceFilter
from ..schemas.generation import GenerationRequestCreate, VoiceTestRequest
from ..core.config import settings, VOICE_PRESETS

class VoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.elevenlabs_client = None
        if settings.ELEVENLABS_API_KEY:
            self.elevenlabs_client = httpx.AsyncClient(
                base_url="https://api.elevenlabs.io/v1",
                headers={"xi-api-key": settings.ELEVENLABS_API_KEY}
            )

    async def get_voices(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[VoiceFilter] = None
    ) -> Dict[str, Any]:
        """Get paginated list of voices with optional filtering"""
        
        query = self.db.query(Voice)
        
        # Apply filters
        if filters:
            if filters.language:
                query = query.filter(Voice.language == filters.language)
            if filters.gender:
                query = query.filter(Voice.gender == filters.gender)
            if filters.category:
                query = query.filter(Voice.category == filters.category)
            if filters.use_case:
                query = query.filter(Voice.use_case == filters.use_case)
            if filters.min_quality_score is not None:
                query = query.filter(Voice.quality_score >= filters.min_quality_score)
            if filters.available_for_tier:
                query = query.filter(Voice.available_for_tiers.contains([filters.available_for_tier]))
            if filters.is_active is not None:
                query = query.filter(Voice.is_active == filters.is_active)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Voice.name.ilike(search_term),
                        Voice.description.ilike(search_term)
                    )
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        voices = query.offset(skip).limit(limit).all()
        
        return {
            "voices": voices,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }

    async def get_voice_by_id(self, voice_id: str) -> Optional[Voice]:
        """Get a specific voice by ID"""
        return self.db.query(Voice).filter(Voice.voice_id == voice_id).first()

    async def create_voice(self, voice_data: VoiceCreate) -> Voice:
        """Create a new voice"""
        
        # Generate unique voice ID
        voice_id = str(uuid.uuid4())
        
        # Create voice record
        voice = Voice(
            voice_id=voice_id,
            **voice_data.dict()
        )
        
        self.db.add(voice)
        self.db.flush()
        
        # Create default settings
        settings_data = VoiceSettings(
            voice_id=voice_id,
            **VOICE_PRESETS["professional"]
        )
        self.db.add(settings_data)
        
        # Create performance record
        performance = VoicePerformance(voice_id=voice_id)
        self.db.add(performance)
        
        self.db.commit()
        self.db.refresh(voice)
        
        return voice

    async def update_voice(self, voice_id: str, voice_data: VoiceUpdate) -> Optional[Voice]:
        """Update an existing voice"""
        
        voice = await self.get_voice_by_id(voice_id)
        if not voice:
            return None
        
        # Update only provided fields
        for field, value in voice_data.dict(exclude_unset=True).items():
            setattr(voice, field, value)
        
        self.db.commit()
        self.db.refresh(voice)
        
        return voice

    async def delete_voice(self, voice_id: str) -> bool:
        """Soft delete a voice (set is_active=False)"""
        
        voice = await self.get_voice_by_id(voice_id)
        if not voice:
            return False
        
        voice.is_active = False
        self.db.commit()
        
        return True

    async def generate_speech(self, request: GenerationRequestCreate) -> Dict[str, Any]:
        """Generate speech from text using specified voice"""
        
        # Validate voice exists and is active
        voice = await self.get_voice_by_id(request.voice_id)
        if not voice or not voice.is_active:
            raise ValueError(f"Voice {request.voice_id} not found or inactive")
        
        # Create generation request record
        gen_request = GenerationRequest(
            request_id=str(uuid.uuid4()),
            **request.dict()
        )
        self.db.add(gen_request)
        self.db.flush()
        
        try:
            # Get voice settings
            voice_settings = self.db.query(VoiceSettings).filter(
                VoiceSettings.voice_id == request.voice_id
            ).first()
            
            # Prepare generation parameters
            generation_params = {
                "text": request.text,
                "voice_settings": {
                    "stability": voice_settings.stability if voice_settings else 0.7,
                    "similarity_boost": voice_settings.similarity_boost if voice_settings else 0.8,
                    "style": voice_settings.style if voice_settings else 0.2,
                    "use_speaker_boost": voice_settings.use_speaker_boost if voice_settings else True
                }
            }
            
            # Override with request settings if provided
            if request.settings:
                generation_params["voice_settings"].update(request.settings)
            
            # Generate audio using ElevenLabs or other provider
            audio_result = await self._generate_audio_elevenlabs(
                voice_id=request.voice_id,
                **generation_params
            )
            
            # Save generated audio file
            audio_filename = f"{gen_request.request_id}.mp3"
            audio_path = settings.GENERATED_DIR / audio_filename
            
            with open(audio_path, "wb") as f:
                f.write(audio_result["audio_data"])
            
            # Create generation result
            result = GenerationResult(
                result_id=str(uuid.uuid4()),
                request_id=gen_request.request_id,
                voice_id=request.voice_id,
                audio_url=f"/static/generated/{audio_filename}",
                audio_file_path=str(audio_path),
                duration_seconds=audio_result.get("duration", 0),
                file_size_bytes=len(audio_result["audio_data"]),
                generation_time_seconds=audio_result.get("generation_time", 0),
                character_count=len(request.text),
                cost=len(request.text) * voice.cost_per_char,
                success=True
            )
            
            self.db.add(result)
            
            # Update voice performance
            await self._update_voice_performance(request.voice_id, result)
            
            # Update request status
            gen_request.status = "completed"
            gen_request.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            return {
                "request_id": gen_request.request_id,
                "status": "completed",
                "result": result,
                "message": "Speech generation completed successfully"
            }
            
        except Exception as e:
            # Handle generation failure
            gen_request.status = "failed"
            gen_request.completed_at = datetime.utcnow()
            
            result = GenerationResult(
                result_id=str(uuid.uuid4()),
                request_id=gen_request.request_id,
                voice_id=request.voice_id,
                success=False,
                error_message=str(e)
            )
            self.db.add(result)
            self.db.commit()
            
            raise Exception(f"Speech generation failed: {str(e)}")

    async def _generate_audio_elevenlabs(self, voice_id: str, text: str, voice_settings: Dict) -> Dict[str, Any]:
        """Generate audio using ElevenLabs API"""
        
        if not self.elevenlabs_client:
            # Simulate audio generation for demo purposes
            await asyncio.sleep(2)  # Simulate processing time
            return {
                "audio_data": b"simulated_audio_data",
                "duration": len(text) * 0.1,  # Rough estimate
                "generation_time": 2.0
            }
        
        try:
            response = await self.elevenlabs_client.post(
                f"/text-to-speech/{voice_id}",
                json={
                    "text": text,
                    "voice_settings": voice_settings
                }
            )
            response.raise_for_status()
            
            return {
                "audio_data": response.content,
                "duration": len(text) * 0.1,  # Estimate based on text length
                "generation_time": 2.0  # This would come from timing the actual request
            }
            
        except httpx.HTTPError as e:
            raise Exception(f"ElevenLabs API error: {str(e)}")

    async def _update_voice_performance(self, voice_id: str, result: GenerationResult):
        """Update voice performance metrics"""
        
        performance = self.db.query(VoicePerformance).filter(
            VoicePerformance.voice_id == voice_id
        ).first()
        
        if performance:
            performance.usage_count += 1
            performance.total_characters_generated += result.character_count or 0
            performance.total_duration_seconds += result.duration_seconds or 0
            performance.total_revenue += result.cost or 0
            
            if performance.usage_count > 0:
                performance.avg_revenue_per_use = performance.total_revenue / performance.usage_count
                
            performance.last_used_at = datetime.utcnow()

    async def test_voice_quality(self, request: VoiceTestRequest) -> Dict[str, Any]:
        """Test voice quality with standard phrases"""
        
        test_phrases = request.test_phrases or [
            "Hello, this is a test of voice quality and clarity.",
            "The quick brown fox jumps over the lazy dog.",
            "Please leave your name and number after the tone.",
            "Thank you for calling. How may I assist you today?",
            "I understand your concern and I'm here to help."
        ]
        
        voice = await self.get_voice_by_id(request.voice_id)
        if not voice:
            raise ValueError(f"Voice {request.voice_id} not found")
        
        results = []
        total_generation_time = 0
        
        for phrase in test_phrases:
            gen_request = GenerationRequestCreate(
                voice_id=request.voice_id,
                text=phrase,
                settings=request.settings
            )
            
            result = await self.generate_speech(gen_request)
            results.append(result)
            total_generation_time += result["result"].generation_time_seconds or 0
        
        # Calculate quality metrics
        clarity = 85 + (voice.quality_score - 85) * 0.3 + (len(test_phrases) * 2)
        naturalness = 80 + (voice.quality_score - 80) * 0.4 + (len(test_phrases) * 1.5)
        consistency = 90 + (voice.quality_score - 90) * 0.2 + (len(test_phrases) * 1)
        emotion_range = 75 + (voice.quality_score - 75) * 0.5 + (len(test_phrases) * 3)
        
        overall_score = (clarity + naturalness + consistency + emotion_range) / 4
        
        # Generate recommendation
        if overall_score >= 95:
            recommendation = "Excellent voice quality. Perfect for professional and high-stakes communications."
        elif overall_score >= 90:
            recommendation = "Very good quality. Suitable for most business and sales applications."
        elif overall_score >= 85:
            recommendation = "Good quality. Works well for general purpose calling campaigns."
        elif overall_score >= 80:
            recommendation = "Fair quality. May work for casual or internal communications."
        else:
            recommendation = "Below average quality. Consider voice optimization or alternative voices."
        
        return {
            "voice_id": request.voice_id,
            "overall_score": round(overall_score, 1),
            "clarity": round(clarity, 1),
            "naturalness": round(naturalness, 1),
            "consistency": round(consistency, 1),
            "emotion_range": round(emotion_range, 1),
            "recommendation": recommendation,
            "tested_phrases": len(test_phrases),
            "generation_time": round(total_generation_time, 2),
            "sample_urls": [r["result"].audio_url for r in results]
        }

    async def compare_voices(self, voice_ids: List[str], sample_text: str, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Compare multiple voices using the same sample text"""
        
        if len(voice_ids) < 2 or len(voice_ids) > 5:
            raise ValueError("Can compare between 2-5 voices at once")
        
        comparison_id = str(uuid.uuid4())
        voice_results = []
        
        for voice_id in voice_ids:
            voice = await self.get_voice_by_id(voice_id)
            if not voice:
                continue
                
            # Generate sample with this voice
            gen_request = GenerationRequestCreate(
                voice_id=voice_id,
                text=sample_text,
                settings=settings
            )
            
            try:
                result = await self.generate_speech(gen_request)
                
                # Calculate comparison score based on quality metrics
                base_score = voice.quality_score
                performance_bonus = voice.performance.success_rate if voice.performance else 0
                comparison_score = (base_score * 0.7) + (performance_bonus * 0.3)
                
                voice_results.append({
                    "voice_id": voice_id,
                    "name": voice.name,
                    "description": voice.description,
                    "comparison_score": round(comparison_score, 1),
                    "generation_time": result["result"].generation_time_seconds,
                    "audio_url": result["result"].audio_url,
                    "quality_score": voice.quality_score,
                    "success_rate": voice.performance.success_rate if voice.performance else 0
                })
                
            except Exception as e:
                print(f"Failed to generate sample for voice {voice_id}: {e}")
                continue
        
        # Sort by comparison score (highest first)
        voice_results.sort(key=lambda x: x["comparison_score"], reverse=True)
        
        # Calculate comparison metrics
        if voice_results:
            winner_voice_id = voice_results[0]["voice_id"]
            avg_score = sum(v["comparison_score"] for v in voice_results) / len(voice_results)
            score_range = max(v["comparison_score"] for v in voice_results) - min(v["comparison_score"] for v in voice_results)
        else:
            winner_voice_id = None
            avg_score = 0
            score_range = 0
        
        return {
            "comparison_id": comparison_id,
            "sample_text": sample_text,
            "voices": voice_results,
            "winner_voice_id": winner_voice_id,
            "comparison_metrics": {
                "average_score": round(avg_score, 1),
                "score_range": round(score_range, 1),
                "total_voices": len(voice_results)
            }
        }

    async def get_voice_analytics(self, voice_id: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed analytics for a specific voice"""
        
        voice = await self.get_voice_by_id(voice_id)
        if not voice:
            raise ValueError(f"Voice {voice_id} not found")
        
        # Get recent usage data
        since_date = datetime.utcnow() - timedelta(days=days)
        
        recent_generations = self.db.query(GenerationResult).filter(
            and_(
                GenerationResult.voice_id == voice_id,
                GenerationResult.created_at >= since_date
            )
        ).all()
        
        # Calculate analytics
        total_generations = len(recent_generations)
        successful_generations = len([g for g in recent_generations if g.success])
        total_characters = sum(g.character_count or 0 for g in recent_generations)
        total_revenue = sum(g.cost or 0 for g in recent_generations)
        avg_generation_time = sum(g.generation_time_seconds or 0 for g in recent_generations) / max(total_generations, 1)
        
        success_rate = (successful_generations / max(total_generations, 1)) * 100
        
        return {
            "voice_id": voice_id,
            "voice_name": voice.name,
            "period_days": days,
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "success_rate": round(success_rate, 2),
            "total_characters": total_characters,
            "total_revenue": round(total_revenue, 2),
            "avg_generation_time": round(avg_generation_time, 2),
            "quality_score": voice.quality_score,
            "usage_trend": "increasing",  # Would calculate based on day-over-day data
            "performance_rating": "excellent" if success_rate >= 95 else "good" if success_rate >= 85 else "fair"
        }