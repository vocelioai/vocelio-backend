"""
AI Brain Sentiment Service
Advanced sentiment analysis and emotion detection for conversations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from transformers import pipeline
import aioredis

from shared.database.client import DatabaseClient
from shared.utils.logging import get_logger
from src.schemas.sentiment import SentimentAnalysisResponse, EmotionAnalysis
from src.core.config import get_settings

logger = get_logger(__name__)

class SentimentService:
    """Advanced sentiment analysis service with emotion detection"""
    
    def __init__(self, database: DatabaseClient):
        self.database = database
        self.settings = get_settings()
        self.running = False
        
        # Initialize sentiment analyzers
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.emotion_classifier = None
        self.nlp = None
        
        # Initialize models
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """Initialize sentiment and emotion analysis models"""
        try:
            logger.info("🤖 Initializing sentiment analysis models...")
            
            # Load spaCy model for NLP
            self.nlp = spacy.load("en_core_web_sm")
            
            # Load emotion classification model
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # CPU inference
            )
            
            logger.info("✅ Sentiment analysis models initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sentiment models: {e}")
    
    async def analyze_sentiment(
        self,
        text: str,
        context: Optional[str] = None,
        include_emotions: bool = True,
        include_confidence: bool = True
    ) -> SentimentAnalysisResponse:
        """Comprehensive sentiment analysis"""
        try:
            # Basic sentiment analysis with TextBlob
            blob = TextBlob(text)
            textblob_sentiment = blob.sentiment
            
            # VADER sentiment analysis
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # Determine overall sentiment
            overall_sentiment = self._determine_overall_sentiment(
                textblob_sentiment.polarity,
                vader_scores['compound']
            )
            
            # Calculate confidence score
            confidence = self._calculate_sentiment_confidence(
                textblob_sentiment.polarity,
                vader_scores,
                text
            )
            
            # Detailed sentiment scores
            sentiment_scores = {
                "positive": max(0, textblob_sentiment.polarity),
                "negative": max(0, -textblob_sentiment.polarity),
                "neutral": 1 - abs(textblob_sentiment.polarity),
                "compound": vader_scores['compound'],
                "intensity": abs(textblob_sentiment.polarity)
            }
            
            # Emotion analysis if requested
            emotions = None
            if include_emotions and self.emotion_classifier:
                emotions = await self._analyze_emotions(text)
            
            # Generate recommendations
            recommendations = self._generate_sentiment_recommendations(
                overall_sentiment, confidence, emotions, context
            )
            
            return SentimentAnalysisResponse(
                sentiment=overall_sentiment,
                confidence=confidence if include_confidence else 1.0,
                sentiment_scores=sentiment_scores,
                emotions=emotions,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {e}")
            # Return neutral sentiment on failure
            return SentimentAnalysisResponse(
                sentiment="neutral",
                confidence=0.5,
                sentiment_scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                emotions=None,
                recommendations=["Unable to analyze sentiment - using neutral classification"]
            )
    
    async def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text using transformer model"""
        try:
            if not self.emotion_classifier:
                return {}
            
            # Get emotion predictions
            emotion_results = self.emotion_classifier(text)
            
            # Convert to normalized scores
            emotions = {}
            for result in emotion_results:
                emotion = result['label'].lower()
                score = result['score']
                emotions[emotion] = score
            
            # Ensure we have standard emotions
            standard_emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust']
            for emotion in standard_emotions:
                if emotion not in emotions:
                    emotions[emotion] = 0.0
            
            return emotions
            
        except Exception as e:
            logger.error(f"❌ Emotion analysis failed: {e}")
            return {}
    
    def _determine_overall_sentiment(self, textblob_polarity: float, vader_compound: float) -> str:
        """Determine overall sentiment from multiple analyzers"""
        # Weighted average of analyzers
        combined_score = (textblob_polarity * 0.6) + (vader_compound * 0.4)
        
        if combined_score >= 0.1:
            return "positive"
        elif combined_score <= -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_sentiment_confidence(
        self, 
        textblob_polarity: float, 
        vader_scores: Dict[str, float], 
        text: str
    ) -> float:
        """Calculate confidence score for sentiment analysis"""
        try:
            # Base confidence on agreement between analyzers
            agreement = 1 - abs(textblob_polarity - vader_scores['compound'])
            
            # Adjust for text length (longer text generally more reliable)
            length_factor = min(1.0, len(text.split()) / 10)
            
            # Adjust for extremity (more extreme sentiments are often more confident)
            extremity_factor = abs(vader_scores['compound'])
            
            # Combine factors
            confidence = (agreement * 0.5) + (length_factor * 0.3) + (extremity_factor * 0.2)
            
            return min(1.0, max(0.1, confidence))
            
        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.5
    
    def _generate_sentiment_recommendations(
        self,
        sentiment: str,
        confidence: float,
        emotions: Optional[Dict[str, float]],
        context: Optional[str]
    ) -> List[str]:
        """Generate actionable recommendations based on sentiment analysis"""
        recommendations = []
        
        # Sentiment-based recommendations
        if sentiment == "negative" and confidence > 0.7:
            recommendations.append("🔄 Consider adjusting conversation approach - negative sentiment detected")
            recommendations.append("🎯 Switch to empathetic response mode")
            
            if emotions and emotions.get("anger", 0) > 0.5:
                recommendations.append("😤 High anger detected - use de-escalation techniques")
            elif emotions and emotions.get("sadness", 0) > 0.5:
                recommendations.append("😢 Sadness detected - use supportive language")
        
        elif sentiment == "positive" and confidence > 0.8:
            recommendations.append("✅ Positive sentiment - good opportunity to advance conversation")
            recommendations.append("🚀 Consider moving toward closing or next steps")
            
            if emotions and emotions.get("joy", 0) > 0.6:
                recommendations.append("😊 High enthusiasm detected - capitalize on positive mood")
        
        elif sentiment == "neutral":
            if confidence < 0.6:
                recommendations.append("❓ Unclear sentiment - ask clarifying questions")
            else:
                recommendations.append("⚖️ Neutral sentiment - maintain current approach")
        
        # Confidence-based recommendations
        if confidence < 0.5:
            recommendations.append("🔍 Low confidence in sentiment analysis - manual review recommended")
        
        # Context-based recommendations
        if context:
            if "sales" in context.lower():
                if sentiment == "positive":
                    recommendations.append("💼 Sales context + positive sentiment = ideal closing opportunity")
                elif sentiment == "negative":
                    recommendations.append("💼 Sales context + negative sentiment = focus on objection handling")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def start_sentiment_monitoring(self):
        """Start background sentiment monitoring for real-time insights"""
        self.running = True
        logger.info("😊 Starting real-time sentiment monitoring...")
        
        while self.running:
            try:
                await self._monitor_conversation_sentiment()
                await self._generate_sentiment_alerts()
                await self._update_sentiment_trends()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Sentiment monitoring cycle failed: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_conversation_sentiment(self):
        """Monitor ongoing conversations for sentiment changes"""
        try:
            # Get recent conversations that need sentiment monitoring
            recent_conversations = await self.database.fetch_all(
                """
                SELECT id, agent_id, user_id, input_message, generated_response,
                       sentiment_analysis, created_at
                FROM ai_conversations 
                WHERE created_at >= NOW() - INTERVAL '5 minutes'
                AND sentiment_analysis IS NOT NULL
                """
            )
            
            for conv in recent_conversations:
                # Analyze sentiment trend
                sentiment_trend = await self._analyze_sentiment_trend(
                    conv["agent_id"], 
                    conv["user_id"]
                )
                
                # Check for sentiment alerts
                if sentiment_trend.get("alert_needed", False):
                    await self._create_sentiment_alert(conv, sentiment_trend)
            
        except Exception as e:
            logger.error(f"❌ Conversation sentiment monitoring failed: {e}")
    
    async def _analyze_sentiment_trend(self, agent_id: str, user_id: str) -> Dict[str, Any]:
        """Analyze sentiment trend for agent conversations"""
        try:
            # Get recent sentiment data
            sentiment_data = await self.database.fetch_all(
                """
                SELECT sentiment_analysis, created_at
                FROM ai_conversations 
                WHERE agent_id = $1 AND user_id = $2 
                AND created_at >= NOW() - INTERVAL '1 hour'
                AND sentiment_analysis IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 10
                """,
                agent_id, user_id
            )
            
            if len(sentiment_data) < 3:
                return {"alert_needed": False}
            
            # Extract sentiment scores
            sentiment_scores = []
            for data in sentiment_data:
                if data["sentiment_analysis"] and "compound" in data["sentiment_analysis"]:
                    sentiment_scores.append(data["sentiment_analysis"]["compound"])
            
            if len(sentiment_scores) < 3:
                return {"alert_needed": False}
            
            # Calculate trend
            recent_avg = np.mean(sentiment_scores[:3])  # Last 3 conversations
            historical_avg = np.mean(sentiment_scores[3:])  # Previous conversations
            
            sentiment_change = recent_avg - historical_avg
            
            # Determine if alert is needed
            alert_needed = False
            alert_type = None
            
            if sentiment_change < -0.3:  # Significant negative trend
                alert_needed = True
                alert_type = "negative_trend"
            elif recent_avg < -0.5:  # Very negative sentiment
                alert_needed = True
                alert_type = "negative_sentiment"
            elif sentiment_change > 0.3:  # Significant positive trend
                alert_needed = True
                alert_type = "positive_trend"
            
            return {
                "alert_needed": alert_needed,
                "alert_type": alert_type,
                "sentiment_change": sentiment_change,
                "recent_sentiment": recent_avg,
                "historical_sentiment": historical_avg,
                "data_points": len(sentiment_scores)
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment trend analysis failed: {e}")
            return {"alert_needed": False}
    
    async def _create_sentiment_alert(self, conversation: Dict[str, Any], trend_data: Dict[str, Any]):
        """Create sentiment-based alert"""
        try:
            alert_type = trend_data.get("alert_type", "unknown")
            
            # Create alert based on type
            if alert_type == "negative_trend":
                title = "⚠️ Negative Sentiment Trend Detected"
                message = f"Agent {conversation['agent_id']} showing declining sentiment in recent conversations"
                severity = "warning"
            elif alert_type == "negative_sentiment":
                title = "🚨 Very Negative Sentiment Alert"
                message = f"Agent {conversation['agent_id']} receiving very negative responses"
                severity = "critical"
            elif alert_type == "positive_trend":
                title = "📈 Positive Sentiment Improvement"
                message = f"Agent {conversation['agent_id']} showing improved sentiment performance"
                severity = "info"
            else:
                return  # No alert needed
            
            # Store alert in database
            await self.database.execute(
                """
                INSERT INTO ai_alerts 
                (user_id, agent_id, alert_type, severity, title, message, alert_data)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                conversation["user_id"],
                conversation["agent_id"],
                "sentiment",
                severity,
                title,
                message,
                trend_data
            )
            
            logger.info(f"📢 Sentiment alert created: {title}")
            
        except Exception as e:
            logger.error(f"❌ Sentiment alert creation failed: {e}")
    
    async def _generate_sentiment_alerts(self):
        """Generate system-wide sentiment alerts"""
        try:
            # Check for global sentiment patterns
            global_sentiment = await self.database.fetch_one(
                """
                SELECT 
                    AVG(CAST(sentiment_analysis->>'compound' AS FLOAT)) as avg_sentiment,
                    COUNT(*) as conversation_count,
                    COUNT(*) FILTER (WHERE CAST(sentiment_analysis->>'compound' AS FLOAT) < -0.5) as negative_count
                FROM ai_conversations 
                WHERE created_at >= NOW() - INTERVAL '1 hour'
                AND sentiment_analysis IS NOT NULL
                """
            )
            
            if global_sentiment and global_sentiment["conversation_count"] > 10:
                avg_sentiment = global_sentiment["avg_sentiment"]
                negative_rate = global_sentiment["negative_count"] / global_sentiment["conversation_count"]
                
                # Global negative sentiment alert
                if avg_sentiment < -0.2 or negative_rate > 0.3:
                    await self._create_global_sentiment_alert(avg_sentiment, negative_rate)
            
        except Exception as e:
            logger.error(f"❌ Global sentiment alert generation failed: {e}")
    
    async def _create_global_sentiment_alert(self, avg_sentiment: float, negative_rate: float):
        """Create global sentiment alert"""
        try:
            await self.database.execute(
                """
                INSERT INTO ai_alerts 
                (alert_type, severity, title, message, alert_data)
                VALUES ($1, $2, $3, $4, $5)
                """,
                "global_sentiment",
                "warning",
                "🌍 Global Sentiment Alert",
                f"System-wide negative sentiment detected: {negative_rate*100:.1f}% negative conversations",
                {
                    "avg_sentiment": avg_sentiment,
                    "negative_rate": negative_rate,
                    "threshold_exceeded": True
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Global sentiment alert creation failed: {e}")
    
    async def _update_sentiment_trends(self):
        """Update sentiment trends for analytics"""
        try:
            # Calculate hourly sentiment trends
            hourly_trends = await self.database.fetch_all(
                """
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    AVG(CAST(sentiment_analysis->>'compound' AS FLOAT)) as avg_sentiment,
                    COUNT(*) as conversation_count
                FROM ai_conversations 
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                AND sentiment_analysis IS NOT NULL
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour
                """
            )
            
            # Store trends for analytics
            for trend in hourly_trends:
                await self.database.execute(
                    """
                    INSERT INTO ai_system_metrics 
                    (metric_name, metric_category, metric_value, measurement_window, time_bucket)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (metric_name, time_bucket) DO UPDATE SET
                    metric_value = EXCLUDED.metric_value
                    """,
                    "sentiment_score",
                    "quality",
                    trend["avg_sentiment"],
                    "1h",
                    trend["hour"]
                )
            
        except Exception as e:
            logger.error(f"❌ Sentiment trends update failed: {e}")
    
    async def get_sentiment_analytics(
        self, 
        user_id: str, 
        time_range: str = "24h",
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive sentiment analytics"""
        try:
            # Parse time range
            hours = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Build query conditions
            conditions = ["user_id = $1", "created_at >= $2", "sentiment_analysis IS NOT NULL"]
            params = [user_id, start_time]
            
            if agent_id:
                conditions.append("agent_id = $3")
                params.append(agent_id)
            
            # Get sentiment data
            sentiment_data = await self.database.fetch_all(
                f"""
                SELECT 
                    sentiment_analysis,
                    agent_id,
                    created_at,
                    feedback_score
                FROM ai_conversations 
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC
                """,
                *params
            )
            
            if not sentiment_data:
                return {"no_data": True}
            
            # Calculate analytics
            sentiments = []
            emotions_data = []
            agent_sentiment = {}
            
            for data in sentiment_data:
                sentiment_analysis = data["sentiment_analysis"]
                if sentiment_analysis and "compound" in sentiment_analysis:
                    sentiments.append(sentiment_analysis["compound"])
                    
                    # Agent breakdown
                    agent_id = data["agent_id"]
                    if agent_id not in agent_sentiment:
                        agent_sentiment[agent_id] = []
                    agent_sentiment[agent_id].append(sentiment_analysis["compound"])
                    
                    # Emotion data
                    if "emotions" in sentiment_analysis:
                        emotions_data.append(sentiment_analysis["emotions"])
            
            # Calculate summary metrics
            overall_sentiment = np.mean(sentiments) if sentiments else 0
            sentiment_std = np.std(sentiments) if sentiments else 0
            
            # Sentiment distribution
            positive_count = len([s for s in sentiments if s > 0.1])
            negative_count = len([s for s in sentiments if s < -0.1])
            neutral_count = len(sentiments) - positive_count - negative_count
            
            # Agent performance
            agent_metrics = {}
            for agent_id, agent_sentiments in agent_sentiment.items():
                agent_metrics[agent_id] = {
                    "avg_sentiment": np.mean(agent_sentiments),
                    "sentiment_consistency": 1 - np.std(agent_sentiments),
                    "conversation_count": len(agent_sentiments),
                    "positive_rate": len([s for s in agent_sentiments if s > 0.1]) / len(agent_sentiments)
                }
            
            # Emotion analysis
            emotion_summary = {}
            if emotions_data:
                all_emotions = set()
                for emotions in emotions_data:
                    all_emotions.update(emotions.keys())
                
                for emotion in all_emotions:
                    emotion_scores = [e.get(emotion, 0) for e in emotions_data if emotion in e]
                    if emotion_scores:
                        emotion_summary[emotion] = {
                            "average": np.mean(emotion_scores),
                            "frequency": len(emotion_scores) / len(emotions_data)
                        }
            
            return {
                "summary": {
                    "overall_sentiment": round(overall_sentiment, 3),
                    "sentiment_stability": round(1 - sentiment_std, 3),
                    "total_conversations": len(sentiment_data)
                },
                "distribution": {
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                    "positive_rate": round(positive_count / len(sentiments) * 100, 1) if sentiments else 0
                },
                "agent_performance": agent_metrics,
                "emotion_analysis": emotion_summary,
                "trends": await self._calculate_sentiment_trends(user_id, start_time, agent_id),
                "time_period": f"{start_time.isoformat()} to {datetime.utcnow().isoformat()}"
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment analytics failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_sentiment_trends(
        self, 
        user_id: str, 
        start_time: datetime, 
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate sentiment trends over time"""
        try:
            # Build query for hourly sentiment trends
            conditions = ["user_id = $1", "created_at >= $2", "sentiment_analysis IS NOT NULL"]
            params = [user_id, start_time]
            
            if agent_id:
                conditions.append("agent_id = $3")
                params.append(agent_id)
            
            hourly_sentiment = await self.database.fetch_all(
                f"""
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    AVG(CAST(sentiment_analysis->>'compound' AS FLOAT)) as avg_sentiment,
                    COUNT(*) as conversation_count
                FROM ai_conversations 
                WHERE {' AND '.join(conditions)}
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour
                """,
                *params
            )
            
            if len(hourly_sentiment) < 2:
                return {"trend": "insufficient_data"}
            
            # Calculate trend direction
            sentiments = [h["avg_sentiment"] for h in hourly_sentiment]
            if len(sentiments) >= 2:
                trend_slope = np.polyfit(range(len(sentiments)), sentiments, 1)[0]
                
                if trend_slope > 0.02:
                    trend_direction = "improving"
                elif trend_slope < -0.02:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"
            
            # Calculate volatility
            sentiment_volatility = np.std(sentiments) if len(sentiments) > 1 else 0
            
            return {
                "trend": trend_direction,
                "trend_slope": trend_slope if len(sentiments) >= 2 else 0,
                "volatility": round(sentiment_volatility, 3),
                "data_points": len(hourly_sentiment),
                "latest_sentiment": sentiments[-1] if sentiments else 0,
                "sentiment_range": {
                    "min": min(sentiments) if sentiments else 0,
                    "max": max(sentiments) if sentiments else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Sentiment trends calculation failed: {e}")
            return {"trend": "error"}
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours"""
        if time_range.endswith('h'):
            return int(time_range[:-1])
        elif time_range.endswith('d'):
            return int(time_range[:-1]) * 24
        elif time_range.endswith('w'):
            return int(time_range[:-1]) * 24 * 7
        else:
            return 24  # Default to 24 hours
    
    async def batch_analyze_sentiment(
        self, 
        texts: List[str], 
        user_id: str,
        context: Optional[str] = None
    ) -> List[SentimentAnalysisResponse]:
        """Batch sentiment analysis for multiple texts"""
        try:
            results = []
            
            for text in texts:
                sentiment_result = await self.analyze_sentiment(
                    text=text,
                    context=context,
                    include_emotions=True,
                    include_confidence=True
                )
                results.append(sentiment_result)
            
            # Store batch analysis results
            await self._store_batch_sentiment_results(results, user_id, context)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch sentiment analysis failed: {e}")
            return []
    
    async def _store_batch_sentiment_results(
        self, 
        results: List[SentimentAnalysisResponse], 
        user_id: str,
        context: Optional[str]
    ):
        """Store batch sentiment analysis results"""
        try:
            for i, result in enumerate(results):
                await self.database.execute(
                    """
                    INSERT INTO ai_sentiment_analysis 
                    (user_id, text_index, sentiment, confidence, sentiment_scores, emotions, context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_id,
                    i,
                    result.sentiment,
                    result.confidence,
                    result.sentiment_scores,
                    result.emotions,
                    context
                )
                
        except Exception as e:
            logger.error(f"❌ Batch sentiment storage failed: {e}")
    
    async def get_sentiment_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Get actionable sentiment insights"""
        try:
            insights = []
            
            # Get recent sentiment performance
            sentiment_performance = await self.database.fetch_one(
                """
                SELECT 
                    AVG(CAST(sentiment_analysis->>'compound' AS FLOAT)) as avg_sentiment,
                    COUNT(*) as total_conversations,
                    COUNT(*) FILTER (WHERE CAST(sentiment_analysis->>'compound' AS FLOAT) > 0.1) as positive_conversations,
                    COUNT(*) FILTER (WHERE CAST(sentiment_analysis->>'compound' AS FLOAT) < -0.1) as negative_conversations
                FROM ai_conversations 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '24 hours'
                AND sentiment_analysis IS NOT NULL
                """,
                user_id
            )
            
            if sentiment_performance and sentiment_performance["total_conversations"] > 0:
                avg_sentiment = sentiment_performance["avg_sentiment"]
                positive_rate = sentiment_performance["positive_conversations"] / sentiment_performance["total_conversations"]
                negative_rate = sentiment_performance["negative_conversations"] / sentiment_performance["total_conversations"]
                
                # Positive sentiment insight
                if positive_rate > 0.6:
                    insights.append({
                        "type": "positive",
                        "title": "🌟 Excellent Sentiment Performance",
                        "description": f"{positive_rate*100:.1f}% of conversations have positive sentiment",
                        "recommendation": "Continue current conversation strategies",
                        "confidence": 0.9
                    })
                
                # Negative sentiment insight
                elif negative_rate > 0.4:
                    insights.append({
                        "type": "warning",
                        "title": "⚠️ High Negative Sentiment",
                        "description": f"{negative_rate*100:.1f}% of conversations have negative sentiment",
                        "recommendation": "Review conversation scripts and agent training",
                        "confidence": 0.85
                    })
                
                # Agent-specific insights
                agent_insights = await self._get_agent_sentiment_insights(user_id)
                insights.extend(agent_insights)
            
            return insights[:10]  # Return top 10 insights
            
        except Exception as e:
            logger.error(f"❌ Sentiment insights generation failed: {e}")
            return []
    
    async def _get_agent_sentiment_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Get agent-specific sentiment insights"""
        try:
            # Get agent sentiment performance
            agent_performance = await self.database.fetch_all(
                """
                SELECT 
                    agent_id,
                    AVG(CAST(sentiment_analysis->>'compound' AS FLOAT)) as avg_sentiment,
                    COUNT(*) as conversation_count,
                    STDDEV(CAST(sentiment_analysis->>'compound' AS FLOAT)) as sentiment_volatility
                FROM ai_conversations 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
                AND sentiment_analysis IS NOT NULL
                GROUP BY agent_id
                HAVING COUNT(*) >= 10  -- Minimum conversations for statistical significance
                ORDER BY avg_sentiment DESC
                """,
                user_id
            )
            
            insights = []
            
            if agent_performance:
                # Best performing agent
                best_agent = agent_performance[0]
                if best_agent["avg_sentiment"] > 0.3:
                    insights.append({
                        "type": "positive",
                        "title": f"🏆 Top Sentiment Performer: Agent {best_agent['agent_id']}",
                        "description": f"Average sentiment score: {best_agent['avg_sentiment']:.2f}",
                        "recommendation": "Use this agent's approach as a template for others",
                        "confidence": 0.9
                    })
                
                # Worst performing agent
                worst_agent = agent_performance[-1]
                if worst_agent["avg_sentiment"] < -0.1:
                    insights.append({
                        "type": "warning",
                        "title": f"🎯 Improvement Opportunity: Agent {worst_agent['agent_id']}",
                        "description": f"Below-average sentiment score: {worst_agent['avg_sentiment']:.2f}",
                        "recommendation": "Consider retraining or script optimization",
                        "confidence": 0.85
                    })
                
                # Most consistent agent
                consistent_agents = sorted(agent_performance, key=lambda x: x["sentiment_volatility"] or 0)
                if consistent_agents and consistent_agents[0]["sentiment_volatility"] < 0.2:
                    insights.append({
                        "type": "positive",
                        "title": f"⚖️ Most Consistent: Agent {consistent_agents[0]['agent_id']}",
                        "description": "Highly consistent sentiment performance",
                        "recommendation": "Stable performer - good for high-value prospects",
                        "confidence": 0.8
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Agent sentiment insights failed: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Sentiment service health check"""
        try:
            # Test database connection
            await self.database.execute("SELECT 1")
            
            # Test sentiment analysis
            test_result = await self.analyze_sentiment("This is a test message")
            
            return test_result.confidence > 0
            
        except Exception as e:
            logger.error(f"❌ Sentiment service health check failed: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown of sentiment service"""
        self.running = False
        logger.info("🔄 Sentiment service shutting down...")
        
        # Clean up models and resources
        if self.nlp:
            del self.nlp
        if self.emotion_classifier:
            del self.emotion_classifier
        
        logger.info("✅ Sentiment service shutdown complete")