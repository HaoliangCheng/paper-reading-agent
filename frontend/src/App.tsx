import React, { useState, useEffect, useRef, useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import 'katex/dist/katex.min.css';
import styled, { ThemeProvider } from 'styled-components';
import { theme } from './theme/Theme';
import { Paper, Message } from './types';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import UploadModal from './components/Modals/UploadModal';
import DeleteModal from './components/Modals/DeleteModal';
import './App.css';

const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: ${props => props.theme.colors.bgPrimary};
  color: ${props => props.theme.colors.textPrimary};
`;

const MainContentWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: ${props => props.theme.colors.bgPrimary};
`;

// Extend window interface for renderMathInElement and highlight.js
declare global {
  interface Window {
    renderMathInElement?: (element: HTMLElement, options?: any) => void;
    hljs?: any;
    copyCode?: (button: HTMLButtonElement) => void;
  }
}

// Global function for copying code
window.copyCode = (button: HTMLButtonElement) => {
  const code = button.getAttribute('data-code');
  if (!code) return;

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

marked.setOptions({
  breaks: true,
  gfm: true,
});

const decodeHTMLEntities = (text: string): string => {
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
};

const processCodeBlocks = (htmlContent: string): string => {
  let processed = htmlContent.replace(
    /<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
    (match, language, code) => {
      const decodedCode = decodeHTMLEntities(code);
      let highlighted = code;
      if (window.hljs) {
        try {
          highlighted = window.hljs.highlight(decodedCode, { language }).value;
        } catch (e) {
          console.error('Highlight error:', e);
        }
      }

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

  processed = processed.replace(
    /<pre><code>([\s\S]*?)<\/code><\/pre>/g,
    (match, code) => {
      const decodedCode = decodeHTMLEntities(code);
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
    const mathBlocks: string[] = [];
    let processedMarkdown = markdown.replace(
      /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|(?:\$[^$\n]+\$))/g,
      (match) => {
        const placeholder = `@@MATH_BLOCK_${mathBlocks.length}@@`;
        mathBlocks.push(match);
        return placeholder;
      }
    );

    for (let i = 0; i < 3; i++) {
      processedMarkdown = processedMarkdown.replace(/^(\s*\d+\.\s+.*|^\s+!\[.*\]\(.*\))\n+(!\[.*\]\(.*\))/gm, '$1\n   $2');
    }
    
    processedMarkdown = processedMarkdown.replace(
      /!\[([^\]]*)\]\(([^)]+\.(png|jpg|jpeg|gif|svg))\)/gi,
      (match, altText, imagePath) => {
        if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
          return match;
        }
        const uploadsIndex = imagePath.indexOf('uploads/');
        if (uploadsIndex !== -1) {
          const relativePath = imagePath.substring(uploadsIndex + 8);
          return `![${altText}](http://localhost:5000/uploads/${relativePath})`;
        }
        return `![${altText}](http://localhost:5000/uploads/${imagePath})`;
      }
    );
    
    const result = marked.parse(processedMarkdown);
    let htmlContent = typeof result === 'string' ? result : '';
    
    mathBlocks.forEach((math, index) => {
      const placeholder = `@@MATH_BLOCK_${index}@@`;
      htmlContent = htmlContent.split(placeholder).join(math);
    });

    htmlContent = htmlContent
      .replace(/<strong><strong>/g, '<strong>')
      .replace(/<\/strong><\/strong>/g, '</strong>');
    
    htmlContent = processCodeBlocks(htmlContent);

    return DOMPurify.sanitize(htmlContent, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 's', 'a', 'img', 'code', 'pre', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'button'],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'id', 'data-code']
    });
  } catch (error) {
    console.error('Error parsing markdown:', error);
    return markdown;
  }
};

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
  const [thinkingStage, setThinkingStage] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    if (messages.length > 0 && messagesContainerRef.current) {
      const lastMessage = messages[messages.length - 1];
      const isUserMessage = lastMessage.isUser;

      // Handle copy buttons (still need this globally for the container)
      const copyButtons = messagesContainerRef.current.querySelectorAll('.copy-button');
      copyButtons.forEach(button => {
        button.addEventListener('click', () => window.copyCode?.(button as HTMLButtonElement));
      });

      // Handle scrolling
      const timer = setTimeout(() => {
        if (lastMessageRef.current && messagesContainerRef.current) {
          if (isUserMessage) {
            messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
          } else {
            const container = messagesContainerRef.current;
            const lastMessageElement = lastMessageRef.current;
            const containerRect = container.getBoundingClientRect();
            const messageRect = lastMessageElement.getBoundingClientRect();
            const scrollOffset = messageRect.top - containerRect.top + container.scrollTop;
            container.scrollTop = scrollOffset;
          }
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages, selectedPaper]); // Only scroll/bind buttons when messages or paper change

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleAnalyzePaper = async () => {
    if (uploadTab === 'file' && !selectedFile) return;
    if (uploadTab === 'link' && !paperUrl.trim()) return;

    setIsLoading(true);
    setThinkingStage('Uploading paper');
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

      if (!response.body) throw new Error('No response body');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6));
            if (data.status) {
              setThinkingStage(data.status);
            } else if (data.response) {
              await loadPapers();
              const updatedResponse = await fetch('http://localhost:5000/api/papers');
              const updatedData = await updatedResponse.json();
              if (updatedResponse.ok) {
                const newPaper = updatedData.papers.find((p: Paper) => p.id === data.id);
                if (newPaper) {
                  await handleSelectPaper(newPaper);
                }
              }
              setSelectedFile(null);
              setPaperUrl('');
              if (fileInputRef.current) fileInputRef.current.value = '';
              setShowUploadModal(false);
              setIsLoading(false);
              setThinkingStage('');
            } else if (data.error) {
              throw new Error(data.error);
            }
          }
        }
      }
    } catch (error: any) {
      alert('Error: ' + error.message);
      setIsLoading(false);
      setThinkingStage('');
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
    setThinkingStage('Thinking');

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

      if (!response.body) throw new Error('No response body');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6));
            if (data.status) {
              setThinkingStage(data.status);
            } else if (data.response) {
              const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: data.response,
                isUser: false,
                timestamp: new Date().toISOString(),
              };
              setMessages(prev => [...prev, aiMessage]);
              setIsTyping(false);
              setThinkingStage('');
            } else if (data.error) {
              throw new Error(data.error);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: `Error: ${error.message || 'Unable to connect to server'}`,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
      setThinkingStage('');
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
    <ThemeProvider theme={theme}>
      <AppContainer>
        <Sidebar 
          papers={papers}
          selectedPaper={selectedPaper}
          onSelectPaper={handleSelectPaper}
          onAddPaper={() => setShowUploadModal(true)}
          onConfirmDelete={confirmDeletePaper}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        <MainContentWrapper>
          <ChatInterface 
            selectedPaper={selectedPaper}
            messages={messages}
            currentMessage={currentMessage}
            isTyping={isTyping}
            thinkingStage={thinkingStage}
            isDarkMode={isDarkMode}
            onSendMessage={handleSendMessage}
            onMessageChange={setCurrentMessage}
            onToggleTheme={toggleTheme}
            onShowUpload={() => setShowUploadModal(true)}
            convertMarkdownToHtml={convertMarkdownToHtml}
            messagesContainerRef={messagesContainerRef as any}
            lastMessageRef={lastMessageRef as any}
          />
        </MainContentWrapper>

        {showUploadModal && (
          <UploadModal 
            isLoading={isLoading}
            uploadTab={uploadTab}
            setUploadTab={setUploadTab}
            selectedFile={selectedFile}
            paperUrl={paperUrl}
            setPaperUrl={setPaperUrl}
            selectedLanguage={selectedLanguage}
            setSelectedLanguage={setSelectedLanguage}
            thinkingStage={thinkingStage}
            onClose={() => setShowUploadModal(false)}
            onAnalyze={handleAnalyzePaper}
            onFileChange={handleFileChange}
            fileInputRef={fileInputRef as any}
          />
        )}

        {showDeleteModal && paperToDelete && (
          <DeleteModal 
            paper={paperToDelete}
            onClose={() => setShowDeleteModal(false)}
            onConfirm={handleDeletePaper}
          />
        )}
      </AppContainer>
    </ThemeProvider>
  );
};

export default App;
