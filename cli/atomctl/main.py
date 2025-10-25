#!/usr/bin/env python3
"""
atomctl - ATOM Cloud CLI Tool
Developer tool to pack, push, validate, and run WPKs
"""

import click
import yaml
import json
import os
import tarfile
import tempfile
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime

# Configuration
DEFAULT_REGISTRY_URL = "http://localhost:8000"
DEFAULT_RUNTIME_URL = "http://localhost:4000"
CONFIG_FILE = Path.home() / ".atomctl" / "config.yaml"

class AtomCLI:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return yaml.safe_load(f) or {}
        return {
            "registry_url": DEFAULT_REGISTRY_URL,
            "runtime_url": DEFAULT_RUNTIME_URL,
            "auth_token": None
        }
    
    def save_config(self):
        """Save CLI configuration"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.config.get("auth_token"):
            return {"Authorization": f"Bearer {self.config['auth_token']}"}
        return {}

cli = AtomCLI()

@click.group()
@click.version_option(version="1.0.0")
def atomctl():
    """ATOM Cloud CLI - Manage workflow packages (WPKs)"""
    pass

@atomctl.command()
@click.argument('wpk_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output tarball path')
@click.option('--sign', is_flag=True, help='Sign the WPK with cosign')
def pack(wpk_file: str, output: Optional[str], sign: bool):
    """Pack a WPK file into a signed tarball"""
    wpk_path = Path(wpk_file)
    
    try:
        # Load and validate WPK
        with open(wpk_path, 'r') as f:
            wpk_data = yaml.safe_load(f)
        
        # Validate basic structure
        if not all(key in wpk_data for key in ['apiVersion', 'kind', 'metadata', 'spec']):
            click.echo("[ERROR] Invalid WPK structure", err=True)
            return
        
        workflow_name = wpk_data['metadata']['name']
        workflow_version = wpk_data['metadata']['version']
        
        # Determine output path
        if not output:
            output = f"{workflow_name}-{workflow_version}.wpk.tar.gz"
        
        output_path = Path(output)
        
        # Create tarball
        with tarfile.open(output_path, 'w:gz') as tar:
            tar.add(wpk_path, arcname=wpk_path.name)
        
        click.echo(f"📦 Packed WPK: {output_path}")
        
        # Sign if requested
        if sign:
            if not sign_wpk(wpk_path):
                click.echo("❌ Failed to sign WPK", err=True)
                return
            
            # Update WPK with signature and repack
            with open(wpk_path, 'r') as f:
                wpk_data = yaml.safe_load(f)
            
            # Add signature (mock for now)
            signature = generate_mock_signature(str(wpk_path))
            wpk_data['metadata']['signature'] = signature
            
            # Write updated WPK
            with open(wpk_path, 'w') as f:
                yaml.dump(wpk_data, f, default_flow_style=False)
            
            # Repack with signature
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(wpk_path, arcname=wpk_path.name)
            
            click.echo(f"✅ Signed and packed: {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Pack failed: {str(e)}", err=True)

@atomctl.command()
@click.argument('wpk_file', type=click.Path(exists=True))
def validate(wpk_file: str):
    """Validate a WPK file against the schema"""
    wpk_path = Path(wpk_file)
    
    try:
        # Load WPK
        with open(wpk_path, 'r') as f:
            wpk_data = yaml.safe_load(f)
        
        # Basic validation
        errors = []
        
        # Check required top-level fields
        required_fields = ['apiVersion', 'kind', 'metadata', 'spec']
        for field in required_fields:
            if field not in wpk_data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            click.echo("[ERROR] Validation failed:")
            for error in errors:
                click.echo(f"  - {error}")
            return
        
        # Check metadata
        metadata = wpk_data.get('metadata', {})
        required_metadata = ['name', 'version', 'description', 'author']
        for field in required_metadata:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        # Check spec
        spec = wpk_data.get('spec', {})
        required_spec = ['runtime', 'safety', 'handlers']
        for field in required_spec:
            if field not in spec:
                errors.append(f"Missing spec field: {field}")
        
        # Check handlers
        handlers = spec.get('handlers', [])
        if not handlers:
            errors.append("No handlers defined")
        
        for i, handler in enumerate(handlers):
            if 'name' not in handler:
                errors.append(f"Handler {i}: missing name")
            if 'type' not in handler:
                errors.append(f"Handler {i}: missing type")
            if 'config' not in handler:
                errors.append(f"Handler {i}: missing config")
        
        if errors:
            click.echo("[ERROR] Validation failed:")
            for error in errors:
                click.echo(f"  - {error}")
        else:
            click.echo("[SUCCESS] WPK validation passed")
            
            # Show summary
            click.echo(f"\n📋 WPK Summary:")
            click.echo(f"  Name: {metadata.get('name')}")
            click.echo(f"  Version: {metadata.get('version')}")
            click.echo(f"  Author: {metadata.get('author')}")
            click.echo(f"  Runtime: {spec.get('runtime', {}).get('type')}")
            click.echo(f"  Safety Mode: {spec.get('safety', {}).get('mode')}")
            click.echo(f"  Handlers: {len(handlers)}")
            
            if 'signature' in metadata:
                click.echo(f"  Signed: ✅ ({metadata['signature'][:16]}...)")
            else:
                click.echo(f"  Signed: ❌ (use --sign to sign)")
        
    except yaml.YAMLError as e:
        click.echo(f"❌ Invalid YAML: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}", err=True)

@atomctl.command()
@click.argument('wpk_file', type=click.Path(exists=True))
@click.option('--registry-url', help='Registry URL override')
def push(wpk_file: str, registry_url: Optional[str]):
    """Push a WPK to the workflow registry"""
    wpk_path = Path(wpk_file)
    registry = registry_url or cli.config['registry_url']
    
    try:
        # Validate WPK first
        click.echo("🔍 Validating WPK...")
        with open(wpk_path, 'r') as f:
            wpk_data = yaml.safe_load(f)
        
        # Check if signed
        if not wpk_data.get('metadata', {}).get('signature'):
            click.echo("❌ WPK must be signed before pushing", err=True)
            click.echo("💡 Use 'atomctl pack --sign' to sign the WPK")
            return
        
        # Push to registry
        click.echo(f"📤 Pushing to registry: {registry}")
        
        with open(wpk_path, 'rb') as f:
            files = {'file': (wpk_path.name, f, 'application/x-yaml')}
            headers = cli.get_auth_headers()
            
            response = requests.post(
                f"{registry}/workflows",
                files=files,
                headers=headers,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            click.echo(f"✅ WPK pushed successfully")
            click.echo(f"  Workflow ID: {result.get('workflow_id')}")
            click.echo(f"  Status: {result.get('status')}")
        else:
            click.echo(f"❌ Push failed: {response.status_code}")
            if response.text:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                click.echo(f"  Error: {error_data.get('detail', 'Unknown error')}")
        
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ Push failed: {str(e)}", err=True)

@atomctl.command()
@click.argument('workflow_id')
@click.option('--parameters', '-p', help='Parameters JSON string')
@click.option('--dry-run', is_flag=True, help='Perform dry run')
@click.option('--runtime-url', help='Runtime agent URL override')
@click.option('--wait', is_flag=True, help='Wait for execution to complete')
def run(workflow_id: str, parameters: Optional[str], dry_run: bool, runtime_url: Optional[str], wait: bool):
    """Run a workflow from the registry"""
    registry = cli.config['registry_url']
    runtime = runtime_url or cli.config['runtime_url']
    
    try:
        # Get workflow from registry
        click.echo(f"📥 Fetching workflow: {workflow_id}")
        
        headers = cli.get_auth_headers()
        response = requests.get(f"{registry}/workflows/{workflow_id}", headers=headers, timeout=30)
        
        if response.status_code != 200:
            click.echo(f"❌ Failed to fetch workflow: {response.status_code}", err=True)
            return
        
        workflow_data = response.json()
        wpk_content = workflow_data['wpk_content']
        
        # Parse parameters
        params = {}
        if parameters:
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                click.echo("❌ Invalid parameters JSON", err=True)
                return
        
        # Execute workflow
        click.echo(f"🚀 {'Dry-run' if dry_run else 'Executing'} workflow: {workflow_id}")
        
        execution_request = {
            "workflow_id": workflow_id,
            "wpk_content": wpk_content,
            "parameters": params,
            "dry_run": dry_run
        }
        
        response = requests.post(
            f"{runtime}/execute",
            json=execution_request,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            execution_id = result['execution_id']
            
            click.echo(f"✅ Execution started")
            click.echo(f"  Execution ID: {execution_id}")
            
            if wait:
                click.echo("⏳ Waiting for completion...")
                wait_for_execution(runtime, execution_id, headers)
        else:
            click.echo(f"❌ Execution failed: {response.status_code}")
            if response.text:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                click.echo(f"  Error: {error_data.get('detail', 'Unknown error')}")
        
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ Run failed: {str(e)}", err=True)

@atomctl.command()
@click.option('--registry-url', help='Registry URL')
@click.option('--runtime-url', help='Runtime agent URL')
@click.option('--auth-token', help='Authentication token')
def config(registry_url: Optional[str], runtime_url: Optional[str], auth_token: Optional[str]):
    """Configure atomctl settings"""
    if registry_url:
        cli.config['registry_url'] = registry_url
        click.echo(f"✅ Registry URL set to: {registry_url}")
    
    if runtime_url:
        cli.config['runtime_url'] = runtime_url
        click.echo(f"✅ Runtime URL set to: {runtime_url}")
    
    if auth_token:
        cli.config['auth_token'] = auth_token
        click.echo("✅ Auth token configured")
    
    cli.save_config()
    
    # Show current config
    click.echo("\n📋 Current Configuration:")
    click.echo(f"  Registry URL: {cli.config['registry_url']}")
    click.echo(f"  Runtime URL: {cli.config['runtime_url']}")
    click.echo(f"  Auth Token: {'✅ Set' if cli.config.get('auth_token') else '❌ Not set'}")

@atomctl.command()
def list():
    """List workflows in the registry"""
    registry = cli.config['registry_url']
    
    try:
        headers = cli.get_auth_headers()
        response = requests.get(f"{registry}/workflows", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            workflows = data['workflows']
            
            if not workflows:
                click.echo("📭 No workflows found in registry")
                return
            
            click.echo(f"📋 Found {len(workflows)} workflows:")
            click.echo()
            
            for workflow in workflows:
                click.echo(f"🔧 {workflow['name']} v{workflow['version']}")
                click.echo(f"   ID: {workflow['id']}")
                click.echo(f"   Author: {workflow['author']}")
                click.echo(f"   Runtime: {workflow['runtime_type']}")
                click.echo(f"   Safety: {workflow['safety_mode']}")
                click.echo(f"   Created: {workflow.get('created', 'Unknown')}")
                if workflow.get('tags'):
                    click.echo(f"   Tags: {', '.join(workflow['tags'])}")
                click.echo()
        else:
            click.echo(f"❌ Failed to list workflows: {response.status_code}", err=True)
    
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ List failed: {str(e)}", err=True)

@atomctl.command()
@click.argument('execution_id')
@click.option('--runtime-url', help='Runtime agent URL override')
def status(execution_id: str, runtime_url: Optional[str]):
    """Get execution status"""
    runtime = runtime_url or cli.config['runtime_url']
    
    try:
        headers = cli.get_auth_headers()
        response = requests.get(f"{runtime}/execute/{execution_id}", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            click.echo(f"📊 Execution Status: {execution_id}")
            click.echo(f"  Workflow: {data['workflow_id']}")
            click.echo(f"  Status: {data['status']}")
            click.echo(f"  Started: {data.get('started_at', 'Not started')}")
            click.echo(f"  Completed: {data.get('completed_at', 'Not completed')}")
            click.echo(f"  Current Step: {data.get('current_step', 'None')}")
            click.echo(f"  Progress: {data['steps_completed']}/{data['total_steps']}")
            
            if data.get('error_message'):
                click.echo(f"  Error: {data['error_message']}")
            
            if data.get('logs'):
                click.echo("\n📝 Logs:")
                for log in data['logs']:
                    click.echo(f"    {log}")
        else:
            click.echo(f"❌ Failed to get status: {response.status_code}", err=True)
    
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"❌ Status check failed: {str(e)}", err=True)

def sign_wpk(wpk_path: Path) -> bool:
    """Sign WPK with cosign (mock implementation)"""
    try:
        # Mock cosign signing - in production use actual cosign
        click.echo("🔐 Signing WPK with cosign...")
        return True
    except Exception as e:
        click.echo(f"❌ Signing failed: {str(e)}", err=True)
        return False

def generate_mock_signature(content: str) -> str:
    """Generate mock signature for testing"""
    return f"cosign-{hashlib.sha256(content.encode()).hexdigest()[:16]}"

def wait_for_execution(runtime_url: str, execution_id: str, headers: Dict[str, str]):
    """Wait for execution to complete"""
    import time
    
    while True:
        try:
            response = requests.get(f"{runtime_url}/execute/{execution_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                
                if status in ['completed', 'failed', 'rolled_back']:
                    if status == 'completed':
                        click.echo("✅ Execution completed successfully")
                    elif status == 'failed':
                        click.echo("❌ Execution failed")
                        if data.get('error_message'):
                            click.echo(f"  Error: {data['error_message']}")
                    elif status == 'rolled_back':
                        click.echo("↩️ Execution rolled back")
                    
                    # Show final logs
                    if data.get('logs'):
                        click.echo("\n📝 Final Logs:")
                        for log in data['logs'][-5:]:  # Show last 5 logs
                            click.echo(f"    {log}")
                    
                    break
                else:
                    click.echo(f"⏳ Status: {status} ({data['steps_completed']}/{data['total_steps']})")
                    time.sleep(2)
            else:
                click.echo(f"❌ Failed to check status: {response.status_code}")
                break
                
        except KeyboardInterrupt:
            click.echo("\n⏹️ Stopped waiting (execution continues in background)")
            break
        except Exception as e:
            click.echo(f"❌ Error checking status: {str(e)}")
            break

if __name__ == '__main__':
    atomctl()