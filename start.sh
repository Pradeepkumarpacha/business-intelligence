#!/bin/bash
# AI Business Intelligence Platform - Render Deployment Script
# Built by Pradeep Kumar Pacha

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting AI Business Intelligence Platform..."
streamlit run product_launch_intelligence_agent.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
