#!/bin/bash
set -e

cd /home/walland/Downloads/Video-Genius
echo "[$(date)] Starting deploy..." > deploy-run.log
timeout 3600 bash deploy.sh >> deploy-run.log 2>&1 &
DEPLOY_PID=$!
echo "[$(date)] Deploy PID: $DEPLOY_PID" >> deploy-run.log
wait $DEPLOY_PID
echo "[$(date)] Deploy completed!" >> deploy-run.log
