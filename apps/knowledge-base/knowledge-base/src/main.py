"""
Knowledge Base Service - Vocelio AI Call Center
Intelligent knowledge management with document processing, search, and AI-powered insights
"""

# Add parent directories to Python path for Docker compatibility
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import re
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Knowledge Base Models
class DocumentType(str, Enum):
    FAQ = "faq"
    MANUAL = "manual"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TRAINING = "training"
    PRODUCT_INFO = "product_info"
    TROUBLESHOOTING = "troubleshooting"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    SCRIPT = "script"
    TEMPLATE = "template"
    GLOSSARY = "glossary"
    CHANGELOG = "changelog"
    ANNOUNCEMENT = "announcement"
    ARTICLE = "article"

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    NEEDS_REVIEW = "needs_review"
    EXPIRED = "expired"

class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"

class ContentFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    DOCX = "docx"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"

class SearchType(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    FUZZY = "fuzzy"
    EXACT = "exact"
    PHRASE = "phrase"

class DocumentMetadata(BaseModel):
    author: str
    department: str
    tags: List[str] = []
    keywords: List[str] = []
    language: str = "en-US"
    region: str = "global"
    version: str = "1.0.0"
    review_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    related_documents: List[str] = []
    external_links: List[str] = []
    attachments: List[str] = []

class ContentAnalysis(BaseModel):
    word_count: int = 0
    reading_time_minutes: float = 0.0
    complexity_score: float = 0.0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    topic_categories: List[str] = []
    extracted_entities: Dict[str, List[str]] = {}
    key_phrases: List[str] = []
    summary: str = ""

class SearchFilter(BaseModel):
    document_types: Optional[List[DocumentType]] = None
    access_levels: Optional[List[AccessLevel]] = None
    departments: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    languages: Optional[List[str]] = None
    authors: Optional[List[str]] = None

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    summary: str
    document_type: DocumentType
    status: DocumentStatus = DocumentStatus.DRAFT
    access_level: AccessLevel = AccessLevel.INTERNAL
    content_format: ContentFormat = ContentFormat.TEXT
    
    # Metadata
    metadata: DocumentMetadata
    analysis: Optional[ContentAnalysis] = None
    
    # Organization
    category: str
    subcategory: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)  # 1-10 priority scale
    
    # Versioning
    version_history: List[str] = []
    parent_document_id: Optional[str] = None
    child_documents: List[str] = []
    
    # Usage tracking
    view_count: int = 0
    search_hits: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    last_accessed: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # File information
    file_size_bytes: Optional[int] = None
    file_path: Optional[str] = None
    original_filename: Optional[str] = None

class SearchResult(BaseModel):
    document_id: str
    title: str
    summary: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    matched_content: str
    highlighted_text: str
    document_type: DocumentType
    category: str
    last_updated: datetime
    view_count: int
    helpful_votes: int

