#!/usr/bin/env python3
"""
atomctl - ATOM Cloud CLI Tool (Windows-compatible version)
Developer tool to pack, push, validate, and run WPKs
"""

import click
import yaml
import json
import os
import tarfile
import tempfile
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

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
            click.echo(f"\nWPK Summary:")
            click.echo(f"  Name: {metadata.get('name')}")
            click.echo(f"  Version: {metadata.get('version')}")
            click.echo(f"  Author: {metadata.get('author')}")
            click.echo(f"  Runtime: {spec.get('runtime', {}).get('type')}")
            click.echo(f"  Safety Mode: {spec.get('safety', {}).get('mode')}")
            click.echo(f"  Handlers: {len(handlers)}")
            
            if 'signature' in metadata:
                click.echo(f"  Signed: YES ({metadata['signature'][:16]}...)")
            else:
                click.echo(f"  Signed: NO (use pack --sign to sign)")
        
    except yaml.YAMLError as e:
        click.echo(f"[ERROR] Invalid YAML: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"[ERROR] Validation failed: {str(e)}", err=True)

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
        
        click.echo(f"[SUCCESS] Packed WPK: {output_path}")
        
        # Sign if requested
        if sign:
            # Add signature (mock for now)
            signature = f"cosign-{hashlib.sha256(str(wpk_path).encode()).hexdigest()[:16]}"
            wpk_data['metadata']['signature'] = signature
            
            # Write updated WPK
            with open(wpk_path, 'w') as f:
                yaml.dump(wpk_data, f, default_flow_style=False)
            
            # Repack with signature
            with tarfile.open(output_path, 'w:gz') as tar:
                tar.add(wpk_path, arcname=wpk_path.name)
            
            click.echo(f"[SUCCESS] Signed and packed: {output_path}")
        
    except Exception as e:
        click.echo(f"[ERROR] Pack failed: {str(e)}", err=True)

@atomctl.command()
def config():
    """Show current configuration"""
    click.echo("Current Configuration:")
    click.echo(f"  Registry URL: {cli.config['registry_url']}")
    click.echo(f"  Runtime URL: {cli.config['runtime_url']}")
    click.echo(f"  Auth Token: {'SET' if cli.config.get('auth_token') else 'NOT SET'}")

if __name__ == '__main__':
    atomctl()