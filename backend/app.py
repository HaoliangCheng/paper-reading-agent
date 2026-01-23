from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import requests
import shutil
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Silence noisy HTTP loggers
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
import json
import re
from database import (
    init_database, save_paper, get_all_papers, get_paper_by_id,
    delete_paper, save_message, get_messages_by_paper,
    save_reading_session, get_reading_session
)
from agents import ConversationalPaperAgent
from providers import GeminiProvider
from dotenv import load_dotenv

# Ensure .env is loaded
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize providers
llm_provider = GeminiProvider()

# In-memory storage for active reading sessions
# Key: paper_id, Value: {agent, file, language, paper_folder}
reading_sessions = {}

# Initialize database
init_database()


def _parse_step1_response(response_text: str, fallback_title: str) -> tuple:
    """
    Parse Step 1 response to extract title and summary.
    Step 1 should return JSON with 'title' and 'summary' fields.

    Args:
        response_text: Raw response from Step 1
        fallback_title: Fallback title (usually filename) if parsing fails

    Returns:
        Tuple of (title, summary)
    """
    try:
        # Try to extract JSON from response
        text = response_text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        # Try to find JSON object in the text
        json_match = re.search(r'\{[^{}]*"title"[^{}]*"summary"[^{}]*\}|\{[^{}]*"summary"[^{}]*"title"[^{}]*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group()

        data = json.loads(text)
        title = data.get('title', '').strip() or fallback_title
        summary = data.get('summary', response_text).strip()

        return title, summary

    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"Could not parse Step 1 JSON: {e}")
        # Return the whole response as summary and use fallback title
        return fallback_title, response_text


