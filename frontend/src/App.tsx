import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import 'katex/dist/katex.min.css';
import './App.css';

// Extend window interface for renderMathInElement and highlight.js
declare global {
  interface Window {
    renderMathInElement?: (element: HTMLElement, options?: any) => void;
    hljs?: any;
    copyCode?: (button: HTMLButtonElement) => void;
  }
}

// Global function for copying code (to be used by copy buttons in generated HTML)
window.copyCode = (button: HTMLButtonElement) => {
  const code = button.getAttribute('data-code');
  if (!code) return;

  // Decode HTML entities back to original characters
  const decodedCode = code
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#10;/g, '\n')
    .replace(/&#13;/g, '\r')
    .replace(/&#9;/g, '\t');

  navigator.clipboard.writeText(decodedCode).then(() => {
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.classList.add('copied');
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove('copied');
    }, 2000);
  }).catch(err => {
    console.error('Failed to copy code: ', err);
  });
};

// Ensure marked is configured to parse images
marked.setOptions({
  breaks: true,
  gfm: true, // GitHub Flavored Markdown
});

interface Paper {
  id: string;
  title: string;
  file_path: string;
  language: string;
  timestamp: string;
  summary?: string;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

const App: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [paperUrl, setPaperUrl] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [paperToDelete, setPaperToDelete] = useState<Paper | null>(null);
  const [uploadTab, setUploadTab] = useState<'file' | 'link'>('file');
  const [isTyping, setIsTyping] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  const triggerFileInput = () => {
    if (!isLoading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const languages = ['English', '中文'];

  // Helper function to decode HTML entities (like jQuery's .html().text())
  const decodeHTMLEntities = (text: string): string => {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = text;
    return textarea.value;
  };

  const processCodeBlocks = (htmlContent: string): string => {
    // Process <pre><code class="language-xyz"> blocks
    let processed = htmlContent.replace(
      /<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
      (match, language, code) => {
        // Decode all HTML entities properly using DOM method (equivalent to jQuery's .html().text())
        const decodedCode = decodeHTMLEntities(code);
          
        let highlighted = code;
        if (window.hljs) {
          try {
            highlighted = window.hljs.highlight(decodedCode, { language }).value;
          } catch (e) {
            console.error('Highlight error:', e);
          }
        }

        // Escape code for data attribute to preserve it for copying
        const escapedCode = decodedCode
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;')
          .replace(/\n/g, '&#10;')
          .replace(/\r/g, '&#13;')
          .replace(/\t/g, '&#9;');

        return `
          <div class="code-block-container">
            <div class="code-block-header">
              <span class="code-language">${language}</span>
              <button class="copy-button" data-code="${escapedCode}">Copy</button>
            </div>
            <div class="code-block-content">
              <pre><code class="hljs ${language}">${highlighted}</code></pre>
            </div>
          </div>
        `;
      }
    );

    // Process <pre><code> blocks without language
    processed = processed.replace(
      /<pre><code>([\s\S]*?)<\/code><\/pre>/g,
      (match, code) => {
        // Decode all HTML entities properly using DOM method
        const decodedCode = decodeHTMLEntities(code);

        // Escape code for data attribute to preserve it for copying
        const escapedCode = decodedCode
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;')
          .replace(/\n/g, '&#10;')
          .replace(/\r/g, '&#13;')
          .replace(/\t/g, '&#9;');

        return `
          <div class="code-block-container">
            <div class="code-block-header">
              <span class="code-language">code</span>
              <button class="copy-button" data-code="${escapedCode}">Copy</button>
            </div>
            <div class="code-block-content">
              <pre><code>${decodedCode}</code></pre>
            </div>
          </div>
        `;
      }
    );

    return processed;
  };

  const convertMarkdownToHtml = (markdown: string): string => {
    try {
      // Pre-process markdown for KaTeX as per reference example
      let processedMarkdown = markdown.replace(/\\/g, '\\\\');
      
      processedMarkdown = processedMarkdown.replace(
        /!\[([^\]]*)\]\(([^)]+\.(png|jpg|jpeg|gif|svg))\)/gi,
        (match, altText, imagePath) => {
          // ... existing image handling ...
          if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
            return match;
          }
          const uploadsIndex = imagePath.indexOf('uploads/');
          if (uploadsIndex !== -1) {
            const relativePath = imagePath.substring(uploadsIndex + 8);
            const newUrl = `http://localhost:5000/uploads/${relativePath}`;
            return `![${altText}](${newUrl})`;
          }
          const newUrl = `http://localhost:5000/uploads/${imagePath}`;
          return `![${altText}](${newUrl})`;
        }
      );
      
      // Now parse the processed markdown to HTML
      const result = marked.parse(processedMarkdown);
      let htmlContent = typeof result === 'string' ? result : '';
      
      // Clean up markdown interference with math (like underscores becoming <em>)
      // and handle display issues as per reference example
      htmlContent = htmlContent
        .replace(/<em>/g, '_')
        .replace(/<\/em>/g, '_')
        .replace(/<strong><strong>/g, '<strong>')
        .replace(/<\/strong><\/strong>/g, '</strong>');
      
      // Process code blocks for syntax highlighting and copy button
      htmlContent = processCodeBlocks(htmlContent);

      // Sanitize and return
      return DOMPurify.sanitize(htmlContent, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 's', 'a', 'img', 'code', 'pre', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'button'],
        ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id', 'data-code']
      });
    } catch (error) {
      console.error('Error parsing markdown:', error);
      return markdown;
    }
  };

  const loadPapers = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/papers');
      const data = await response.json();
      if (response.ok) {
        setPapers(data.papers);
      }
    } catch (error) {
      console.error('Error loading papers:', error);
    }
  };

  const loadMessages = async (paperId: string) => {
    try {
      const response = await fetch(`http://localhost:5000/api/papers/${paperId}/messages`);
      const data = await response.json();
      if (response.ok) {
        return data.messages;
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    }
    return [];
  };

  useEffect(() => {
    loadPapers();
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('theme');
    const lightTheme = document.getElementById('highlight-light') as HTMLLinkElement;
    const darkTheme = document.getElementById('highlight-dark') as HTMLLinkElement;
    
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark-mode');
      if (lightTheme) lightTheme.disabled = true;
      if (darkTheme) darkTheme.disabled = false;
    }
  }, []);

  // Toggle theme
  const toggleTheme = () => {
    setIsDarkMode(prev => {
      const newMode = !prev;
      const lightTheme = document.getElementById('highlight-light') as HTMLLinkElement;
      const darkTheme = document.getElementById('highlight-dark') as HTMLLinkElement;
      
      if (newMode) {
        document.documentElement.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        if (lightTheme) lightTheme.disabled = true;
        if (darkTheme) darkTheme.disabled = false;
      } else {
        document.documentElement.classList.remove('dark-mode');
        localStorage.setItem('theme', 'light');
        if (lightTheme) lightTheme.disabled = false;
        if (darkTheme) darkTheme.disabled = true;
      }
      return newMode;
    });
  };

  // Auto-render math formulas and initialize copy buttons after messages update
  useEffect(() => {
    if (messages.length > 0 && messagesContainerRef.current) {
      const lastMessage = messages[messages.length - 1];
      const isUserMessage = lastMessage.isUser;

      // Small delay to ensure DOM is updated
      const timer = setTimeout(() => {
        if (messagesContainerRef.current) {
          // Render Math
          if (window.renderMathInElement) {
            window.renderMathInElement(messagesContainerRef.current, {
              delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false },
                { left: '\\[', right: '\\]', display: true },
              ],
              throwOnError: false,
              ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
            });
          }

          // Initialize Copy Buttons
          const copyButtons = messagesContainerRef.current.querySelectorAll('.copy-button');
          copyButtons.forEach(button => {
            button.addEventListener('click', () => window.copyCode?.(button as HTMLButtonElement));
          });

          // Additional delay for scrolling to ensure content is fully rendered
          setTimeout(() => {
            if (lastMessageRef.current && messagesContainerRef.current) {
              if (isUserMessage) {
                // User message: scroll to bottom
                messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
              } else {
                // AI message: scroll to show new message at top of viewport (within container only)
                const container = messagesContainerRef.current;
                const lastMessageElement = lastMessageRef.current;
                
                // Get the position relative to the scrollable container
                const containerRect = container.getBoundingClientRect();
                const messageRect = lastMessageElement.getBoundingClientRect();
                
                // Calculate scroll position to put message at the top of container
                const scrollOffset = messageRect.top - containerRect.top + container.scrollTop;
                
                container.scrollTop = scrollOffset;
              }
            }
          }, 50);
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleAnalyzePaper = async () => {
    if (uploadTab === 'file' && !selectedFile) return;
    if (uploadTab === 'link' && !paperUrl.trim()) return;

    setIsLoading(true);
    const formData = new FormData();
    if (uploadTab === 'file' && selectedFile) {
      formData.append('file', selectedFile);
    } else {
      formData.append('url', paperUrl);
    }
    formData.append('language', selectedLanguage);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        await loadPapers();
        
        // Find the newly created paper and select it
        const updatedResponse = await fetch('http://localhost:5000/api/papers');
        const updatedData = await updatedResponse.json();
        if (updatedResponse.ok) {
          const newPaper = updatedData.papers.find((p: Paper) => p.id === data.id);
          if (newPaper) {
            // Select the paper which will load messages from database
            await handleSelectPaper(newPaper);
          }
        }
        
        // Reset states
        setSelectedFile(null);
        setPaperUrl('');
        if (fileInputRef.current) fileInputRef.current.value = '';
        setShowUploadModal(false);
      } else {
        alert('Error analyzing paper: ' + data.error);
      }
    } catch (error) {
      alert('Error connecting to server');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !selectedPaper || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: currentMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper_id: selectedPaper.id,
          message: currentMessage,
          language: selectedPaper.language,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.response,
          isUser: false,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: `Error: ${data.error || 'Failed to get response'}`,
          isUser: false,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: 'Error: Unable to connect to server',
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSelectPaper = async (paper: Paper) => {
    setSelectedPaper(paper);
    setIsTyping(false);
    
    const savedMessages = await loadMessages(paper.id);
    setMessages(savedMessages || []);
  };

  const handleDeletePaper = async () => {
    if (!paperToDelete) return;

    try {
      const response = await fetch(`http://localhost:5000/api/papers/${paperToDelete.id}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        setPapers(prev => prev.filter(paper => paper.id !== paperToDelete.id));
        if (selectedPaper?.id === paperToDelete.id) {
          setSelectedPaper(null);
          setMessages([]);
        }
        setShowDeleteModal(false);
        setPaperToDelete(null);
      } else {
        alert('Error deleting paper');
      }
    } catch (error) {
      console.error('Error deleting paper:', error);
      alert('Error deleting paper');
    }
  };

  const confirmDeletePaper = (paper: Paper, event: React.MouseEvent) => {
    event.stopPropagation();
    setPaperToDelete(paper);
    setShowDeleteModal(true);
  };

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>Paper Agent</h2>
          <button 
            className="add-button"
            onClick={() => setShowUploadModal(true)}
            title="Add New Paper"
          >
            +
          </button>
        </div>
        
        <div className="history-section">
          <h3>History</h3>
          <div className="paper-list">
            {papers.map(paper => (
              <div
                key={paper.id}
                className={`paper-item ${selectedPaper?.id === paper.id ? 'selected' : ''}`}
                onClick={() => handleSelectPaper(paper)}
              >
                <div className="paper-content">
                  <div className="paper-title">{paper.title}</div>
                  <div className="paper-meta">
                    {paper.language} • {new Date(paper.timestamp).toLocaleDateString()}
                  </div>
                </div>
                <div className="paper-actions">
                  <button
                    className="location-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Construct URL to open the PDF file
                      const filePath = paper.file_path;
                      let fileUrl = filePath;
                      
                      // If it's a relative path, construct full URL
                      if (!filePath.startsWith('http')) {
                        const uploadsIndex = filePath.indexOf('uploads/');
                        if (uploadsIndex !== -1) {
                          const relativePath = filePath.substring(uploadsIndex);
                          fileUrl = `http://localhost:5000/${relativePath}`;
                        } else {
                          fileUrl = `http://localhost:5000/uploads/${filePath}`;
                        }
                      }
                      
                      // Open PDF in new tab
                      window.open(fileUrl, '_blank');
                    }}
                    title="Open paper in new tab"
                  >
                    📄
                  </button>
                  <button
                    className="delete-button"
                    onClick={(e) => confirmDeletePaper(paper, e)}
                    title="Delete paper"
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="main-content">
        {selectedPaper ? (
          <div className="chat-container">
            <div className="chat-header">
              <h2>{selectedPaper.title}</h2>
              <button 
                className="theme-toggle-button" 
                onClick={toggleTheme}
                title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                {isDarkMode ? '☀️' : '🌙'}
              </button>
            </div>
            
            <div className="messages" ref={messagesContainerRef}>
              {messages.map((message, index) => (
                <div
                  key={message.id}
                  ref={index === messages.length - 1 ? lastMessageRef : null}
                  className={`message ${message.isUser ? 'user-message' : 'ai-message'}`}
                >
                  <div 
                    className="message-content"
                    dangerouslySetInnerHTML={{
                      __html: message.isUser 
                        ? message.text 
                        : convertMarkdownToHtml(message.text)
                    }}
                  />
                </div>
              ))}
              {isTyping && (
                <div className="message ai-message">
                  <div className="message-content typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="message-input">
              <input
                type="text"
                placeholder="Ask a question about this paper..."
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSendMessage()}
                className="chat-input"
                disabled={isTyping}
              />
              <button 
                onClick={handleSendMessage} 
                className="send-button"
                disabled={isTyping || !currentMessage.trim()}
              >
                {isTyping ? 'Thinking...' : 'Send'}
              </button>
            </div>
          </div>
        ) : (
          <div className="placeholder">
            <button 
              className="theme-toggle-button placeholder-theme-toggle" 
              onClick={toggleTheme}
              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {isDarkMode ? '☀️' : '🌙'}
            </button>
            <div className="placeholder-icon">📄</div>
            <h2>Paper Reading Agent</h2>
            <p>Upload a PDF research paper or provide a link to start analyzing and chatting.</p>
            <button 
              className="start-button"
              onClick={() => setShowUploadModal(true)}
            >
              Upload Your Paper
            </button>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="modal-overlay" onClick={() => !isLoading && setShowUploadModal(false)}>
          <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add New Paper</h3>
              {!isLoading && (
                <button className="close-btn" onClick={() => setShowUploadModal(false)}>×</button>
              )}
            </div>
            
            <div className="modal-tabs">
              <button 
                className={`tab-btn ${uploadTab === 'file' ? 'active' : ''}`}
                onClick={() => setUploadTab('file')}
                disabled={isLoading}
              >
                Upload File
              </button>
              <button 
                className={`tab-btn ${uploadTab === 'link' ? 'active' : ''}`}
                onClick={() => setUploadTab('link')}
                disabled={isLoading}
              >
                Paste Link
              </button>
            </div>

            <div className="modal-body">
              {uploadTab === 'file' ? (
                <div className="upload-choice">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                    className="visually-hidden"
                    id="modal-file-upload"
                  />
                  <div 
                    onClick={triggerFileInput} 
                    className={`file-drop-zone ${isLoading ? 'disabled' : ''}`}
                  >
                    <div className="drop-icon">📁</div>
                    <div className="drop-text">
                      {selectedFile ? selectedFile.name : 'Choose PDF'}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="upload-choice">
                  <input
                    type="text"
                    placeholder="Paste PDF link (e.g. ArXiv URL)"
                    value={paperUrl}
                    onChange={(e) => setPaperUrl(e.target.value)}
                    className="modal-url-input"
                    disabled={isLoading}
                  />
                  <p className="url-hint">Tip: ArXiv abstract links work automatically!</p>
                </div>
              )}

              <div className="language-choice">
                <label>Output Language:</label>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="modal-language-select"
                  disabled={isLoading}
                >
                  {languages.map(lang => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleAnalyzePaper}
                disabled={isLoading || (uploadTab === 'file' ? !selectedFile : !paperUrl.trim())}
                className="modal-analyze-button"
              >
                {isLoading ? (
                  <span className="loading-spinner">Analyzing Paper...</span>
                ) : (
                  'Analyze and Add'
                )}
              </button>
              {isLoading && (
                <p className="loading-time-hint">This process usually takes about 1 minute. Please don't close this window.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && paperToDelete && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="upload-modal delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Delete Paper</h3>
              <button className="close-btn" onClick={() => setShowDeleteModal(false)}>×</button>
            </div>
            <div className="modal-body delete-modal-body">
              <div className="delete-warning-icon">⚠️</div>
              <p className="delete-confirm-text">Are you sure you want to delete <strong>"{paperToDelete.title}"</strong>?</p>
              <p className="delete-subtext">This action cannot be undone and all chat history will be lost.</p>
              
              <div className="modal-actions">
                <button 
                  className="cancel-btn" 
                  onClick={() => setShowDeleteModal(false)}
                >
                  Cancel
                </button>
                <button 
                  className="confirm-delete-btn" 
                  onClick={handleDeletePaper}
                >
                  Delete Paper
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
