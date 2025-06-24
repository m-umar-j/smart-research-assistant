#!/bin/sh


cd /app && uvicorn backend.main:app --host 0.0.0.0 --port 8000 &


cd /app && streamlit run frontend/app.py --server.port=7860 --server.address=0.0.0.0

