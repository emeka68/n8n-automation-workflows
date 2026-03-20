"""
n8n REST API Client

Provides methods to interact with n8n workflows via REST API.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any


class N8nClient:
    """Client for n8n REST API operations."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize n8n client.
        
        Args:
            base_url: n8n instance URL (defaults to N8N_URL env var)
            api_key: n8n API key (defaults to N8N_API_KEY env var)
        """
        self.base_url = base_url or os.getenv("N8N_URL", "http://localhost:5678")
        self.api_key = api_key or os.getenv("N8N_API_KEY", "")
        self.base_url = self.base_url.rstrip("/")
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to n8n API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            
        Returns:
            Response JSON as dict
        """
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        kwargs = {"headers": self.headers}
        
        if data:
            kwargs["json"] = data

        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        
        return response.json() if response.text else {}

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.
        
        Returns:
            List of workflow objects
        """
        data = self._request("GET", "workflows")
        return data.get("data", [])

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get a single workflow by ID.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow object
        """
        return self._request("GET", f"workflows/{workflow_id}")

    def create_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow.
        
        Args:
            workflow_json: Workflow JSON definition
            
        Returns:
            Created workflow object
        """
        return self._request("POST", "workflows", workflow_json)

    def update_workflow(
        self, workflow_id: str, workflow_json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing workflow.
        
        Args:
            workflow_id: Workflow ID
            workflow_json: Updated workflow JSON
            
        Returns:
            Updated workflow object
        """
        return self._request("PUT", f"workflows/{workflow_id}", workflow_json)

    def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Activate a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Updated workflow object
        """
        return self._request("PATCH", f"workflows/{workflow_id}/activate")

    def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deactivate a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Updated workflow object
        """
        return self._request("PATCH", f"workflows/{workflow_id}/deactivate")

    def delete_workflow(self, workflow_id: str) -> None:
        """
        Delete a workflow.
        
        Args:
            workflow_id: Workflow ID
        """
        self._request("DELETE", f"workflows/{workflow_id}")

    def get_workflow_executions(self, workflow_id: str, limit: int = 10) -> List[Dict]:
        """
        Get execution history for a workflow.
        
        Args:
            workflow_id: Workflow ID
            limit: Maximum number of executions to return
            
        Returns:
            List of execution objects
        """
        data = self._request("GET", f"workflows/{workflow_id}/executions?limit={limit}")
        return data.get("data", [])
