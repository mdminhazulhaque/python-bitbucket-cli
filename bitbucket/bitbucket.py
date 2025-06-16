#!/usr/bin/env python3
"""
Bitbucket API client for interacting with Bitbucket repositories.
"""

import requests
from typing import Dict, Any, Optional, Generator, Tuple
import sys


class BitBucketClientError(Exception):
    """Custom exception for Bitbucket client errors."""
    pass


class BitBucketClient:
    """Client for interacting with Bitbucket API v2.0."""
    
    BASE_URL = "https://api.bitbucket.org/2.0"
    
    def __init__(self, auth: Tuple[str, str]):
        """
        Initialize the Bitbucket client.
        
        Args:
            auth: Tuple of (username, app_password)
        """
        if not auth or len(auth) != 2:
            raise BitBucketClientError("Authentication tuple (username, password) is required")
        
        self.auth = auth
        self.session = requests.Session()
        self.session.auth = auth
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Bitbucket API.
        
        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method (GET, POST, DELETE)
            data: JSON data for POST requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            BitBucketClientError: If the request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                response = self.session.get(url)
                
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            raise BitBucketClientError(f"API request failed: {e}")
        except ValueError as e:
            raise BitBucketClientError(f"Failed to parse JSON response: {e}")

    
    def get_repositories(self, workspace: str) -> Generator[str, None, None]:
        """
        Get all repositories from a workspace.
        
        Args:
            workspace: Bitbucket workspace name
            
        Yields:
            Repository names
        """
        page = 1
        while True:
            endpoint = f"/repositories/{workspace}?sort=-updated_on&page={page}"
            try:
                data = self._make_request(endpoint)
                for repo in data.get('values', []):
                    yield repo['name']
                    
                if 'next' not in data:
                    break
                page += 1
            except BitBucketClientError:
                break
    
    def get_branches(self, workspace: str, repo: str) -> Generator[str, None, None]:
        """
        Get all branches from a repository.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            
        Yields:
            Branch names
        """
        endpoint = f"/repositories/{workspace}/{repo}/refs/branches"
        while True:
            try:
                data = self._make_request(endpoint)
                for branch in data.get('values', []):
                    yield branch['name']
                    
                if 'next' not in data:
                    break
                endpoint = data['next'].replace(self.BASE_URL, "")
            except BitBucketClientError:
                break
    
    def get_commits(self, workspace: str, repo: str, branch: str = "master", all_commits: bool = False) -> Generator[Dict[str, str], None, None]:
        """
        Get commits from a repository branch.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            branch: Branch name (default: master)
            all_commits: Whether to fetch all commits or just the first page
            
        Yields:
            Commit information dictionaries
        """
        endpoint = f"/repositories/{workspace}/{repo}/commits/{branch}"
        while True:
            try:
                data = self._make_request(endpoint)
                for commit in data.get('values', []):
                    yield {
                        'hash': commit['hash'],
                        'date': commit['date'],
                        'message': commit['message'].split("\n")[0],
                        'author': commit.get('author', {}).get('display_name', 'Unknown')
                    }
                    
                if not all_commits or 'next' not in data:
                    break
                endpoint = data['next'].replace(self.BASE_URL, "")
            except BitBucketClientError:
                break
    
    def get_pipelines(self, workspace: str, repo: str, all_pipelines: bool = False) -> Generator[Dict[str, str], None, None]:
        """
        Get pipeline builds from a repository.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            all_pipelines: Whether to fetch all pipelines or just the first page
            
        Yields:
            Pipeline information dictionaries
        """
        endpoint = f"/repositories/{workspace}/{repo}/pipelines/?sort=-created_on"
        while True:
            try:
                data = self._make_request(endpoint)
                for pipeline in data.get('values', []):
                    yield {
                        'created_on': pipeline['created_on'],
                        'branch': pipeline.get('target', {}).get('selector', {}).get('pattern', 'N/A'),
                        'creator': pipeline.get('creator', {}).get('display_name', 'Unknown'),
                        'state': pipeline.get('state', {}).get('name', 'Unknown'),
                        'build_number': pipeline.get('build_number', 'N/A')
                    }
                    
                if not all_pipelines or 'next' not in data:
                    break
                endpoint = data['next'].replace(self.BASE_URL, "")
            except BitBucketClientError:
                break

    
    def trigger_pipeline(self, workspace: str, repo: str, branch: str, 
                        commit: Optional[str] = None, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger a pipeline for a branch or specific commit.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            branch: Branch name
            commit: Specific commit hash (optional)
            pattern: Custom pipeline pattern (optional)
            
        Returns:
            Pipeline trigger response
            
        Raises:
            BitBucketClientError: If pipeline trigger fails
        """
        endpoint = f"/repositories/{workspace}/{repo}/pipelines/"
        
        if commit and pattern:
            data = {
                "target": {
                    "commit": {
                        "hash": commit,
                        "type": "commit"
                    },
                    "selector": {
                        "type": "custom",
                        "pattern": pattern
                    },
                    "type": "pipeline_ref_target",
                    "ref_type": "branch",
                    "ref_name": branch
                }
            }
        else:
            data = {
                "target": {
                    "ref_type": "branch",
                    "type": "pipeline_ref_target",
                    "ref_name": branch
                }
            }
        
        try:
            response = self._make_request(endpoint, method="POST", data=data)
            return {
                'build_number': response.get('build_number'),
                'url': f"https://bitbucket.org/{workspace}/{repo}/addon/pipelines/home#!/results/{response.get('build_number')}"
            }
        except BitBucketClientError as e:
            raise BitBucketClientError(f"Failed to trigger pipeline: {e}")
    
    def get_variables(self, workspace: str, repo: str) -> Generator[Dict[str, str], None, None]:
        """
        Get pipeline variables from a repository.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            
        Yields:
            Variable information dictionaries
        """
        endpoint = f"/repositories/{workspace}/{repo}/pipelines_config/variables/"
        try:
            data = self._make_request(endpoint)
            for variable in data.get('values', []):
                yield {
                    'uuid': variable['uuid'],
                    'key': variable['key'],
                    'value': "*" * 20 if variable['secured'] else variable['value'],
                    'secured': variable['secured']
                }
        except BitBucketClientError:
            pass
    
    def create_variable(self, workspace: str, repo: str, key: str, value: str, secured: bool = False) -> str:
        """
        Create a pipeline variable.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            key: Variable key
            value: Variable value
            secured: Whether the variable should be secured
            
        Returns:
            UUID of the created variable
            
        Raises:
            BitBucketClientError: If variable creation fails
        """
        endpoint = f"/repositories/{workspace}/{repo}/pipelines_config/variables/"
        data = {
            "key": key,
            "value": value,
            "secured": secured
        }
        
        try:
            response = self._make_request(endpoint, method="POST", data=data)
            return response['uuid']
        except BitBucketClientError as e:
            raise BitBucketClientError(f"Failed to create variable: {e}")
    
    def delete_variable(self, workspace: str, repo: str, variable_uuid: str) -> None:
        """
        Delete a pipeline variable.
        
        Args:
            workspace: Bitbucket workspace name
            repo: Repository name
            variable_uuid: UUID of the variable to delete
            
        Raises:
            BitBucketClientError: If variable deletion fails
        """
        endpoint = f"/repositories/{workspace}/{repo}/pipelines_config/variables/{variable_uuid}"
        
        try:
            self._make_request(endpoint, method="DELETE")
        except BitBucketClientError as e:
            raise BitBucketClientError(f"Failed to delete variable: {e}")