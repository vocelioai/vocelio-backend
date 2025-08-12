"""
Enterprise Security Service - Vocelio AI Enterprise Platform
Advanced Security Operations, Threat Detection, and Security Monitoring
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Header, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, EmailStr, validator, IPvAnyAddress
from typing import List, Optional, Dict, Any, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import ipaddress
import re
from collections import defaultdict, deque
import asyncio
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

# Security Models
class ThreatLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class SecurityEventType(str, Enum):
    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTED = "malware_detected"
    SUSPICIOUS_LOGIN = "suspicious_login"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DDOS_ATTACK = "ddos_attack"
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    CSRF_ATTACK = "csrf_attack"
    PHISHING_ATTEMPT = "phishing_attempt"
    INSIDER_THREAT = "insider_threat"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    POLICY_VIOLATION = "policy_violation"

class AlertStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"

class SecurityPolicyType(str, Enum):
    ACCESS_CONTROL = "access_control"
    PASSWORD_POLICY = "password_policy"
    NETWORK_SECURITY = "network_security"
    DATA_PROTECTION = "data_protection"
    ENCRYPTION = "encryption"
    BACKUP_RECOVERY = "backup_recovery"
    INCIDENT_RESPONSE = "incident_response"
    VULNERABILITY_MANAGEMENT = "vulnerability_management"

class VulnerabilitySeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class SecurityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_ip: str
    destination_ip: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    resource: str
    action: str
    outcome: str  # success, failure, blocked
    details: Dict[str, Any] = {}
    indicators: List[str] = []  # IOCs (Indicators of Compromise)
    mitre_tactics: List[str] = []  # MITRE ATT&CK tactics
    mitre_techniques: List[str] = []  # MITRE ATT&CK techniques
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.5)
    correlation_id: Optional[str] = None
    parent_event_id: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None
    device_fingerprint: Optional[str] = None
    raw_log: Optional[str] = None
    investigation_notes: List[str] = []
    related_alerts: List[str] = []

class SecurityAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    description: str
    threat_level: ThreatLevel
    status: AlertStatus = AlertStatus.OPEN
    event_ids: List[str] = []
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalation_count: int = 0
    false_positive_probability: float = Field(ge=0.0, le=1.0, default=0.0)
    impact_assessment: Optional[str] = None
    remediation_steps: List[str] = []
    timeline: List[Dict[str, Any]] = []
    affected_assets: List[str] = []
    iocs: List[str] = []  # Indicators of Compromise
    ttps: List[str] = []  # Tactics, Techniques, and Procedures

class ThreatIntelligence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    indicator_type: str  # ip, domain, hash, url, email
    indicator_value: str
    threat_type: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = []
    description: Optional[str] = None
    attribution: Optional[str] = None
    malware_families: List[str] = []
    kill_chain_phases: List[str] = []
    is_active: bool = True
    expiry_date: Optional[datetime] = None

class SecurityPolicy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    policy_name: str
    policy_type: SecurityPolicyType
    description: str
    rules: List[Dict[str, Any]] = []
    enforcement_level: str = "enforce"  # monitor, warn, enforce
    is_active: bool = True
    applies_to: List[str] = []  # user groups, departments, etc.
    exceptions: List[str] = []
    created_by: str
    approved_by: Optional[str] = None
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    review_date: Optional[datetime] = None
    compliance_frameworks: List[str] = []
    violation_count: int = 0
    last_violation: Optional[datetime] = None

class Vulnerability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    cve_id: Optional[str] = None
    title: str
    description: str
    severity: VulnerabilitySeverity
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    affected_assets: List[str] = []
    affected_services: List[str] = []
    discovery_method: str
    discovered_date: datetime = Field(default_factory=datetime.utcnow)
    reported_by: str
    status: str = "open"  # open, assigned, in_progress, resolved, risk_accepted
    assigned_to: Optional[str] = None
    remediation_steps: List[str] = []
    workarounds: List[str] = []
    exploit_available: bool = False
    exploit_public: bool = False
    patch_available: bool = False
    patch_details: Optional[str] = None
    business_impact: str
    remediation_timeline: Optional[datetime] = None
    resolution_date: Optional[datetime] = None
    verification_status: str = "pending"  # pending, verified, false_positive

class SecurityMetric(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    metric_name: str
    metric_type: str  # count, percentage, average, etc.
    value: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period: str  # hourly, daily, weekly, monthly
    tags: Dict[str, str] = {}
    threshold_breached: bool = False
    threshold_value: Optional[float] = None

class IncidentResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    incident_title: str
    incident_type: str
    severity: ThreatLevel
    status: str = "identified"  # identified, contained, eradicated, recovered, closed
    incident_commander: str
    response_team: List[str] = []
    start_time: datetime = Field(default_factory=datetime.utcnow)
    detection_time: Optional[datetime] = None
    containment_time: Optional[datetime] = None
    eradication_time: Optional[datetime] = None
    recovery_time: Optional[datetime] = None
    closure_time: Optional[datetime] = None
    affected_systems: List[str] = []
    impact_assessment: str
    root_cause: Optional[str] = None
    lessons_learned: List[str] = []
    action_items: List[Dict[str, Any]] = []
    timeline: List[Dict[str, Any]] = []
    evidence_collected: List[str] = []
    communication_log: List[Dict[str, Any]] = []

# In-memory storage (replace with proper database in production)
security_events_db: List[SecurityEvent] = []
security_alerts_db: Dict[str, SecurityAlert] = {}
threat_intelligence_db: Dict[str, ThreatIntelligence] = {}
security_policies_db: Dict[str, SecurityPolicy] = {}
vulnerabilities_db: Dict[str, Vulnerability] = {}
security_metrics_db: List[SecurityMetric] = []
incident_responses_db: Dict[str, IncidentResponse] = {}

# Real-time connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_alert(self, alert: SecurityAlert):
        message = {
            "type": "security_alert",
            "data": alert.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        disconnected_clients = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

manager = ConnectionManager()

# Threat detection rules
threat_detection_rules = {
    "brute_force": {
        "condition": lambda events: len([e for e in events if e.outcome == "failure"]) >= 5,
        "time_window": 300,  # 5 minutes
        "threat_level": ThreatLevel.HIGH
    },
    "suspicious_login": {
        "condition": lambda events: any(e.geolocation and e.geolocation.get("country") not in ["US", "CA"] for e in events),
        "time_window": 60,
        "threat_level": ThreatLevel.MEDIUM
    },
    "privilege_escalation": {
        "condition": lambda events: any("admin" in e.action.lower() or "root" in e.action.lower() for e in events),
        "time_window": 900,  # 15 minutes
        "threat_level": ThreatLevel.CRITICAL
    }
}

# Utility functions
def calculate_risk_score(threat_level: ThreatLevel, confidence: float, business_impact: str) -> float:
    """Calculate overall risk score"""
    threat_weights = {
        ThreatLevel.CRITICAL: 1.0,
        ThreatLevel.HIGH: 0.8,
        ThreatLevel.MEDIUM: 0.6,
        ThreatLevel.LOW: 0.4,
        ThreatLevel.INFO: 0.2
    }
    
    impact_weights = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.6,
        "low": 0.4,
        "minimal": 0.2
    }
    
    threat_weight = threat_weights.get(threat_level, 0.5)
    impact_weight = impact_weights.get(business_impact.lower(), 0.5)
    
    return (threat_weight * 0.4 + confidence * 0.3 + impact_weight * 0.3) * 100

def detect_threats(events: List[SecurityEvent]) -> List[SecurityAlert]:
    """Analyze events for potential threats"""
    alerts = []
    
    # Group events by source IP and time window
    for rule_name, rule in threat_detection_rules.items():
        time_cutoff = datetime.utcnow() - timedelta(seconds=rule["time_window"])
        recent_events = [e for e in events if e.timestamp >= time_cutoff]
        
        # Group by source IP
        ip_groups = defaultdict(list)
        for event in recent_events:
            ip_groups[event.source_ip].append(event)
        
        for source_ip, ip_events in ip_groups.items():
            if rule["condition"](ip_events):
                alert = SecurityAlert(
                    tenant_id=ip_events[0].tenant_id,
                    title=f"Potential {rule_name.replace('_', ' ').title()} Detected",
                    description=f"Suspicious activity from {source_ip}",
                    threat_level=rule["threat_level"],
                    event_ids=[e.id for e in ip_events],
                    affected_assets=[source_ip],
                    iocs=[source_ip]
                )
                alerts.append(alert)
    
    return alerts

def enrich_event_with_threat_intel(event: SecurityEvent) -> SecurityEvent:
    """Enrich security event with threat intelligence"""
    # Check if source IP is in threat intelligence
    for ti in threat_intelligence_db.values():
        if (ti.indicator_type == "ip" and 
            ti.indicator_value == event.source_ip and 
            ti.is_active):
            event.threat_level = ThreatLevel.HIGH
            event.indicators.append(ti.indicator_value)
            event.details["threat_intel_match"] = {
                "source": ti.source,
                "threat_type": ti.threat_type,
                "confidence": ti.confidence
            }
            break
    
    return event

async def process_security_event(event: SecurityEvent):
    """Process and analyze security event"""
    # Enrich with threat intelligence
    event = enrich_event_with_threat_intel(event)
    
    # Store event
    security_events_db.append(event)
    
    # Detect threats
    recent_events = [e for e in security_events_db 
                    if e.timestamp >= datetime.utcnow() - timedelta(hours=1)]
    alerts = detect_threats(recent_events)
    
    # Create and send alerts
    for alert in alerts:
        security_alerts_db[alert.id] = alert
        await manager.send_alert(alert)
        logger.warning(f"Security alert created: {alert.title}")

# Mock authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"id": "user-123", "tenant_id": "tenant-123", "roles": ["security_admin"]}

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Enterprise Security Service starting up...")
    
    # Load default threat intelligence
    default_threat_intel = [
        ThreatIntelligence(
            indicator_type="ip",
            indicator_value="192.168.1.100",
            threat_type="botnet",
            source="internal_honeypot",
            confidence=0.9,
            tags=["malware", "c2"]
        ),
        ThreatIntelligence(
            indicator_type="domain",
            indicator_value="malicious-site.com",
            threat_type="phishing",
            source="threat_feed",
            confidence=0.85,
            tags=["phishing", "credential_theft"]
        )
    ]
    
    for ti in default_threat_intel:
        threat_intelligence_db[ti.id] = ti
    
    yield
    
    # Shutdown
    logger.info("Enterprise Security Service shutting down...")

# FastAPI app
app = FastAPI(
    title="Vocelio Enterprise Security Service",
    description="Advanced Security Operations, Threat Detection, and Security Monitoring",
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
        "service": "enterprise-security",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# WebSocket endpoint for real-time alerts
@app.websocket("/ws/alerts/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Security Events endpoints
@app.post("/security-events", response_model=SecurityEvent)
async def create_security_event(
    event: SecurityEvent,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create and process security event"""
    event.tenant_id = current_user["tenant_id"]
    background_tasks.add_task(process_security_event, event)
    return event

