#!/bin/sh


cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8000 &


cd /app/frontend && streamlit run app.py --server.port=7860 --server.address=0.0.0.0

