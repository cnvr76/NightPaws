#!/bin/bash

MODEL_DIR="/app/training_data/my_email_classifier"
LOCAL_VERSION_FILE="$MODEL_DIR/version.txt"

GDRIVE_ID="${GDRIVE_FILE_ID}"
VERSION_URL="${REMOTE_VERSION_URL}"

LOCAL_VERSION=$(cat "$LOCAL_VERSION_FILE" 2>/dev/null || echo "0")
REMOTE_VERSION=$(curl -sL "$VERSION_URL")

if [ "$REMOTE_VERSION" != "$LOCAL_VERSION" ]; then
    echo "New model version detected: $REMOTE_VERSION. Downloading..."
    mkdir -p "$MODEL_DIR"
    
    gdown --id "$GDRIVE_ID" -O "$MODEL_DIR/model.zip"
    
    unzip -o "$MODEL_DIR/model.zip" -d "$MODEL_DIR"
    
    echo "$REMOTE_VERSION" > "$LOCAL_VERSION_FILE"
    rm "$MODEL_DIR/model.zip"
    echo "Model updated successfully."
else
    echo "Model is up to date (v$LOCAL_VERSION)."
fi

if [ $# -gt 0 ]; then
    exec "$@"
else
    exec uvicorn app:app --host 0.0.0.0 --port 8000
fi