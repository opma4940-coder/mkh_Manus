#!/bin/bash
set -e

echo "Starting Smoke Tests for mkh_Manus..."

# Check Backend Health
echo "Testing Backend Root..."
curl -s -f http://localhost:8000/ || (echo "Backend root failed" && exit 1)

# Test Upload Request
echo "Testing Upload Request..."
curl -s -X POST http://localhost:8000/uploads/request \
     -H "Content-Type: application/json" \
     -d '{"filename": "test.txt", "content_type": "text/plain", "size": 1024}' || (echo "Upload request failed" && exit 1)

# Test Task Creation
echo "Testing Task Creation..."
curl -s -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Task", "payload": {"action": "test"}}' || (echo "Task creation failed" && exit 1)

# Test Agent Dispatch
echo "Testing Agent Dispatch..."
curl -s -X POST http://localhost:8000/agents/dispatch \
     -H "Content-Type: application/json" \
     -d '{"task_id": "test-task-id"}' || (echo "Agent dispatch failed" && exit 1)

# Test Task Replay (Dry Run)
echo "Testing Task Replay (Dry Run)..."
curl -s -X POST "http://localhost:8000/tasks/test-task-id/replay?dry_run=true" \
     -H "Content-Type: application/json" || (echo "Task replay failed" && exit 1)

echo "All Smoke Tests Passed Successfully!"