class SearchQuery(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_text: str
    search_type: SearchType = SearchType.SEMANTIC
    filters: Optional[SearchFilter] = None
    user_id: str
    session_id: Optional[str] = None
    
    # Results
    results_count: int = 0
    results: List[SearchResult] = []
    processing_time_ms: float = 0.0
    
    # Analytics
    clicked_results: List[str] = []
    helpful_results: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class KnowledgeCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    parent_category_id: Optional[str] = None
    subcategories: List[str] = []
    document_count: int = 0
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

class KnowledgeTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    document_type: DocumentType
    template_content: str
    required_fields: List[str] = []
    optional_fields: List[str] = []
    usage_count: int = 0
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class UserInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    document_id: str
    interaction_type: str  # "view", "search", "vote", "comment", "share"
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class KnowledgeAnalytics(BaseModel):
    total_documents: int
    published_documents: int
    total_searches: int
    successful_searches: int
    average_search_time_ms: float
    most_searched_terms: List[Dict[str, Any]]
    popular_documents: List[Dict[str, Any]]
    content_gaps: List[str]
    user_satisfaction: float
    
    # Time-based metrics
    daily_activity: List[Dict[str, Any]] = []
    category_distribution: Dict[str, int] = {}
    access_patterns: Dict[str, int] = {}
    
    # Content quality metrics
    average_helpfulness: float
    outdated_content_count: int
    content_without_review: int

# Sample data
SAMPLE_DOCUMENTS = [
    Document(
        title="Customer Service Best Practices",
        content="Customer service excellence requires active listening, empathy, and solution-focused communication. Always greet customers warmly, acknowledge their concerns, and work towards resolution. Key principles include: 1) Listen actively to understand the customer's issue completely. 2) Show empathy and understanding for their situation. 3) Ask clarifying questions to gather all necessary information. 4) Provide clear, step-by-step solutions. 5) Follow up to ensure satisfaction. Remember to maintain a positive tone throughout the interaction and never take customer frustration personally.",
        summary="Comprehensive guide covering essential customer service principles and best practices for effective customer interactions.",
        document_type=DocumentType.TRAINING,
        status=DocumentStatus.PUBLISHED,
        access_level=AccessLevel.INTERNAL,
        metadata=DocumentMetadata(
            author="Sarah Johnson",
            department="Customer Success",
            tags=["customer-service", "training", "best-practices"],
            keywords=["empathy", "communication", "resolution", "satisfaction"],
            version="2.1.0"
        ),
        analysis=ContentAnalysis(
            word_count=157,
            reading_time_minutes=1.2,
            complexity_score=6.5,
            readability_score=8.2,
            sentiment_score=0.7,
            topic_categories=["customer_service", "communication"],
            key_phrases=["active listening", "customer satisfaction", "problem resolution"],
            summary="Guide for effective customer service delivery with focus on empathy and solution-oriented approach."
        ),
        category="Training",
        subcategory="Customer Service",
        priority=9,
        view_count=342,
        search_hits=89,
        helpful_votes=67,
        unhelpful_votes=3,
        published_at=datetime.now() - timedelta(days=30)
    ),
    Document(
        title="Product Return Policy",
        content="Our return policy allows customers to return products within 30 days of purchase for a full refund. Items must be in original condition with all packaging and accessories. Digital products and personalized items are non-returnable. To process a return: 1) Customer initiates return request through our portal or by calling customer service. 2) We provide a return authorization number and prepaid shipping label. 3) Customer ships the item back within 7 days. 4) We inspect the item upon receipt. 5) Refund is processed within 3-5 business days. Exceptions may apply for bulk orders or special promotions.",
        summary="Complete return policy guidelines including timeframes, conditions, and step-by-step return process.",
        document_type=DocumentType.POLICY,
        status=DocumentStatus.PUBLISHED,
        access_level=AccessLevel.PUBLIC,
        metadata=DocumentMetadata(
            author="Legal Team",
            department="Legal",
            tags=["returns", "policy", "refunds"],
            keywords=["30 days", "original condition", "refund", "authorization"],
            version="1.5.0",
            review_date=datetime.now() + timedelta(days=90)
        ),
        analysis=ContentAnalysis(
            word_count=143,
            reading_time_minutes=1.1,
            complexity_score=7.0,
            readability_score=7.8,
            sentiment_score=0.1,
            topic_categories=["policy", "returns", "customer_service"],
            key_phrases=["30 days", "full refund", "original condition"],
            summary="Policy outlining return procedures and requirements for customer refunds."
        ),
        category="Policies",
        subcategory="Returns",
        priority=8,
        view_count=128,
        search_hits=45,
        helpful_votes=89,
        unhelpful_votes=12,
        published_at=datetime.now() - timedelta(days=15)
    ),
    Document(
        title="Technical Troubleshooting Guide",
        content="Common technical issues and their solutions: 1) Login Problems: Clear browser cache, check credentials, verify account status. If issue persists, reset password or contact IT support. 2) Slow Performance: Check internet connection, close unnecessary applications, restart device. For persistent issues, run system diagnostics. 3) Audio Issues: Check microphone and speaker settings, test with different browsers, ensure proper permissions. Update audio drivers if needed. 4) Connection Drops: Verify network stability, check firewall settings, try different network if available. 5) Feature Not Working: Refresh page, check browser compatibility, disable browser extensions. Always document steps taken before escalating to technical support.",
        summary="Comprehensive troubleshooting guide for common technical issues with step-by-step resolution steps.",
        document_type=DocumentType.TROUBLESHOOTING,
        status=DocumentStatus.PUBLISHED,
        access_level=AccessLevel.INTERNAL,
        metadata=DocumentMetadata(
            author="IT Support Team",
            department="IT",
            tags=["troubleshooting", "technical", "support", "solutions"],
            keywords=["login", "performance", "audio", "connection", "browser"],
            version="3.2.0"
        ),
        analysis=ContentAnalysis(
            word_count=168,
            reading_time_minutes=1.3,
            complexity_score=8.1,
            readability_score=7.5,
            sentiment_score=0.2,
            topic_categories=["technical_support", "troubleshooting"],
            key_phrases=["technical issues", "step-by-step", "diagnostics"],
            summary="Technical guide providing solutions for common system and connectivity problems."
        ),
        category="Technical Support",
        subcategory="Troubleshooting",
        priority=9,
        view_count=256,
        search_hits=78,
        helpful_votes=134,
        unhelpful_votes=8,
        published_at=datetime.now() - timedelta(days=7)
    )
]

SAMPLE_CATEGORIES = [
    KnowledgeCategory(
        name="Customer Service",
        description="Customer service guidelines, scripts, and best practices",
        document_count=15,
        icon="customer-service",
        color="#4F46E5",
        sort_order=1
    ),
    KnowledgeCategory(
        name="Technical Support",
        description="Technical troubleshooting guides and IT support documentation",
        document_count=23,
        icon="technical",
        color="#059669",
        sort_order=2
    ),
    KnowledgeCategory(
        name="Policies",
        description="Company policies, procedures, and compliance documentation",
        document_count=12,
        icon="policy",
        color="#DC2626",
        sort_order=3
    ),
    KnowledgeCategory(
        name="Training",
        description="Training materials and educational resources",
        document_count=18,
        icon="training",
        color="#7C2D12",
        sort_order=4
    )
]

# Global storage
documents: List[Document] = []
categories: List[KnowledgeCategory] = []
templates: List[KnowledgeTemplate] = []
search_queries: List[SearchQuery] = []
user_interactions: List[UserInteraction] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global documents, categories
    
    documents.extend(SAMPLE_DOCUMENTS)
    categories.extend(SAMPLE_CATEGORIES)
    
    logger.info("Sample knowledge base data initialized successfully")

async def analyze_document_content(content: str) -> ContentAnalysis:
    """Analyze document content for insights"""
    # Mock content analysis - in production, this would use NLP/ML models
    words = len(content.split())
    reading_time = words / 200  # Average reading speed
    
    # Simple sentiment analysis (mock)
    positive_words = ["good", "excellent", "great", "effective", "successful", "helpful"]
    negative_words = ["bad", "poor", "difficult", "problem", "issue", "error"]
    
    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    sentiment = (positive_count - negative_count) / max(1, positive_count + negative_count)
    
    # Extract key phrases (simple implementation)
    sentences = content.split('.')
    key_phrases = []
    for sentence in sentences[:3]:
        if len(sentence.strip()) > 20:
            key_phrases.append(sentence.strip()[:50] + "...")
    
    return ContentAnalysis(
        word_count=words,
        reading_time_minutes=round(reading_time, 1),
        complexity_score=min(10, max(1, words / 20)),
        readability_score=8.5 - (words / 100),
        sentiment_score=sentiment,
        topic_categories=["general"],
        key_phrases=key_phrases[:3],
        summary=content[:200] + "..." if len(content) > 200 else content
    )

async def perform_search(query: str, search_type: SearchType, filters: Optional[SearchFilter] = None) -> List[SearchResult]:
    """Perform search across knowledge base"""
    
    results = []
    query_lower = query.lower()
    
    # Filter documents based on criteria
    filtered_docs = documents.copy()
    
    if filters:
        if filters.document_types:
            filtered_docs = [d for d in filtered_docs if d.document_type in filters.document_types]
        
        if filters.access_levels:
            filtered_docs = [d for d in filtered_docs if d.access_level in filters.access_levels]
        
        if filters.departments:
            filtered_docs = [d for d in filtered_docs if d.metadata.department in filters.departments]
        
        if filters.tags:
            filtered_docs = [d for d in filtered_docs if any(tag in d.metadata.tags for tag in filters.tags)]
        
        if filters.date_range_start:
            filtered_docs = [d for d in filtered_docs if d.updated_at >= filters.date_range_start]
        
        if filters.date_range_end:
            filtered_docs = [d for d in filtered_docs if d.updated_at <= filters.date_range_end]
    
    # Perform search based on type
    for doc in filtered_docs:
        relevance_score = 0.0
        matched_content = ""
        
        # Search in title, content, and summary
        searchable_text = f"{doc.title} {doc.content} {doc.summary}".lower()
        
        if search_type == SearchType.EXACT:
            if query_lower in searchable_text:
                relevance_score = 1.0
                matched_content = query
        
        elif search_type == SearchType.KEYWORD:
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in searchable_text)
            relevance_score = matches / len(query_words) if query_words else 0
            matched_content = " ".join([word for word in query_words if word in searchable_text])
        
        elif search_type == SearchType.PHRASE:
            if query_lower in searchable_text:
                relevance_score = 0.9
                matched_content = query
        
        elif search_type == SearchType.SEMANTIC or search_type == SearchType.FUZZY:
            # Mock semantic/fuzzy search
            query_words = query_lower.split()
            score = 0
            for word in query_words:
                if word in searchable_text:
                    score += 0.3
                # Simple fuzzy matching
                for doc_word in searchable_text.split():
                    if word in doc_word or doc_word in word:
                        score += 0.1
            
            relevance_score = min(1.0, score / len(query_words) if query_words else 0)
            matched_content = query
        
        if relevance_score > 0.1:  # Minimum relevance threshold
            # Find context around matches
            context_start = max(0, doc.content.lower().find(query_lower) - 50)
            context_end = min(len(doc.content), context_start + 200)
            highlighted_text = doc.content[context_start:context_end]
            
            # Highlight query terms
            for word in query_lower.split():
                highlighted_text = re.sub(
                    f"({re.escape(word)})", 
                    r"<mark>\1</mark>", 
                    highlighted_text, 
                    flags=re.IGNORECASE
                )
            
            results.append(SearchResult(
                document_id=doc.id,
                title=doc.title,
                summary=doc.summary,
                relevance_score=relevance_score,
                matched_content=matched_content,
                highlighted_text=highlighted_text,
                document_type=doc.document_type,
                category=doc.category,
                last_updated=doc.updated_at,
                view_count=doc.view_count,
                helpful_votes=doc.helpful_votes
            ))
            
            # Update search hit count
            doc.search_hits += 1
    
    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return results[:20]  # Return top 20 results

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Knowledge Base Service",
    description="Intelligent knowledge management with document processing, search, and AI-powered insights for Vocelio AI Call Center",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "knowledge-base",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Document Management Endpoints
