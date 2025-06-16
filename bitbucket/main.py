#!/usr/bin/env python3
"""
Bitbucket CLI - A command-line interface for Bitbucket repositories.
"""

import click
import os
import sys
from typing import Tuple, Optional
from tabulate import tabulate

from .bitbucket import BitBucketClient, BitBucketClientError


def get_auth_from_env() -> Tuple[str, str]:
    """
    Get authentication credentials from environment variable.
    
    Returns:
        Tuple of (username, app_password)
        
    Raises:
        click.ClickException: If BITBUCKET_AUTH is not found or invalid
    """
    auth_str = os.environ.get('BITBUCKET_AUTH')
    if not auth_str:
        raise click.ClickException(
            'BITBUCKET_AUTH environment variable not found.\n'
            'Generate an app password from: https://bitbucket.org/account/settings/app-passwords/\n'
            'Then export it as: export BITBUCKET_AUTH=username:app_password'
        )
    
    try:
        username, password = auth_str.split(":", 1)
        return username, password
    except ValueError:
        raise click.ClickException(
            'BITBUCKET_AUTH must be in format "username:app_password"'
        )


def create_client() -> BitBucketClient:
    """Create and return a configured Bitbucket client."""
    auth = get_auth_from_env()
    return BitBucketClient(auth)


@click.group()
@click.version_option(version='1.0.0', prog_name='bitbucket-cli')
def app():
    """Bitbucket CLI - Interact with your Bitbucket repositories from the command line."""
    pass


@app.command(help="List repositories from a workspace")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--table', '-t', is_flag=True, help="Display output in table format")
def repos(workspace: str, table: bool):
    """List all repositories in a workspace."""
    try:
        client = create_client()
        repos_list = list(client.get_repositories(workspace))
        
        if not repos_list:
            click.echo(f"No repositories found in workspace '{workspace}'")
            return
        
        if table:
            headers = ["Repository Name"]
            data = [[repo] for repo in repos_list]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            for repo in repos_list:
                click.echo(repo)
                
    except BitBucketClientError as e:
        raise click.ClickException(f"Error fetching repositories: {e}")


@app.command(help="List branches from a repository")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--repo', '-r', required=True, help="Repository name")
@click.option('--table', '-t', is_flag=True, help="Display output in table format")
def branches(workspace: str, repo: str, table: bool):
    """List all branches in a repository."""
    try:
        client = create_client()
        branches_list = list(client.get_branches(workspace, repo))
        
        if not branches_list:
            click.echo(f"No branches found in repository '{workspace}/{repo}'")
            return
        
        if table:
            headers = ["Branch Name"]
            data = [[branch] for branch in branches_list]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            for branch in branches_list:
                click.echo(branch)
                
    except BitBucketClientError as e:
        raise click.ClickException(f"Error fetching branches: {e}")


@app.command(help="List commits from a repository")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--repo', '-r', required=True, help="Repository name")
@click.option('--branch', '-b', default='master', help="Branch name (default: master)")
@click.option('--all', '-a', is_flag=True, help="Fetch all commits (not just first page)")
@click.option('--table', '-t', is_flag=True, help="Display output in table format")
def commits(workspace: str, repo: str, branch: str, all: bool, table: bool):
    """List commits from a repository branch."""
    try:
        client = create_client()
        commits_list = list(client.get_commits(workspace, repo, branch, all))
        
        if not commits_list:
            click.echo(f"No commits found in branch '{branch}' of repository '{workspace}/{repo}'")
            return
        
        if table:
            headers = ["Hash", "Date", "Author", "Message"]
            data = [[c['hash'][:8], c['date'], c['author'], c['message']] for c in commits_list]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            for commit in commits_list:
                click.echo(f"{commit['hash'][:8]} {commit['date']} {commit['author']} {commit['message']}")
                
    except BitBucketClientError as e:
        raise click.ClickException(f"Error fetching commits: {e}")