@app.get("/security-events", response_model=List[SecurityEvent])
async def get_security_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[SecurityEventType] = None,
    threat_level: Optional[ThreatLevel] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source_ip: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get security events with filtering"""
    tenant_events = [e for e in security_events_db if e.tenant_id == current_user["tenant_id"]]
    
    # Apply filters
    if event_type:
        tenant_events = [e for e in tenant_events if e.event_type == event_type]
    if threat_level:
        tenant_events = [e for e in tenant_events if e.threat_level == threat_level]
    if start_date:
        tenant_events = [e for e in tenant_events if e.timestamp >= start_date]
    if end_date:
        tenant_events = [e for e in tenant_events if e.timestamp <= end_date]
    if source_ip:
        tenant_events = [e for e in tenant_events if e.source_ip == source_ip]
    
    # Sort by timestamp (newest first)
    tenant_events.sort(key=lambda x: x.timestamp, reverse=True)
    
    return tenant_events[skip:skip + limit]

@app.get("/security-events/{event_id}", response_model=SecurityEvent)
async def get_security_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific security event"""
    event = next((e for e in security_events_db 
                 if e.id == event_id and e.tenant_id == current_user["tenant_id"]), None)
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found")
    return event

# Security Alerts endpoints
@app.get("/security-alerts", response_model=List[SecurityAlert])
async def get_security_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[AlertStatus] = None,
    threat_level: Optional[ThreatLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get security alerts"""
    tenant_alerts = [a for a in security_alerts_db.values() 
                    if a.tenant_id == current_user["tenant_id"]]
    
    if status:
        tenant_alerts = [a for a in tenant_alerts if a.status == status]
    if threat_level:
        tenant_alerts = [a for a in tenant_alerts if a.threat_level == threat_level]
    
    # Sort by creation time (newest first)
    tenant_alerts.sort(key=lambda x: x.created_at, reverse=True)
    
    return tenant_alerts[skip:skip + limit]

@app.get("/security-alerts/{alert_id}", response_model=SecurityAlert)
async def get_security_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific security alert"""
    alert = security_alerts_db.get(alert_id)
    if not alert or alert.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="Security alert not found")
    return alert