@app.get("/documents", response_model=List[Document])
async def get_documents(
    document_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    access_level: Optional[AccessLevel] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    sort_by: str = "updated_at",  # "updated_at", "created_at", "title", "views", "votes"
    sort_order: str = "desc",  # "asc", "desc"
    limit: int = 50,
    offset: int = 0
):
    """Get documents with filtering and sorting options"""
    
    filtered_docs = documents.copy()
    
    # Apply filters
    if document_type:
        filtered_docs = [d for d in filtered_docs if d.document_type == document_type]
    
    if status:
        filtered_docs = [d for d in filtered_docs if d.status == status]
    
    if access_level:
        filtered_docs = [d for d in filtered_docs if d.access_level == access_level]
    
    if category:
        filtered_docs = [d for d in filtered_docs if d.category.lower() == category.lower()]
    
    if author:
        filtered_docs = [d for d in filtered_docs if author.lower() in d.metadata.author.lower()]
    
    if tag:
        filtered_docs = [d for d in filtered_docs if tag.lower() in [t.lower() for t in d.metadata.tags]]
    
    # Apply sorting
    reverse = sort_order == "desc"
    
    if sort_by == "title":
        filtered_docs.sort(key=lambda x: x.title.lower(), reverse=reverse)
    elif sort_by == "created_at":
        filtered_docs.sort(key=lambda x: x.created_at, reverse=reverse)
    elif sort_by == "views":
        filtered_docs.sort(key=lambda x: x.view_count, reverse=reverse)
    elif sort_by == "votes":
        filtered_docs.sort(key=lambda x: x.helpful_votes, reverse=reverse)
    else:  # updated_at
        filtered_docs.sort(key=lambda x: x.updated_at, reverse=reverse)
    
    # Apply pagination
    return filtered_docs[offset:offset + limit]

