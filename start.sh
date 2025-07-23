#!/bin/bash
pip install -r requirements.txt
streamlit run product_launch_intelligence_agent.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