@app.command(help="List pipeline builds from a repository")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--repo', '-r', required=True, help="Repository name")
@click.option('--all', '-a', is_flag=True, help="Fetch all pipelines (not just first page)")
@click.option('--table', '-t', is_flag=True, help="Display output in table format")
def builds(workspace: str, repo: str, all: bool, table: bool):
    """List pipeline builds from a repository."""
    try:
        client = create_client()
        pipelines_list = list(client.get_pipelines(workspace, repo, all))
        
        if not pipelines_list:
            click.echo(f"No pipelines found in repository '{workspace}/{repo}'")
            return
        
        if table:
            headers = ["Build #", "Created", "Branch", "Creator", "State"]
            data = [[p['build_number'], p['created_on'], p['branch'], p['creator'], p['state']] for p in pipelines_list]
            click.echo(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            for pipeline in pipelines_list:
                click.echo(f"{pipeline['build_number']} {pipeline['created_on']} {pipeline['branch']} {pipeline['creator']} {pipeline['state']}")
                
    except BitBucketClientError as e:
        raise click.ClickException(f"Error fetching pipelines: {e}")


@app.command(help="Trigger a pipeline for a branch or commit")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--repo', '-r', required=True, help="Repository name")
@click.option('--branch', '-b', required=True, help="Branch name")
@click.option('--commit', '-c', help="Specific commit hash (optional)")
@click.option('--pattern', '-p', help="Custom pipeline pattern (required if commit is specified)")
def trigger(workspace: str, repo: str, branch: str, commit: Optional[str], pattern: Optional[str]):
    """Trigger a pipeline for a branch or specific commit."""
    if commit and not pattern:
        raise click.ClickException("Pattern is required when triggering pipeline for a specific commit")
    
    try:
        client = create_client()
        result = client.trigger_pipeline(workspace, repo, branch, commit, pattern)
        
        click.echo(f"✅ Pipeline {result['build_number']} started successfully!")
        click.echo(f"🔗 View progress: {result['url']}")
        
    except BitBucketClientError as e:
        raise click.ClickException(f"Error triggering pipeline: {e}")


@app.command(help="Manage pipeline variables")
@click.option('--workspace', '-w', required=True, help="Bitbucket workspace name")
@click.option('--repo', '-r', required=True, help="Repository name")
@click.option('--create', '-c', is_flag=True, help="Create a new variable")
@click.option('--delete', '-d', help="Delete a variable by UUID (format: {uuid})")
@click.option('--key', '-k', help="Variable key (required for creation)")
@click.option('--value', '-v', help="Variable value (required for creation)")
@click.option('--secured', '-s', is_flag=True, help="Mark variable as secured")
@click.option('--table', '-t', is_flag=True, help="Display output in table format")
def variables(workspace: str, repo: str, create: bool, delete: Optional[str], 
             key: Optional[str], value: Optional[str], secured: bool, table: bool):
    """Manage pipeline variables for a repository."""
    try:
        client = create_client()
        
        if create:
            if not key or not value:
                raise click.ClickException("Both --key and --value are required when creating a variable")
            
            variable_uuid = client.create_variable(workspace, repo, key, value, secured)
            click.echo(f"✅ Variable created successfully with UUID: {variable_uuid}")
            
        elif delete:
            # Remove curly braces if present
            uuid_clean = delete.strip('{}')
            client.delete_variable(workspace, repo, uuid_clean)
            click.echo(f"✅ Variable {delete} deleted successfully")
            
        else:
            # List variables
            variables_list = list(client.get_variables(workspace, repo))
            
            if not variables_list:
                click.echo(f"No variables found in repository '{workspace}/{repo}'")
                return
            
            if table:
                headers = ["UUID", "Key", "Value", "Secured"]
                data = [[v['uuid'], v['key'], v['value'], "Yes" if v['secured'] else "No"] for v in variables_list]
                click.echo(tabulate(data, headers=headers, tablefmt="grid"))
            else:
                for var in variables_list:
                    secured_indicator = "🔒" if var['secured'] else "🔓"
                    click.echo(f"{var['uuid']} {var['key']} {var['value']} {secured_indicator}")
                    
    except BitBucketClientError as e:
        raise click.ClickException(f"Error managing variables: {e}")


if __name__ == "__main__":
    app()