@app.put("/security-alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: AlertStatus,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update security alert status"""
    alert = security_alerts_db.get(alert_id)
    if not alert or alert.tenant_id != current_user["tenant_id"]:
        raise HTTPException(status_code=404, detail="Security alert not found")
    
    old_status = alert.status
    alert.status = status
    alert.updated_at = datetime.utcnow()
    
    if status == AlertStatus.ACKNOWLEDGED:
        alert.acknowledged_at = datetime.utcnow()
    elif status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()
    
    # Add to timeline
    timeline_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": f"Status changed from {old_status} to {status}",
        "user": current_user["id"],
        "notes": notes
    }
    alert.timeline.append(timeline_entry)
    
    security_alerts_db[alert_id] = alert
    return {"message": "Alert status updated successfully"}

# Threat Intelligence endpoints
@app.get("/threat-intelligence", response_model=List[ThreatIntelligence])
async def get_threat_intelligence(
    indicator_type: Optional[str] = None,
    is_active: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence indicators"""
    indicators = list(threat_intelligence_db.values())
    
    if indicator_type:
        indicators = [i for i in indicators if i.indicator_type == indicator_type]
    if is_active is not None:
        indicators = [i for i in indicators if i.is_active == is_active]
    
    return indicators

@app.post("/threat-intelligence", response_model=ThreatIntelligence)
async def create_threat_intelligence(
    threat_intel: ThreatIntelligence,
    current_user: dict = Depends(get_current_user)
):
    """Add new threat intelligence indicator"""
    threat_intelligence_db[threat_intel.id] = threat_intel
    return threat_intel

@app.put("/threat-intelligence/{indicator_id}")
async def update_threat_intelligence(
    indicator_id: str,
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update threat intelligence indicator"""
    indicator = threat_intelligence_db.get(indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Threat intelligence indicator not found")
    
    for key, value in updates.items():
        if hasattr(indicator, key):
            setattr(indicator, key, value)
    
    indicator.last_seen = datetime.utcnow()
    threat_intelligence_db[indicator_id] = indicator
    return {"message": "Threat intelligence updated successfully"}

# Security Policies endpoints
@app.get("/security-policies", response_model=List[SecurityPolicy])
async def get_security_policies(
    policy_type: Optional[SecurityPolicyType] = None,
    is_active: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get security policies"""
    tenant_policies = [p for p in security_policies_db.values() 
                      if p.tenant_id == current_user["tenant_id"]]
    
    if policy_type:
        tenant_policies = [p for p in tenant_policies if p.policy_type == policy_type]
    if is_active is not None:
        tenant_policies = [p for p in tenant_policies if p.is_active == is_active]
    
    return tenant_policies

@app.post("/security-policies", response_model=SecurityPolicy)
async def create_security_policy(
    policy: SecurityPolicy,
    current_user: dict = Depends(get_current_user)
):
    """Create new security policy"""
    policy.tenant_id = current_user["tenant_id"]
    policy.created_by = current_user["id"]
    security_policies_db[policy.id] = policy
    return policy

# Vulnerabilities endpoints
@app.get("/vulnerabilities", response_model=List[Vulnerability])
async def get_vulnerabilities(
    severity: Optional[VulnerabilitySeverity] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get vulnerabilities"""
    tenant_vulns = [v for v in vulnerabilities_db.values() 
                   if v.tenant_id == current_user["tenant_id"]]
    
    if severity:
        tenant_vulns = [v for v in tenant_vulns if v.severity == severity]
    if status:
        tenant_vulns = [v for v in tenant_vulns if v.status == status]
    
    return tenant_vulns

@app.post("/vulnerabilities", response_model=Vulnerability)
async def create_vulnerability(
    vulnerability: Vulnerability,
    current_user: dict = Depends(get_current_user)
):
    """Report new vulnerability"""
    vulnerability.tenant_id = current_user["tenant_id"]
    vulnerability.reported_by = current_user["id"]
    vulnerabilities_db[vulnerability.id] = vulnerability
    return vulnerability

# Incident Response endpoints
@app.get("/incident-responses", response_model=List[IncidentResponse])
async def get_incident_responses(
    status: Optional[str] = None,
    severity: Optional[ThreatLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get incident responses"""
    tenant_incidents = [i for i in incident_responses_db.values() 
                       if i.tenant_id == current_user["tenant_id"]]
    
    if status:
        tenant_incidents = [i for i in tenant_incidents if i.status == status]
    if severity:
        tenant_incidents = [i for i in tenant_incidents if i.severity == severity]
    
    return tenant_incidents

@app.post("/incident-responses", response_model=IncidentResponse)
async def create_incident_response(
    incident: IncidentResponse,
    current_user: dict = Depends(get_current_user)
):
    """Create new incident response"""
    incident.tenant_id = current_user["tenant_id"]
    incident.incident_commander = current_user["id"]
    incident_responses_db[incident.id] = incident
    return incident

# Analytics and Dashboard endpoints
@app.get("/analytics/security-dashboard")
async def get_security_dashboard(
    time_range: int = 24,  # hours
    current_user: dict = Depends(get_current_user)
):
    """Get security dashboard analytics"""
    tenant_id = current_user["tenant_id"]
    cutoff_time = datetime.utcnow() - timedelta(hours=time_range)
    
    # Get recent events and alerts
    recent_events = [e for e in security_events_db 
                    if e.tenant_id == tenant_id and e.timestamp >= cutoff_time]
    recent_alerts = [a for a in security_alerts_db.values() 
                    if a.tenant_id == tenant_id and a.created_at >= cutoff_time]
    
    # Calculate metrics
    total_events = len(recent_events)
    critical_alerts = len([a for a in recent_alerts if a.threat_level == ThreatLevel.CRITICAL])
    open_alerts = len([a for a in recent_alerts if a.status == AlertStatus.OPEN])
    
    # Threat level distribution
    threat_distribution = {}
    for level in ThreatLevel:
        threat_distribution[level.value] = len([e for e in recent_events if e.threat_level == level])
    
    # Top source IPs
    ip_counts = defaultdict(int)
    for event in recent_events:
        ip_counts[event.source_ip] += 1
    top_source_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Attack timeline (hourly buckets)
    timeline = []
    for i in range(time_range):
        hour_start = datetime.utcnow() - timedelta(hours=i+1)
        hour_end = datetime.utcnow() - timedelta(hours=i)
        hour_events = [e for e in recent_events if hour_start <= e.timestamp < hour_end]
        timeline.append({
            "hour": hour_start.strftime("%H:00"),
            "events": len(hour_events),
            "alerts": len([a for a in recent_alerts if hour_start <= a.created_at < hour_end])
        })
    
    timeline.reverse()  # Chronological order
    
    return {
        "total_events": total_events,
        "critical_alerts": critical_alerts,
        "open_alerts": open_alerts,
        "threat_level_distribution": threat_distribution,
        "top_source_ips": [{"ip": ip, "count": count} for ip, count in top_source_ips],
        "attack_timeline": timeline,
        "active_threats": len([ti for ti in threat_intelligence_db.values() if ti.is_active]),
        "open_vulnerabilities": len([v for v in vulnerabilities_db.values() 
                                   if v.tenant_id == tenant_id and v.status == "open"]),
        "mean_time_to_resolution": "2.5 hours",  # Mock metric
        "security_score": max(0, 100 - (critical_alerts * 10 + open_alerts * 5))
    }

@app.get("/analytics/threat-trends")
async def get_threat_trends(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get threat trends over time"""
    tenant_id = current_user["tenant_id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily threat counts
    daily_trends = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        day_events = [e for e in security_events_db 
                     if (e.tenant_id == tenant_id and 
                         day_start <= e.timestamp < day_end)]
        
        threat_counts = {}
        for event_type in SecurityEventType:
            threat_counts[event_type.value] = len([e for e in day_events if e.event_type == event_type])
        
        daily_trends.append({
            "date": day_start.date().isoformat(),
            "total_events": len(day_events),
            "threat_breakdown": threat_counts
        })
    
    return {
        "period_days": days,
        "daily_trends": daily_trends,
        "top_threat_types": [
            {"type": "brute_force", "count": 156, "trend": "+12%"},
            {"type": "suspicious_login", "count": 89, "trend": "-5%"},
            {"type": "malware_detected", "count": 23, "trend": "+45%"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
