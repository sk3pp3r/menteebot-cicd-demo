#!/usr/bin/env python3
"""
Unit tests for the hello_world application.
"""

import pytest
import json
from src.hello_world import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_hello_world_endpoint(client):
    """Test the main hello world endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'Hello from CI/CD!'
    assert 'service' in data
    assert data['service'] == 'menteebot-cicd-demo'
    assert 'timestamp' in data
    assert 'version' in data


def test_health_check_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data
    assert 'checks' in data


def test_readiness_check_endpoint(client):
    """Test the readiness check endpoint."""
    response = client.get('/health/ready')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'ready'
    assert 'timestamp' in data
    assert 'version' in data


def test_version_endpoint(client):
    """Test the version information endpoint."""
    response = client.get('/version')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'version' in data
    assert 'build_date' in data
    assert 'git_commit' in data
    assert 'environment' in data
    assert 'python_version' in data
    assert 'flask_version' in data


def test_api_status_endpoint(client):
    """Test the API status endpoint."""
    response = client.get('/api/v1/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'service' in data
    assert data['service'] == 'menteebot-cicd-demo'
    assert 'status' in data
    assert data['status'] == 'operational'
    assert 'timestamp' in data
    assert 'version' in data


def test_metrics_endpoint(client):
    """Test the Prometheus metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'http_requests_total' in response.data.decode()


def test_404_error_handler(client):
    """Test the 404 error handler."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Not Found'
    assert 'message' in data
    assert 'timestamp' in data


def test_environment_variables():
    """Test that environment variables are properly set."""
    import os
    from src.hello_world import VERSION, BUILD_DATE, GIT_COMMIT
    
    assert VERSION is not None
    assert BUILD_DATE is not None
    assert GIT_COMMIT is not None 