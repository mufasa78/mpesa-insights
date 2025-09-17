#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p .streamlit

# Start the Streamlit app
exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false