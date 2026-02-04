# Paper Reading Agent

An intelligent open-source agent that helps you read, analyze, and interact with academic papers using AI.

## Features

- **PDF Upload & Analysis**: Upload academic papers via file or arXiv URL
- **Smart Summary**: Automatic paper summarization using Google Gemini 3.0 Flash
- **Interactive Chat**: Ask questions and discuss paper content with AI
- **On-Demand Figure Extraction**: Extracts figures/diagrams only when needed for efficient processing
- **Session Persistence**: Maintains conversation history and extracted images across sessions
- **Multilingual Support**: English, Chinese, Spanish, French, and more
- **Beautiful UI**: Modern, responsive React frontend with LaTeX math rendering (KaTeX)

## Tech Stack

### Backend
- **Framework**: Flask (Python 3.8+)
- **AI Model**: Google Gemini 3.0 Flash (gemini-3-flash-preview)
- **PDF Processing**: PyMuPDF (fitz), PyPDF2
- **Database**: SQLite with conversation history
- **Image Processing**: Pillow (PIL)

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: CSS3 with modern animations
- **Math Rendering**: KaTeX for LaTeX equations
- **HTTP Client**: Native fetch API

## Architecture

The agent uses a **conversational design** with on-demand figure extraction:

1. **Upload Phase**: PDF uploaded to Gemini File API
2. **Initial Analysis**: Generates paper summary automatically
3. **Chat Phase**: User asks questions, agent extracts figures only when needed
4. **Function Calling**: LLM decides which figures to extract/display using built-in tools

## Prerequisites

- Python 3.12 or higher
- Node.js 14 or higher
- Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

## Installation & Setup

### 🚀 Quick Start (One-Click Setup)

**The easiest way to get started:**

1. **Get your Gemini API key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. **Create `.env` file** in the `backend/` folder:
   ```bash
   cd backend
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. **Run the startup script:**

   **Mac/Linux:**
   ```bash
   cd ../
   ./start.sh
   ```

   **Windows:**
   ```bash
   cd ../
   start.bat
   ```

That's it! The script will:
- ✅ Check all prerequisites (Python, Node.js)
- ✅ Install backend and frontend dependencies
- ✅ Start both servers automatically
- ✅ Open the application in your browser

---

### 📋 Manual Setup (Alternative)

If you prefer manual setup or the startup script doesn't work:

#### 1. Clone the Repository

```bash
git clone https://github.com/HaoliangCheng/paper-reading-agent.git
cd paper-reading-agent
```

#### 2. Backend Setup

#### Option A: Using UV (Recommended - Faster)

```bash
cd backend

# Install uv if you haven't already
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Initialize project and install dependencies (one time)
uv sync

# If uv sync fails, use this simpler alternative:
# uv venv && uv pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Run the server (no activation needed!)
uv run python app.py
```

**Why no `source .venv/bin/activate`?**
- `uv run` automatically uses the project's virtual environment
- No manual activation needed - UV handles it for you
- Much cleaner workflow!

#### Option B: Using pip (Traditional)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Run the server
python app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will open at `http://localhost:3000`

## Project Structure

```
paper-reading-agent/
├── backend/
│   ├── app.py                          # Flask API server
│   ├── database.py                     # SQLite database operations
│   ├── pyproject.toml                  # Python project config (uv)
│   ├── requirements.txt                # Python dependencies (pip fallback)
│   ├── .python-version                 # Python version (3.12)
│   ├── agents/
│   │   └── conversational/
│   │       ├── agent.py                # Conversational agent (Design 4)
│   │       ├── image_extractor.py      # On-demand figure extraction
│   │       ├── prompts.py              # LLM system prompts
│   │       └── tools.py                # Function declarations
│   ├── providers/
│   │   ├── base.py                     # Provider interfaces
│   │   ├── gemini_provider.py          # Gemini API wrapper
│   │   └── pdf_provider.py             # PDF processing utilities
│   ├── models/
│   │   ├── paper.py                    # Paper data models
│   │   └── session.py                  # Session data models
│   └── uploads/                        # Uploaded PDFs and extracted figures
├── frontend/
│   ├── src/
│   │   ├── App.tsx                     # Main application component
│   │   ├── App.css                     # Styles and animations
│   │   └── index.tsx                   # React entry point
│   ├── public/
│   │   └── index.html                  # HTML template with KaTeX CDN
│   └── package.json                    # Node dependencies
└── README.md
```

## API Endpoints

- `POST /api/analyze` - Upload and analyze a paper
- `POST /api/chat` - Send a message in conversation
- `GET /api/papers` - Get all analyzed papers
- `GET /api/papers/<id>/messages` - Get conversation history
- `DELETE /api/papers/<id>` - Delete a paper
- `POST /api/explain-figure` - Get detailed figure explanation
- `GET /uploads/<path>` - Serve uploaded files and images
- `GET /health` - Health check


## Environment Variables

Create `backend/.env` with:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
