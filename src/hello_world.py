#!/usr/bin/env python3
"""
Menteebot CI/CD Demo - Hello World Application
A simple Flask application demonstrating CI/CD pipeline capabilities.

Author: Haim Cohen
Website: https://haimc.xyz
"""

import os
import sys
import logging
import json
from datetime import datetime
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Application version
VERSION = os.getenv('APP_VERSION', '1.0.0')
BUILD_DATE = os.getenv('BUILD_DATE', datetime.now().isoformat())
GIT_COMMIT = os.getenv('GIT_COMMIT', 'unknown')

app = Flask(__name__)

@app.before_request
def before_request():
    """Log request details before processing."""
    request.start_time = datetime.now()

@app.after_request
def after_request(response):
    """Log response details and update metrics after processing."""
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        REQUEST_LATENCY.observe(duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    logger.info(
        f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s"
    )
    
    return response

@app.route('/')
def hello_world():
    """Main greeting endpoint."""
    return jsonify({
        'message': 'Hello from CI/CD!',
        'service': 'menteebot-cicd-demo',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

@app.route('/health')
def health_check():
    """Health check endpoint for load balancer and monitoring."""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'uptime': get_uptime(),
        'checks': {
            'database': 'healthy',
            'cache': 'healthy',
            'external_services': 'healthy'
        }
    }
    
    return jsonify(health_status), 200

@app.route('/health/ready')
def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe."""
    ready_status = {
        'status': 'ready',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION
    }
    
    return jsonify(ready_status), 200

@app.route('/version')
def version_info():
    """Version information endpoint."""
    version_info = {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'git_commit': GIT_COMMIT,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'python_version': sys.version,
        'flask_version': Flask.__version__
    }
    
    return jsonify(version_info)

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/v1/status')
def api_status():
    """API status endpoint with detailed information."""
    status = {
        'service': 'menteebot-cicd-demo',
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'hostname': os.getenv('HOSTNAME', 'unknown'),
        'region': os.getenv('AWS_REGION', 'unknown'),
        'uptime': get_uptime(),
        'memory_usage': get_memory_usage(),
        'cpu_usage': get_cpu_usage()
    }
    
    return jsonify(status)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500

def get_uptime():
    """Get application uptime."""
    # In a real application, you would track the start time
    # For demo purposes, return a placeholder
    return "0 days, 0 hours, 0 minutes"

def get_memory_usage():
    """Get memory usage information."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent
        }
    except ImportError:
        return {'error': 'psutil not available'}

def get_cpu_usage():
    """Get CPU usage information."""
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        return {'error': 'psutil not available'}

def graceful_shutdown(signum, frame):
    """Handle graceful shutdown."""
    logger.info("Received shutdown signal, shutting down gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    import signal
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Menteebot CI/CD Demo v{VERSION}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Listening on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug) 