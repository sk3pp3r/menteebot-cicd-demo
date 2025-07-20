# Menteebot CI/CD Demo - Makefile
# Build automation and development tasks

.PHONY: help install test lint security-scan build run clean deploy-dev deploy-staging deploy-prod

# Default target
help:
	@echo "Menteebot CI/CD Demo - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        Install Python dependencies"
	@echo "  dev           Start development environment with Docker Compose"
	@echo "  test          Run tests with coverage"
	@echo "  lint          Run code linting and formatting"
	@echo "  security-scan Run security scanning"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build         Build Docker image"
	@echo "  run           Run application locally"
	@echo "  clean         Clean build artifacts"
	@echo "  deploy-dev    Deploy to development environment"
	@echo "  deploy-staging Deploy to staging environment"
	@echo "  deploy-prod   Deploy to production environment"
	@echo ""
	@echo "Infrastructure:"
	@echo "  terraform-init    Initialize Terraform"
	@echo "  terraform-plan    Plan Terraform changes"
	@echo "  terraform-apply   Apply Terraform changes"
	@echo "  terraform-destroy Destroy Terraform infrastructure"
	@echo ""
	@echo "Monitoring:"
	@echo "  monitoring    Start monitoring stack (Prometheus + Grafana)"
	@echo "  logs          View application logs"

# Variables
VERSION := $(shell cat version.txt)
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
DOCKER_IMAGE := menteebot-cicd-demo
DOCKER_TAG := $(VERSION)

# Python environment
PYTHON := python3
PIP := pip3

# Development
install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

dev:
	@echo "Starting development environment..."
	docker-compose -f docker/docker-compose.yml up --build

dev-proxy:
	@echo "Starting development environment with proxy..."
	docker-compose -f docker/docker-compose.yml --profile proxy up --build

monitoring:
	@echo "Starting monitoring stack..."
	docker-compose -f docker/docker-compose.yml --profile monitoring up --build

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running code linting..."
	black src/ tests/
	isort src/ tests/
	flake8 src/ tests/
	mypy src/

security-scan:
	@echo "Running security scan..."
	bandit -r src/
	safety check

# Build
build:
	@echo "Building Docker image..."
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VCS_REF=$(GIT_COMMIT) \
		-f docker/Dockerfile \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-t $(DOCKER_IMAGE):latest \
		.

run:
	@echo "Running application locally..."
	$(PYTHON) src/hello_world.py

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	docker system prune -f

# Deployment
deploy-dev:
	@echo "Deploying to development environment..."
	cd infrastructure/terraform/environments/dev && \
	terraform init && \
	terraform plan && \
	terraform apply -auto-approve

deploy-staging:
	@echo "Deploying to staging environment..."
	cd infrastructure/terraform/environments/staging && \
	terraform init && \
	terraform plan && \
	terraform apply -auto-approve

deploy-prod:
	@echo "Deploying to production environment..."
	cd infrastructure/terraform/environments/prod && \
	terraform init && \
	terraform plan && \
	terraform apply -auto-approve

# Infrastructure
terraform-init:
	@echo "Initializing Terraform..."
	cd infrastructure/terraform/environments/dev && terraform init

terraform-plan:
	@echo "Planning Terraform changes..."
	cd infrastructure/terraform/environments/dev && terraform plan

terraform-apply:
	@echo "Applying Terraform changes..."
	cd infrastructure/terraform/environments/dev && terraform apply

terraform-destroy:
	@echo "Destroying Terraform infrastructure..."
	cd infrastructure/terraform/environments/dev && terraform destroy

# Monitoring
logs:
	@echo "Viewing application logs..."
	docker-compose -f docker/docker-compose.yml logs -f app

# Version management
version-bump-patch:
	@echo "Bumping patch version..."
	$(eval NEW_VERSION := $(shell awk -F. '{print $$1"."$$2"."$$3+1}' version.txt))
	@echo $(NEW_VERSION) > version.txt
	@echo "Version bumped to $(NEW_VERSION)"

version-bump-minor:
	@echo "Bumping minor version..."
	$(eval NEW_VERSION := $(shell awk -F. '{print $$1"."$$2+1".0"}' version.txt))
	@echo $(NEW_VERSION) > version.txt
	@echo "Version bumped to $(NEW_VERSION)"

version-bump-major:
	@echo "Bumping major version..."
	$(eval NEW_VERSION := $(shell awk -F. '{print $$1+1".0.0"}' version.txt))
	@echo $(NEW_VERSION) > version.txt
	@echo "Version bumped to $(NEW_VERSION)"

# Docker registry operations
docker-login:
	@echo "Logging into Docker registry..."
	aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.eu-north-1.amazonaws.com

docker-push:
	@echo "Pushing Docker image to registry..."
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.eu-north-1.amazonaws.com/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.eu-north-1.amazonaws.com/$(DOCKER_IMAGE):latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.eu-north-1.amazonaws.com/$(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.eu-north-1.amazonaws.com/$(DOCKER_IMAGE):latest

# CI/CD pipeline helpers
ci-build:
	@echo "CI build process..."
	make install
	make lint
	make security-scan
	make test
	make build

ci-deploy:
	@echo "CI deploy process..."
	make docker-login
	make docker-push
	make deploy-dev 