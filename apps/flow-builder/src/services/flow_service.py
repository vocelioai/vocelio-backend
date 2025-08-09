# apps/flow-builder/src/services/flow_service.py
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from shared.database.client import get_database_session
from models.flow import Flow, FlowVersion
from schemas.flow import FlowCreate, FlowUpdate, FlowResponse, FlowList
from datetime import datetime
import json

class FlowService:
    def __init__(self, db: Session = Depends(get_database_session)):
        self.db = db
    
    async def get_flows(
        self,
        user_id: UUID,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[FlowList]:
        """Get all flows for a user/organization with filtering"""
        query = self.db.query(Flow).filter(
            Flow.organization_id == organization_id
        )
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Flow.name.ilike(f"%{search}%"),
                    Flow.description.ilike(f"%{search}%")
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Flow.category == category)
        
        # Order by updated date
        query = query.order_by(Flow.updated_at.desc())
        
        # Apply pagination
        flows = query.offset(skip).limit(limit).all()
        
        return [FlowList.from_orm(flow) for flow in flows]
    
    async def create_flow(
        self,
        flow_data: FlowCreate,
        user_id: UUID,
        organization_id: UUID
    ) -> FlowResponse:
        """Create a new flow"""
        
        # Create new flow
        db_flow = Flow(
            name=flow_data.name,
            description=flow_data.description,
            category=flow_data.category,
            flow_data=flow_data.flow_data or {},
            viewport=flow_data.viewport or {"x": 0, "y": 0, "zoom": 1},
            is_template=flow_data.is_template,
            tags=flow_data.tags or [],
            settings=flow_data.settings or {},
            user_id=user_id,
            organization_id=organization_id,
            status="draft",
            version=1
        )
        
        self.db.add(db_flow)
        self.db.commit()
        self.db.refresh(db_flow)
        
        # Create initial version
        await self._create_version(db_flow, user_id, "Initial version")
        
        return FlowResponse.from_orm(db_flow)
    
    async def get_flow_by_id(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> Optional[FlowResponse]:
        """Get a specific flow by ID"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if flow:
            return FlowResponse.from_orm(flow)
        return None
    
    async def update_flow(
        self,
        flow_id: UUID,
        flow_data: FlowUpdate,
        user_id: UUID
    ) -> Optional[FlowResponse]:
        """Update an existing flow"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return None
        
        # Update fields if provided
        update_data = flow_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(flow, field, value)
        
        flow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(flow)
        
        return FlowResponse.from_orm(flow)
    
    async def delete_flow(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a flow"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return False
        
        self.db.delete(flow)
        self.db.commit()
        return True
    
    async def duplicate_flow(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> Optional[FlowResponse]:
        """Duplicate an existing flow"""
        original_flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not original_flow:
            return None
        
        # Create duplicate with modified name
        duplicate_flow = Flow(
            name=f"{original_flow.name} (Copy)",
            description=original_flow.description,
            category=original_flow.category,
            flow_data=original_flow.flow_data,
            viewport=original_flow.viewport,
            is_template=False,  # Duplicates are never templates
            tags=original_flow.tags,
            settings=original_flow.settings,
            user_id=user_id,
            organization_id=original_flow.organization_id,
            status="draft",
            version=1
        )
        
        self.db.add(duplicate_flow)
        self.db.commit()
        self.db.refresh(duplicate_flow)
        
        # Create initial version for duplicate
        await self._create_version(duplicate_flow, user_id, "Duplicated from original")
        
        return FlowResponse.from_orm(duplicate_flow)
    
    async def publish_flow(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> bool:
        """Publish a flow for production use"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return False
        
        # Validate flow before publishing
        validation_result = await self._validate_flow(flow)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot publish invalid flow: {validation_result['errors']}"
            )
        
        flow.status = "published"
        flow.published_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def unpublish_flow(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> bool:
        """Unpublish a flow"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return False
        
        flow.status = "draft"
        flow.published_at = None
        
        self.db.commit()
        return True
    
    async def get_flow_versions(
        self,
        flow_id: UUID,
        user_id: UUID
    ) -> List[FlowVersion]:
        """Get all versions of a flow"""
        # Verify user has access to the flow
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return []
        
        versions = self.db.query(FlowVersion).filter(
            FlowVersion.flow_id == flow_id
        ).order_by(FlowVersion.version_number.desc()).all()
        
        return versions
    
    async def save_flow_version(
        self,
        flow_id: UUID,
        version_name: str,
        user_id: UUID
    ) -> Optional[FlowVersion]:
        """Save current flow state as a new version"""
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id
            )
        ).first()
        
        if not flow:
            return None
        
        return await self._create_version(flow, user_id, version_name)
    
    async def _create_version(
        self,
        flow: Flow,
        user_id: UUID,
        description: str
    ) -> FlowVersion:
        """Create a new version of a flow"""
        
        # Get next version number
        latest_version = self.db.query(FlowVersion).filter(
            FlowVersion.flow_id == flow.id
        ).order_by(FlowVersion.version_number.desc()).first()
        
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        # Create version record
        version = FlowVersion(
            flow_id=flow.id,
            version_number=next_version,
            version_name=description,
            flow_data=flow.flow_data,
            viewport=flow.viewport,
            created_by=user_id,
            description=description
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        return version
    
    async def _validate_flow(self, flow: Flow) -> Dict[str, Any]:
        """Validate a flow for publishing"""
        errors = []
        warnings = []
        
        # Check if flow has nodes
        if not flow.flow_data.get("nodes"):
            errors.append("Flow must have at least one node")
        
        # Check for start node
        nodes = flow.flow_data.get("nodes", [])
        has_start_node = any(node.get("type") == "start" for node in nodes)
        if not has_start_node:
            errors.append("Flow must have a start node")
        
        # Check for end node
        has_end_node = any(node.get("type") == "end" for node in nodes)
        if not has_end_node:
            warnings.append("Flow should have an end node")
        
        # Check for disconnected nodes
        edges = flow.flow_data.get("edges", [])
        node_ids = {node.get("id") for node in nodes}
        connected_nodes = set()
        
        for edge in edges:
            connected_nodes.add(edge.get("source"))
            connected_nodes.add(edge.get("target"))
        
        disconnected_nodes = node_ids - connected_nodes
        if disconnected_nodes and len(nodes) > 1:
            warnings.append(f"Found {len(disconnected_nodes)} disconnected nodes")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }