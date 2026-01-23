import sqlite3
import json
from datetime import datetime

DATABASE_FILE = 'paper_agent.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create papers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            gemini_file_name TEXT,
            language TEXT NOT NULL,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            paper_id TEXT NOT NULL,
            text TEXT NOT NULL,
            is_user BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (id)
        )
    ''')

    # Create reading_sessions table to persist agent state
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reading_sessions (
            paper_id TEXT PRIMARY KEY,
            extracted_images TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES papers (id)
        )
    ''')

    conn.commit()
    conn.close()

def save_paper(paper_data):
    """Save a paper to the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO papers 
        (id, title, file_path, gemini_file_name, language, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        paper_data['id'],
        paper_data['title'],
        paper_data['file_path'],
        paper_data.get('gemini_file_name', ''),
        paper_data['language'],
        paper_data['summary'],
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def get_all_papers():
    """Retrieve all papers from the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, file_path, gemini_file_name, language, summary, created_at
        FROM papers 
        ORDER BY created_at DESC
    ''')
    
    papers = []
    for row in cursor.fetchall():
        papers.append({
            'id': row[0],
            'title': row[1],
            'file_path': row[2],
            'gemini_file_name': row[3],
            'language': row[4],
            'summary': row[5],
            'timestamp': row[6]
        })
    
    conn.close()
    return papers

def get_paper_by_id(paper_id):
    """Retrieve a specific paper by ID"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, file_path, gemini_file_name, language, summary, created_at
        FROM papers 
        WHERE id = ?
    ''', (paper_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'title': row[1],
            'file_path': row[2],
            'gemini_file_name': row[3],
            'language': row[4],
            'summary': row[5],
            'timestamp': row[6]
        }
    return None

def delete_paper(paper_id):
    """Delete a paper, its messages, and reading session"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Delete reading session first
    cursor.execute('DELETE FROM reading_sessions WHERE paper_id = ?', (paper_id,))
    # Delete messages
    cursor.execute('DELETE FROM messages WHERE paper_id = ?', (paper_id,))
    # Delete paper
    cursor.execute('DELETE FROM papers WHERE id = ?', (paper_id,))

    conn.commit()
    conn.close()

def save_message(message_data):
    """Save a message to the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (id, paper_id, text, is_user, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        message_data['id'],
        message_data['paper_id'],
        message_data['text'],
        message_data['is_user'],
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()

def get_messages_by_paper(paper_id):
    """Retrieve all messages for a specific paper"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, text, is_user, created_at
        FROM messages
        WHERE paper_id = ?
        ORDER BY created_at ASC
    ''', (paper_id,))

    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'text': row[1],
            'isUser': bool(row[2]),
            'timestamp': row[3]
        })

    conn.close()
    return messages


def save_reading_session(paper_id, extracted_images):
    """Save or update reading session state"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO reading_sessions (paper_id, extracted_images, updated_at)
        VALUES (?, ?, ?)
    ''', (
        paper_id,
        json.dumps(extracted_images),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_reading_session(paper_id):
    """Retrieve reading session state for a paper"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT extracted_images, updated_at
        FROM reading_sessions
        WHERE paper_id = ?
    ''', (paper_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'extracted_images': json.loads(row[0]) if row[0] else [],
            'updated_at': row[1]
        }
    return None


def delete_reading_session(paper_id):
    """Delete reading session for a paper"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM reading_sessions WHERE paper_id = ?', (paper_id,))

    conn.commit()
    conn.close()
