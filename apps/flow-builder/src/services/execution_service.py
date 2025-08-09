# apps/flow-builder/src/services/execution_service.py
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from shared.database.client import get_database_session
from models.flow import Flow
from models.node import Node, NodeConnection
from schemas.execution import ExecutionRequest, ExecutionResponse, ExecutionStep
from datetime import datetime
import asyncio
import json

class FlowExecutionService:
    def __init__(self, db: Session = Depends(get_database_session)):
        self.db = db
    
    async def execute_flow(
        self,
        flow_id: UUID,
        execution_data: ExecutionRequest,
        user_id: UUID
    ) -> ExecutionResponse:
        """Execute a flow with given input data"""
        
        # Get the flow
        flow = self.db.query(Flow).filter(
            and_(
                Flow.id == flow_id,
                Flow.user_id == user_id,
                Flow.status == "published"
            )
        ).first()
        
        if not flow:
            raise HTTPException(status_code=404, detail="Published flow not found")
        
        # Initialize execution context
        execution_id = uuid4()
        context = {
            "execution_id": execution_id,
            "flow_id": flow_id,
            "user_id": user_id,
            "input_data": execution_data.input_data,
            "variables": execution_data.variables or {},
            "steps": [],
            "current_node": None,
            "status": "running",
            "started_at": datetime.utcnow()
        }
        
        try:
            # Find start node
            start_node = self._find_start_node(flow)
            if not start_node:
                raise HTTPException(status_code=400, detail="Flow has no start node")
            
            # Execute the flow
            result = await self._execute_node(start_node, context)
            
            # Update flow statistics
            await self._update_flow_stats(flow, context)
            
            return ExecutionResponse(
                execution_id=execution_id,
                flow_id=flow_id,
                status=context["status"],
                result=result,
                steps=context["steps"],
                variables=context["variables"],
                started_at=context["started_at"],
                completed_at=datetime.utcnow(),
                duration=(datetime.utcnow() - context["started_at"]).seconds
            )
            
        except Exception as e:
            context["status"] = "error"
            context["error"] = str(e)
            
            return ExecutionResponse(
                execution_id=execution_id,
                flow_id=flow_id,
                status="error",
                error=str(e),
                steps=context["steps"],
                variables=context["variables"],
                started_at=context["started_at"],
                completed_at=datetime.utcnow(),
                duration=(datetime.utcnow() - context["started_at"]).seconds
            )
    
    async def _execute_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single node"""
        
        context["current_node"] = node.id
        
        # Add step to execution trace
        step = ExecutionStep(
            node_id=node.id,
            node_type=node.node_type,
            started_at=datetime.utcnow()
        )
        
        try:
            # Execute node based on type
            result = await self._execute_node_type(node, context)
            
            step.completed_at = datetime.utcnow()
            step.status = "completed"
            step.result = result
            
            context["steps"].append(step)
            
            # Find next node(s)
            next_nodes = await self._get_next_nodes(node, result, context)
            
            # Continue execution if there are next nodes
            if next_nodes:
                if len(next_nodes) == 1:
                    return await self._execute_node(next_nodes[0], context)
                else:
                    # Handle multiple paths (parallel execution)
                    results = []
                    for next_node in next_nodes:
                        node_result = await self._execute_node(next_node, context.copy())
                        results.append(node_result)
                    return {"parallel_results": results}
            else:
                # End of flow
                context["status"] = "completed"
                return result
                
        except Exception as e:
            step.completed_at = datetime.utcnow()
            step.status = "error"
            step.error = str(e)
            context["steps"].append(step)
            context["status"] = "error"
            raise e
    
    async def _execute_node_type(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific node type logic"""
        
        node_type = node.node_type
        node_data = node.data or {}
        
        if node_type == "start":
            return await self._execute_start_node(node, context)
        elif node_type == "message":
            return await self._execute_message_node(node, context)
        elif node_type == "condition":
            return await self._execute_condition_node(node, context)
        elif node_type == "ai_response":
            return await self._execute_ai_response_node(node, context)
        elif node_type == "collect_input":
            return await self._execute_collect_input_node(node, context)
        elif node_type == "transfer":
            return await self._execute_transfer_node(node, context)
        elif node_type == "end":
            return await self._execute_end_node(node, context)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    async def _execute_start_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute start node"""
        return {
            "action": "flow_started",
            "trigger_type": node.data.get("trigger_type", "manual"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _execute_message_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute message node"""
        message = node.data.get("message", "")
        voice_id = node.data.get("voice_id")
        
        # Process template variables in message
        processed_message = self._process_template(message, context["variables"])
        
        return {
            "action": "message_sent",
            "message": processed_message,
            "voice_id": voice_id,
            "duration": len(processed_message) * 0.1  # Estimate based on text length
        }
    
    async def _execute_condition_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute condition node"""
        condition_type = node.data.get("condition_type")
        condition_logic = node.data.get("condition_logic", {})
        
        # Evaluate condition based on type
        if condition_type == "user_input":
            result = self._evaluate_user_input_condition(condition_logic, context)
        elif condition_type == "ai_analysis":
            result = await self._evaluate_ai_condition(condition_logic, context)
        else:
            result = self._evaluate_custom_condition(condition_logic, context)
        
        return {
            "action": "condition_evaluated",
            "condition_type": condition_type,
            "result": result,
            "branch": "true" if result else "false"
        }
    
    async def _execute_ai_response_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute AI response node"""
        prompt = node.data.get("prompt", "")
        model = node.data.get("model", "gpt-4")
        max_tokens = node.data.get("max_tokens", 150)
        
        # Process template variables in prompt
        processed_prompt = self._process_template(prompt, context["variables"])
        
        # Simulate AI response (replace with actual AI service call)
        ai_response = await self._call_ai_service(processed_prompt, model, max_tokens)
        
        # Store AI response in context variables
        context["variables"]["last_ai_response"] = ai_response
        
        return {
            "action": "ai_response_generated",
            "prompt": processed_prompt,
            "response": ai_response,
            "model": model,
            "tokens_used": len(ai_response.split())
        }
    
    async def _execute_collect_input_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute collect input node"""
        input_type = node.data.get("input_type", "speech")
        timeout = node.data.get("timeout", 5)
        retries = node.data.get("retries", 3)
        
        # Simulate input collection (replace with actual call service)
        collected_input = await self._collect_user_input(input_type, timeout, retries)
        
        # Store collected input in context variables
        context["variables"]["user_input"] = collected_input
        
        return {
            "action": "input_collected",
            "input_type": input_type,
            "input_value": collected_input,
            "success": bool(collected_input)
        }
    
    async def _execute_transfer_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute transfer node"""
        transfer_number = node.data.get("transfer_number")
        transfer_type = node.data.get("transfer_type", "cold")
        
        if not transfer_number:
            raise ValueError("Transfer number is required")
        
        # Simulate call transfer (replace with actual call service)
        transfer_result = await self._transfer_call(transfer_number, transfer_type)
        
        return {
            "action": "call_transferred",
            "transfer_number": transfer_number,
            "transfer_type": transfer_type,
            "success": transfer_result["success"]
        }
    
    async def _execute_end_node(
        self,
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute end node"""
        end_reason = node.data.get("end_reason", "completed")
        
        context["status"] = "completed"
        
        return {
            "action": "flow_ended",
            "end_reason": end_reason,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _find_start_node(self, flow: Flow) -> Optional[Node]:
        """Find the start node in a flow"""
        return self.db.query(Node).filter(
            and_(
                Node.flow_id == flow.id,
                Node.node_type == "start"
            )
        ).first()
    
    async def _get_next_nodes(
        self,
        current_node: Node,
        execution_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Node]:
        """Get the next nodes to execute based on current node and result"""
        
        connections = self.db.query(NodeConnection).filter(
            NodeConnection.source_node_id == current_node.id
        ).all()
        
        next_nodes = []
        
        for connection in connections:
            # Check if this connection should be followed
            should_follow = self._should_follow_connection(
                connection, execution_result, context
            )
            
            if should_follow:
                target_node = self.db.query(Node).filter(
                    Node.id == connection.target_node_id
                ).first()
                if target_node:
                    next_nodes.append(target_node)
        
        return next_nodes
    
    def _should_follow_connection(
        self,
        connection: NodeConnection,
        execution_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if a connection should be followed"""
        
        connection_type = connection.connection_type
        
        if connection_type == "default":
            return True
        elif connection_type == "conditional":
            # Evaluate condition
            condition = connection.condition or {}
            return self._evaluate_connection_condition(condition, execution_result, context)
        elif connection_type == "success":
            return execution_result.get("success", False)
        elif connection_type == "error":
            return not execution_result.get("success", True)
        else:
            return True
    
    def _evaluate_connection_condition(
        self,
        condition: Dict[str, Any],
        execution_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate a connection condition"""
        # Simple condition evaluation - can be expanded
        if "field" in condition and "operator" in condition and "value" in condition:
            field = condition["field"]
            operator = condition["operator"]
            expected_value = condition["value"]
            
            # Get actual value from result or context
            actual_value = execution_result.get(field) or context["variables"].get(field)
            
            if operator == "equals":
                return actual_value == expected_value
            elif operator == "not_equals":
                return actual_value != expected_value
            elif operator == "contains":
                return expected_value in str(actual_value)
            elif operator == "greater_than":
                return float(actual_value) > float(expected_value)
            elif operator == "less_than":
                return float(actual_value) < float(expected_value)
        
        return True
    
    def _evaluate_user_input_condition(
        self,
        condition_logic: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate user input condition"""
        user_input = context["variables"].get("user_input", "").lower()
        expected_values = condition_logic.get("expected_values", [])
        
        return any(expected.lower() in user_input for expected in expected_values)
    
    async def _evaluate_ai_condition(
        self,
        condition_logic: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate AI-based condition"""
        # Simulate AI evaluation (replace with actual AI service call)
        prompt = condition_logic.get("evaluation_prompt", "")
        data_to_analyze = context["variables"].get("user_input", "")
        
        # Call AI service to evaluate condition
        ai_result = await self._call_ai_service(
            f"{prompt}\n\nData to analyze: {data_to_analyze}\n\nReturn only 'true' or 'false':",
            "gpt-4",
            10
        )
        
        return "true" in ai_result.lower()
    
    def _evaluate_custom_condition(
        self,
        condition_logic: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate custom condition logic"""
        # Simple custom condition evaluation
        expression = condition_logic.get("expression", "true")
        variables = context["variables"]
        
        try:
            # Safe evaluation with limited scope
            allowed_names = {
                "variables": variables,
                "input_data": context["input_data"],
                "__builtins__": {}
            }
            return eval(expression, allowed_names)
        except:
            return False
    
    def _process_template(
        self,
        template: str,
        variables: Dict[str, Any]
    ) -> str:
        """Process template string with variables"""
        processed = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            processed = processed.replace(placeholder, str(value))
        
        return processed
    
    async def _call_ai_service(
        self,
        prompt: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Call AI service for response generation"""
        # Simulate AI service call (replace with actual implementation)
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return f"AI response to: {prompt[:50]}..."
    
    async def _collect_user_input(
        self,
        input_type: str,
        timeout: int,
        retries: int
    ) -> str:
        """Collect user input (simulate for now)"""
        # Simulate input collection (replace with actual call service)
        await asyncio.sleep(0.1)
        
        if input_type == "speech":
            return "user said something"
        elif input_type == "dtmf":
            return "1"
        else:
            return "mixed input"
    
    async def _transfer_call(
        self,
        transfer_number: str,
        transfer_type: str
    ) -> Dict[str, Any]:
        """Transfer call to another number"""
        # Simulate call transfer (replace with actual call service)
        await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "transfer_number": transfer_number,
            "transfer_type": transfer_type
        }
    
    async def _update_flow_stats(
        self,
        flow: Flow,
        context: Dict[str, Any]
    ) -> None:
        """Update flow execution statistics"""
        flow.total_executions += 1
        flow.last_executed_at = datetime.utcnow()
        
        # Update success rate
        if context["status"] == "completed":
            current_success_rate = flow.success_rate or 0
            total_executions = flow.total_executions
            new_success_rate = ((current_success_rate * (total_executions - 1)) + 100) / total_executions
            flow.success_rate = int(new_success_rate)
        
        # Update average duration
        duration = (datetime.utcnow() - context["started_at"]).seconds
        current_avg = flow.avg_duration or 0
        total_executions = flow.total_executions
        new_avg = ((current_avg * (total_executions - 1)) + duration) / total_executions
        flow.avg_duration = int(new_avg)
        
        self.db.commit()