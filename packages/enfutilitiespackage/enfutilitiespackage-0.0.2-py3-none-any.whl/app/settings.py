"""
Settings Module
"""
import os

GCP_PROJECT_REGION = os.environ.get("GCP_PROJECT_REGION")
GCP_PROJECT = os.environ.get("GCP_PROJECT")
SERVICE_NAME = os.environ.get("SERVICE_NAME") or os.environ.get("K_SERVICE")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
ENABLE_TRACES = bool(os.environ.get("ENABLE_TRACES", False))