@app.route('/api/analyze', methods=['POST'])
def analyze_paper():
    """
    Handle PDF upload and run Step 1 using ConversationalPaperAgent (Design 4).

    Design 4: No upfront figure extraction - images extracted on-demand.
    Returns Step 1 content and stores the agent session for subsequent chat.
    """
    try:
        language = request.form.get('language', 'English')
        file_path = None
        original_filename = None
        paper_id = str(int(time.time() * 1000))

        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                original_filename = secure_filename(file.filename)
                # Create folder for this paper: paper_id_filename
                folder_name = f"{paper_id}_{os.path.splitext(original_filename)[0]}"
                paper_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                os.makedirs(paper_folder, exist_ok=True)

                file_path = os.path.join(paper_folder, original_filename)
                file.save(file_path)

        elif 'url' in request.form:
            url = request.form.get('url')
            if url:
                if 'arxiv.org/abs/' in url:
                    url = url.replace('arxiv.org/abs/', 'arxiv.org/pdf/')
                if 'arxiv.org/pdf/' in url and not url.endswith('.pdf'):
                    url = url + '.pdf'

                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()

                original_filename = url.split('/')[-1] or "paper.pdf"
                if not original_filename.endswith('.pdf'):
                    original_filename += ".pdf"
                original_filename = secure_filename(original_filename)

                # Create folder for this paper
                folder_name = f"{paper_id}_{os.path.splitext(original_filename)[0]}"
                paper_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                os.makedirs(paper_folder, exist_ok=True)

                file_path = os.path.join(paper_folder, original_filename)

                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

        if not file_path:
            return jsonify({'error': 'No PDF file or URL provided'}), 400

        # Upload PDF to Gemini
        logger.info("Uploading PDF to Gemini...")
        gemini_file = llm_provider.upload_file(file_path)

        # Create ConversationalPaperAgent
        agent = ConversationalPaperAgent(
            llm_provider=llm_provider,
            file=gemini_file,
            pdf_path=file_path,
            paper_folder=paper_folder,
            language=language
        )

        # Start session and generate initial summary
        step1_content = agent.start_session()

        # Parse title and summary from response
        paper_title, step1_summary = _parse_step1_response(step1_content, original_filename)
        logger.info(f"Paper analyzed: {paper_title}")

        # Store reading session for subsequent chat
        reading_sessions[paper_id] = {
            'agent': agent,
            'file': gemini_file,
            'language': language,
            'paper_folder': paper_folder,
            'pdf_path': file_path
        }

        # Save session state to database for persistence across restarts
        save_reading_session(paper_id, agent.get_extracted_images())

        # Save to database
        paper_data = {
            'id': paper_id,
            'title': paper_title,
            'file_path': file_path,
            'gemini_file_name': gemini_file.name,
            'language': language,
            'summary': step1_summary
        }
        save_paper(paper_data)

        # Save initial summary as the first AI message
        save_message({
            'id': f"ai-{paper_id}-initial",
            'paper_id': paper_id,
            'text': step1_summary,
            'is_user': False
        })

        return jsonify({
            'id': paper_id,
            'title': paper_title,
            'content': step1_summary,
            'extracted_images': agent.get_extracted_images()
        })

    except Exception as e:
        logger.error(f"Error in analyze_paper: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat using ConversationalPaperAgent.

    Returns the response along with extracted images information.
    """
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        message = data.get('message')
        language = data.get('language', 'English')

        paper = get_paper_by_id(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        # Save user message
        save_message({
            'id': f"user-{int(time.time() * 1000)}",
            'paper_id': paper_id,
            'text': message,
            'is_user': True
        })

        # Check if we have an active session
        if paper_id not in reading_sessions:
            # Try to recreate session if paper exists in database
            if paper.get('gemini_file_name') and paper.get('file_path'):
                try:
                    # Recreate the session
                    gemini_file = llm_provider.get_file(paper['gemini_file_name'])
                    file_path = paper['file_path']
                    paper_folder = os.path.dirname(file_path)

                    # Load saved session state from database
                    saved_session = get_reading_session(paper_id)
                    restored_images = saved_session.get('extracted_images', []) if saved_session else []

                    # Load conversation history from messages
                    messages = get_messages_by_paper(paper_id)
                    restored_history = []
                    for msg in messages:
                        restored_history.append({
                            'role': 'user' if msg['isUser'] else 'assistant',
                            'content': msg['text']
                        })

                    logger.info(f"Restoring session: {len(restored_history)} msgs, {len(restored_images)} images")

                    # Create new agent with restored state
                    agent = ConversationalPaperAgent(
                        llm_provider=llm_provider,
                        file=gemini_file,
                        pdf_path=file_path,
                        paper_folder=paper_folder,
                        language=paper.get('language', language),
                        restored_images=restored_images if restored_images else None,
                        restored_history=restored_history if restored_history else None
                    )

                    # Start session (will restore context if available)
                    agent.start_session()

                    # Store session
                    reading_sessions[paper_id] = {
                        'agent': agent,
                        'file': gemini_file,
                        'language': paper.get('language', language),
                        'paper_folder': paper_folder,
                        'pdf_path': file_path
                    }

                except Exception as e:
                    logger.error(f"Failed to recreate session: {e}", exc_info=True)
                    return jsonify({
                        'error': 'Reading session expired. Please re-upload the paper.'
                    }), 404
            else:
                return jsonify({
                    'error': 'Reading session not found. Please re-upload the paper.'
                }), 404

        # Get agent and send message
        session = reading_sessions[paper_id]
        agent = session['agent']

        response_text = agent.send_message(message)

        # Save AI response
        save_message({
            'id': f"ai-{int(time.time() * 1000)}",
            'paper_id': paper_id,
            'text': response_text,
            'is_user': False
        })

        # Update session state in database (persist extracted images)
        save_reading_session(paper_id, agent.get_extracted_images())

        return jsonify({
            'response': response_text,
            'extracted_images': agent.get_extracted_images()
        })

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/papers', methods=['GET'])
def get_papers():
    return jsonify({'papers': get_all_papers()})


@app.route('/api/papers/<paper_id>/messages', methods=['GET'])
def get_paper_messages(paper_id):
    return jsonify({'messages': get_messages_by_paper(paper_id)})


@app.route('/api/papers/<paper_id>', methods=['DELETE'])
def delete_paper_endpoint(paper_id):
    """Delete paper, its folder, and reading session"""
    # Clean up reading session
    if paper_id in reading_sessions:
        del reading_sessions[paper_id]

    paper = get_paper_by_id(paper_id)
    if paper and paper.get('file_path'):
        # Get the paper folder (parent directory of the PDF)
        paper_folder = os.path.dirname(paper['file_path'])
        if os.path.exists(paper_folder) and paper_folder.startswith(app.config['UPLOAD_FOLDER']):
            try:
                shutil.rmtree(paper_folder)
            except Exception as e:
                logger.error(f"Error deleting folder: {e}")
    delete_paper(paper_id)
    return jsonify({'message': 'Deleted'})


@app.route('/api/explain-figure', methods=['POST'])
def explain_figure():
    """
    Explain a figure/image based on user's question.

    Request JSON:
        - image_path: Path to the image (relative to uploads folder or absolute)
        - question: User's question about the image
        - language: (optional) Language for the response, defaults to 'English'

    Returns:
        JSON with 'response' containing the explanation
    """
    try:
        data = request.get_json()
        image_path = data.get('image_path')
        question = data.get('question')
        language = data.get('language', 'English')

        if not image_path:
            return jsonify({'error': 'image_path is required'}), 400
        if not question:
            return jsonify({'error': 'question is required'}), 400

        # Handle relative paths (from uploads folder)
        if not os.path.isabs(image_path):
            # Check if path starts with 'uploads/'
            if image_path.startswith('uploads/'):
                image_path = os.path.join(basedir, image_path)
            else:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)

        # Verify file exists
        if not os.path.exists(image_path):
            return jsonify({'error': f'Image not found: {image_path}'}), 404

        # Call LLM to explain the figure
        response_text = llm_provider.explain_figure(image_path, question, language)

        return jsonify({'response': response_text})

    except Exception as e:
        logger.error(f"Error in explain_figure: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """Serve uploaded files (PDFs and images) from paper folders"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
