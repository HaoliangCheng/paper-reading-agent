#!/bin/bash

# Paper Reading Agent - One-Click Startup Script
# This script sets up and runs both backend and frontend servers

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Paper Reading Agent - Startup Script${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}✗ Python 3 is not installed. Please install Python 3.12+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

if ! command_exists node; then
    echo -e "${RED}✗ Node.js is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

if ! command_exists npm; then
    echo -e "${RED}✗ npm is not installed. Please install npm${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm $NPM_VERSION found${NC}\n"

# Step 2: Check environment file
echo -e "${YELLOW}[2/6] Checking environment configuration...${NC}"

if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}✗ Backend .env file not found!${NC}"
    echo -e "${YELLOW}Creating template .env file...${NC}"
    cat > "$BACKEND_DIR/.env" << EOF
# Google Gemini API Key
# Get your API key from: https://ai.google.dev/
GOOGLE_API_KEY=your_api_key_here
EOF
    echo -e "${RED}✗ Please edit backend/.env and add your GOOGLE_API_KEY${NC}"
    echo -e "${YELLOW}  Get your API key from: https://ai.google.dev/${NC}"
    exit 1
fi

# Check if API key is set
if grep -q "your_api_key_here" "$BACKEND_DIR/.env"; then
    echo -e "${RED}✗ Please set your GOOGLE_API_KEY in backend/.env${NC}"
    echo -e "${YELLOW}  Get your API key from: https://ai.google.dev/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment file configured${NC}\n"

# Step 3: Install backend dependencies
echo -e "${YELLOW}[3/6] Installing backend dependencies...${NC}"
cd "$BACKEND_DIR"

# Check if uv is available, otherwise use pip
if command_exists uv; then
    echo -e "${BLUE}Using uv for backend dependencies...${NC}"
    uv sync --quiet || {
        echo -e "${RED}✗ Failed to install backend dependencies with uv${NC}"
        exit 1
    }
else
    echo -e "${BLUE}Using pip for backend dependencies...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -q -r requirements.txt || {
        echo -e "${RED}✗ Failed to install backend dependencies${NC}"
        exit 1
    }
fi

echo -e "${GREEN}✓ Backend dependencies installed${NC}\n"

# Step 4: Install frontend dependencies
echo -e "${YELLOW}[4/6] Installing frontend dependencies...${NC}"
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    npm install --silent || {
        echo -e "${RED}✗ Failed to install frontend dependencies${NC}"
        exit 1
    }
else
    echo -e "${BLUE}Frontend dependencies already installed${NC}"
fi

echo -e "${GREEN}✓ Frontend dependencies ready${NC}\n"

# Step 5: Check if ports are available
echo -e "${YELLOW}[5/6] Checking ports...${NC}"

if port_in_use 5000; then
    echo -e "${YELLOW}⚠ Port 5000 is already in use (backend)${NC}"
    echo -e "${YELLOW}  Kill the process or use a different port${NC}"
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠ Port 3000 is already in use (frontend)${NC}"
    echo -e "${YELLOW}  Kill the process or use a different port${NC}"
fi

echo -e "${GREEN}✓ Port check complete${NC}\n"

# Step 6: Start servers
echo -e "${YELLOW}[6/6] Starting servers...${NC}\n"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Servers stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
cd "$BACKEND_DIR"
echo -e "${BLUE}Starting Flask backend on http://localhost:5000${NC}"
if command_exists uv; then
    uv run python app.py > backend.log 2>&1 &
else
    source venv/bin/activate
    python app.py > backend.log 2>&1 &
fi
BACKEND_PID=$!

# Wait for backend to start
sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Backend failed to start. Check backend/backend.log for details${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Start frontend
cd "$FRONTEND_DIR"
echo -e "${BLUE}Starting React frontend on http://localhost:3000${NC}"
BROWSER=none npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}✗ Frontend failed to start. Check frontend/frontend.log for details${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}\n"

# Success message
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   ✓ Paper Reading Agent is running!${NC}"
echo -e "${GREEN}================================================${NC}\n"
echo -e "${BLUE}Backend:${NC}  http://localhost:5000"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}\n"

# Open browser
if command_exists open; then
    sleep 2
    open http://localhost:3000
elif command_exists xdg-open; then
    sleep 2
    xdg-open http://localhost:3000
fi

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
