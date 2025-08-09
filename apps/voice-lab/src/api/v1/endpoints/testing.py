"""
Voice Lab - Voice Testing Endpoints
Handles voice quality testing, A/B testing, and performance analysis
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional, Dict
import asyncio

from services.testing_service import TestingService
from schemas.testing import (
    VoiceTestRequest,
    VoiceTestResult,
    BatchTestRequest,
    BatchTestResult,
    ABTestRequest,
    ABTestResult,
    QualityMetrics
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.post("/test-voice/{voice_id}", response_model=VoiceTestResult)
async def test_voice_quality(
    voice_id: str,
    test_request: VoiceTestRequest,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Test voice quality with comprehensive metrics"""
    try:
        result = await testing_service.test_voice_quality(
            voice_id=voice_id,
            test_phrases=test_request.test_phrases,
            metrics=test_request.metrics,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice test failed: {str(e)}")

@router.post("/batch-test", response_model=BatchTestResult)
async def batch_test_voices(
    batch_request: BatchTestRequest,
    background_tasks: BackgroundTasks,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Test multiple voices with standardized phrases"""
    try:
        batch_id = await testing_service.start_batch_test(
            voice_ids=batch_request.voice_ids,
            test_phrases=batch_request.test_phrases,
            metrics=batch_request.metrics,
            user_id=current_user.id
        )
        
        background_tasks.add_task(
            testing_service.process_ab_test,
            test_id,
            current_user.id
        )
        
        return ABTestResult(
            test_id=test_id,
            status="processing",
            voice_count=len(ab_request.voice_ids),
            scenario_count=len(ab_request.test_scenarios),
            estimated_completion="5-10 minutes"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A/B test failed: {str(e)}")

@router.get("/ab-test/{test_id}/results")
async def get_ab_test_results(
    test_id: str,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get A/B test results and recommendations"""
    results = await testing_service.get_ab_test_results(test_id, current_user.id)
    if not results:
        raise HTTPException(status_code=404, detail="A/B test not found")
    return results

@router.get("/quality-metrics/{voice_id}")
async def get_quality_metrics(
    voice_id: str,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive quality metrics for a voice"""
    metrics = await testing_service.get_voice_quality_metrics(voice_id, current_user.id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Voice not found or no metrics available")
    return metrics

@router.post("/performance-benchmark")
async def benchmark_voice_performance(
    voice_ids: List[str],
    benchmark_type: str = "standard",
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Benchmark voice performance against industry standards"""
    try:
        benchmark_results = await testing_service.benchmark_voices(
            voice_ids=voice_ids,
            benchmark_type=benchmark_type,
            user_id=current_user.id
        )
        return benchmark_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmarking failed: {str(e)}")

@router.get("/test-phrases/recommended")
async def get_recommended_test_phrases(
    use_case: Optional[str] = None,
    language: str = "en",
    difficulty_level: str = "standard",
    testing_service: TestingService = Depends()
):
    """Get recommended test phrases for voice testing"""
    phrases = await testing_service.get_recommended_test_phrases(
        use_case=use_case,
        language=language,
        difficulty_level=difficulty_level
    )
    return {
        "use_case": use_case,
        "language": language,
        "difficulty_level": difficulty_level,
        "phrases": phrases,
        "total_count": len(phrases)
    }

@router.post("/stress-test/{voice_id}")
async def stress_test_voice(
    voice_id: str,
    duration_minutes: int = 5,
    concurrent_requests: int = 3,
    background_tasks: BackgroundTasks,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Perform stress testing on voice performance"""
    if duration_minutes > 30:
        raise HTTPException(status_code=400, detail="Maximum stress test duration is 30 minutes")
    
    try:
        stress_test_id = await testing_service.start_stress_test(
            voice_id=voice_id,
            duration_minutes=duration_minutes,
            concurrent_requests=concurrent_requests,
            user_id=current_user.id
        )
        
        background_tasks.add_task(
            testing_service.process_stress_test,
            stress_test_id,
            current_user.id
        )
        
        return {
            "stress_test_id": stress_test_id,
            "status": "running",
            "duration_minutes": duration_minutes,
            "concurrent_requests": concurrent_requests,
            "estimated_completion": f"{duration_minutes + 2} minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stress test failed: {str(e)}")

@router.get("/reports/quality-trends")
async def get_quality_trends(
    days: int = 30,
    voice_ids: Optional[List[str]] = None,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get quality trends and performance analytics"""
    trends = await testing_service.get_quality_trends(
        user_id=current_user.id,
        days=days,
        voice_ids=voice_ids
    )
    return trends

@router.post("/automated-testing/schedule")
async def schedule_automated_testing(
    voice_ids: List[str],
    schedule_type: str = "daily",  # daily, weekly, monthly
    test_types: List[str] = ["quality", "performance"],
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Schedule automated voice testing"""
    try:
        schedule_id = await testing_service.schedule_automated_testing(
            voice_ids=voice_ids,
            schedule_type=schedule_type,
            test_types=test_types,
            user_id=current_user.id
        )
        
        return {
            "schedule_id": schedule_id,
            "status": "scheduled",
            "voice_count": len(voice_ids),
            "schedule_type": schedule_type,
            "test_types": test_types,
            "next_run": "Next scheduled run in 24 hours"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

@router.get("/testing-history")
async def get_testing_history(
    limit: int = 50,
    test_type: Optional[str] = None,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get user's voice testing history"""
    history = await testing_service.get_testing_history(
        user_id=current_user.id,
        limit=limit,
        test_type=test_type
    )
    return historytask(
            testing_service.process_batch_test,
            batch_id,
            current_user.id
        )
        
        return BatchTestResult(
            batch_id=batch_id,
            status="processing",
            total_voices=len(batch_request.voice_ids),
            total_phrases=len(batch_request.test_phrases),
            estimated_completion="2-3 minutes"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch test failed: {str(e)}")

@router.get("/batch-test/{batch_id}/status")
async def get_batch_test_status(
    batch_id: str,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get batch test status and results"""
    status = await testing_service.get_batch_test_status(batch_id, current_user.id)
    if not status:
        raise HTTPException(status_code=404, detail="Batch test not found")
    return status

@router.post("/ab-test", response_model=ABTestResult)
async def create_ab_test(
    ab_request: ABTestRequest,
    background_tasks: BackgroundTasks,
    testing_service: TestingService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Create A/B test between voices"""
    if len(ab_request.voice_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 voices required for A/B test")
    
    try:
        test_id = await testing_service.create_ab_test(
            voice_ids=ab_request.voice_ids,
            test_scenarios=ab_request.test_scenarios,
            metrics=ab_request.metrics,
            user_id=current_user.id
        )
        
        background_tasks.add_