@app.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str, user_id: Optional[str] = None):
    """Get a specific document by ID"""
    document = next((d for d in documents if d.id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Track view
    document.view_count += 1
    document.last_accessed = datetime.now()
    
    # Log user interaction
    if user_id:
        interaction = UserInteraction(
            user_id=user_id,
            document_id=document_id,
            interaction_type="view"
        )
        user_interactions.append(interaction)
    
    return document

@app.post("/documents", response_model=Document)
async def create_document(
    title: str = Form(...),
    content: str = Form(...),
    summary: str = Form(...),
    document_type: DocumentType = Form(...),
    category: str = Form(...),
    author: str = Form(...),
    department: str = Form(...),
    access_level: AccessLevel = AccessLevel.INTERNAL,
    tags: str = Form(""),  # Comma-separated tags
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new document"""
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    # Create document
    doc = Document(
        title=title,
        content=content,
        summary=summary,
        document_type=document_type,
        access_level=access_level,
        category=category,
        metadata=DocumentMetadata(
            author=author,
            department=department,
            tags=tag_list
        )
    )
    
    documents.append(doc)
    
    # Analyze content in background
    background_tasks.add_task(analyze_and_update_document, doc.id)
    
    logger.info(f"Created new document: {title}")
    return doc

async def analyze_and_update_document(document_id: str):
    """Analyze document content and update analysis"""
    document = next((d for d in documents if d.id == document_id), None)
    if document:
        document.analysis = await analyze_document_content(document.content)
        document.updated_at = datetime.now()

@app.put("/documents/{document_id}", response_model=Document)
async def update_document(
    document_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    status: Optional[DocumentStatus] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Update an existing document"""
    document = next((d for d in documents if d.id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update fields
    if title:
        document.title = title
    if content:
        document.content = content
        # Re-analyze content if changed
        background_tasks.add_task(analyze_and_update_document, document_id)
    if summary:
        document.summary = summary
    if status:
        document.status = status
        if status == DocumentStatus.PUBLISHED:
            document.published_at = datetime.now()
    
    document.updated_at = datetime.now()
    
    logger.info(f"Updated document: {document.title}")
    return document

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    global documents
    document = next((d for d in documents if d.id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents = [d for d in documents if d.id != document_id]
    logger.info(f"Deleted document: {document.title}")
    return {"message": "Document deleted successfully"}

# Search Endpoints
@app.post("/search", response_model=SearchQuery)
async def search_knowledge_base(
    query: str,
    search_type: SearchType = SearchType.SEMANTIC,
    user_id: str = "anonymous",
    filters: Optional[SearchFilter] = None,
    limit: int = 20
):
    """Search the knowledge base"""
    
    start_time = datetime.now()
    
    # Perform search
    results = await perform_search(query, search_type, filters)
    
    # Limit results
    results = results[:limit]
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # Create search query record
    search_query = SearchQuery(
        query_text=query,
        search_type=search_type,
        filters=filters,
        user_id=user_id,
        results_count=len(results),
        results=results,
        processing_time_ms=processing_time,
        completed_at=datetime.now()
    )
    
    search_queries.append(search_query)
    
    # Log search interaction
    interaction = UserInteraction(
        user_id=user_id,
        document_id="search",
        interaction_type="search",
        details={"query": query, "results_count": len(results)}
    )
    user_interactions.append(interaction)
    
    logger.info(f"Search performed: '{query}' - {len(results)} results")
    return search_query

@app.get("/search/suggestions")
async def get_search_suggestions(query: str, limit: int = 10):
    """Get search suggestions based on query"""
    
    query_lower = query.lower()
    suggestions = []
    
    # Get suggestions from document titles and content
    for doc in documents:
        if query_lower in doc.title.lower():
            suggestions.append({
                "text": doc.title,
                "type": "title",
                "document_id": doc.id
            })
        
        # Extract phrases containing query
        words = doc.content.lower().split()
        for i, word in enumerate(words):
            if query_lower in word:
                # Get surrounding context
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                phrase = " ".join(words[start:end])
                if len(phrase) > 10:
                    suggestions.append({
                        "text": phrase,
                        "type": "phrase",
                        "document_id": doc.id
                    })
    
    # Remove duplicates and limit
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion["text"] not in seen and len(unique_suggestions) < limit:
            seen.add(suggestion["text"])
            unique_suggestions.append(suggestion)
    
    return {"suggestions": unique_suggestions}

@app.get("/search/history")
async def get_search_history(user_id: str, limit: int = 20):
    """Get search history for a user"""
    user_searches = [s for s in search_queries if s.user_id == user_id]
    user_searches.sort(key=lambda x: x.created_at, reverse=True)
    return {"searches": user_searches[:limit]}

# Categories Endpoints
@app.get("/categories", response_model=List[KnowledgeCategory])
async def get_categories():
    """Get all knowledge base categories"""
    # Update document counts
    for category in categories:
        category.document_count = len([d for d in documents if d.category == category.name])
    
    categories.sort(key=lambda x: x.sort_order)
    return categories

@app.post("/categories", response_model=KnowledgeCategory)
async def create_category(category_data: KnowledgeCategory):
    """Create a new category"""
    categories.append(category_data)
    logger.info(f"Created new category: {category_data.name}")
    return category_data

@app.get("/categories/{category_id}/documents", response_model=List[Document])
async def get_category_documents(category_id: str, limit: int = 50):
    """Get documents in a specific category"""
    category = next((c for c in categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category_docs = [d for d in documents if d.category == category.name]
    category_docs.sort(key=lambda x: x.updated_at, reverse=True)
    return category_docs[:limit]

# Document Voting Endpoints
@app.post("/documents/{document_id}/vote")
async def vote_document(
    document_id: str,
    helpful: bool,
    user_id: str
):
    """Vote on document helpfulness"""
    document = next((d for d in documents if d.id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if helpful:
        document.helpful_votes += 1
    else:
        document.unhelpful_votes += 1
    
    # Log interaction
    interaction = UserInteraction(
        user_id=user_id,
        document_id=document_id,
        interaction_type="vote",
        details={"helpful": helpful}
    )
    user_interactions.append(interaction)
    
    return {
        "message": "Vote recorded",
        "helpful_votes": document.helpful_votes,
        "unhelpful_votes": document.unhelpful_votes
    }

# Analytics Endpoints
@app.get("/analytics", response_model=KnowledgeAnalytics)
async def get_knowledge_analytics():
    """Get knowledge base analytics"""
    
    total_docs = len(documents)
    published_docs = len([d for d in documents if d.status == DocumentStatus.PUBLISHED])
    total_searches = len(search_queries)
    successful_searches = len([s for s in search_queries if s.results_count > 0])
    
    # Calculate average search time
    search_times = [s.processing_time_ms for s in search_queries if s.processing_time_ms > 0]
    avg_search_time = sum(search_times) / len(search_times) if search_times else 0
    
    # Most searched terms
    query_counts = {}
    for search in search_queries:
        query = search.query_text.lower()
        query_counts[query] = query_counts.get(query, 0) + 1
    
    most_searched = [
        {"term": term, "count": count, "percentage": round(count / total_searches * 100, 1)}
        for term, count in sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    # Popular documents
    popular_docs = sorted(documents, key=lambda x: x.view_count + x.helpful_votes, reverse=True)[:10]
    popular_list = [
        {
            "id": doc.id,
            "title": doc.title,
            "views": doc.view_count,
            "helpful_votes": doc.helpful_votes,
            "category": doc.category
        }
        for doc in popular_docs
    ]
    
    # Category distribution
    category_dist = {}
    for doc in documents:
        category_dist[doc.category] = category_dist.get(doc.category, 0) + 1
    
    # Content gaps (mock analysis)
    content_gaps = [
        "Advanced troubleshooting procedures",
        "Integration setup guides",
        "Performance optimization tips",
        "Security best practices"
    ]
    
    # User satisfaction (based on helpful votes)
    total_votes = sum(d.helpful_votes + d.unhelpful_votes for d in documents)
    helpful_votes = sum(d.helpful_votes for d in documents)
    satisfaction = (helpful_votes / total_votes * 100) if total_votes > 0 else 0
    
    # Daily activity (mock data)
    daily_activity = [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "searches": max(0, 25 - i * 2 + (i % 3) * 5),
            "documents_viewed": max(0, 40 - i * 3 + (i % 4) * 8),
            "new_documents": max(0, 2 - i // 3)
        }
        for i in range(7, 0, -1)
    ]
    
    return KnowledgeAnalytics(
        total_documents=total_docs,
        published_documents=published_docs,
        total_searches=total_searches,
        successful_searches=successful_searches,
        average_search_time_ms=avg_search_time,
        most_searched_terms=most_searched,
        popular_documents=popular_list,
        content_gaps=content_gaps,
        user_satisfaction=round(satisfaction, 1),
        daily_activity=daily_activity,
        category_distribution=category_dist,
        access_patterns={"internal": 65, "public": 30, "restricted": 5},
        average_helpfulness=round(helpful_votes / total_docs, 1) if total_docs > 0 else 0,
        outdated_content_count=len([d for d in documents if d.metadata.review_date and d.metadata.review_date < datetime.now()]),
        content_without_review=len([d for d in documents if not d.metadata.review_date])
    )

@app.get("/analytics/search-trends")
async def get_search_trends(days: int = 30):
    """Get search trends over time"""
    
    # Group searches by day
    daily_searches = {}
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for search in search_queries:
        if search.created_at >= cutoff_date:
            date_key = search.created_at.strftime("%Y-%m-%d")
            daily_searches[date_key] = daily_searches.get(date_key, 0) + 1
    
    # Fill in missing days
    trend_data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_key = date.strftime("%Y-%m-%d")
        trend_data.append({
            "date": date_key,
            "searches": daily_searches.get(date_key, 0)
        })
    
    trend_data.reverse()
    
    return {
        "period_days": days,
        "total_searches": sum(daily_searches.values()),
        "average_daily_searches": sum(daily_searches.values()) / days,
        "trend_data": trend_data
    }

# Document Templates Endpoints
@app.get("/templates", response_model=List[KnowledgeTemplate])
async def get_templates():
    """Get available document templates"""
    return templates

@app.post("/templates", response_model=KnowledgeTemplate)
async def create_template(template_data: KnowledgeTemplate):
    """Create a new document template"""
    templates.append(template_data)
    logger.info(f"Created new template: {template_data.name}")
    return template_data

@app.post("/documents/from-template/{template_id}", response_model=Document)
async def create_document_from_template(
    template_id: str,
    title: str,
    author: str,
    department: str,
    field_values: Dict[str, str] = {}
):
    """Create a document from a template"""
    
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Replace template placeholders with values
    content = template.template_content
    for field, value in field_values.items():
        content = content.replace(f"{{{{{field}}}}}", value)
    
    # Create document
    doc = Document(
        title=title,
        content=content,
        summary=f"Document created from {template.name} template",
        document_type=template.document_type,
        category="Generated",
        metadata=DocumentMetadata(
            author=author,
            department=department,
            tags=["template-generated"]
        )
    )
    
    documents.append(doc)
    template.usage_count += 1
    
    logger.info(f"Created document from template: {title}")
    return doc

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
