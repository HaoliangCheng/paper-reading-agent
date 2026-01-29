import React, { useState } from 'react';
import { Paper, Message } from '../../types';
import * as S from './ChatStyles';
import MessageItem from '../MessageItem';
import { Input, Button } from '../Common';

interface ChatInterfaceProps {
  selectedPaper: Paper | null;
  messages: Message[];
  currentMessage: string;
  isTyping: boolean;
  thinkingStage: string;
  isDarkMode: boolean;
  onSendMessage: () => void;
  onMessageChange: (text: string) => void;
  onToggleTheme: () => void;
  onShowUpload: () => void;
  convertMarkdownToHtml: (text: string) => string;
  messagesContainerRef: React.RefObject<any>;
  lastMessageRef: React.RefObject<any>;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  selectedPaper,
  messages,
  currentMessage,
  isTyping,
  thinkingStage,
  isDarkMode,
  onSendMessage,
  onMessageChange,
  onToggleTheme,
  onShowUpload,
  convertMarkdownToHtml,
  messagesContainerRef,
  lastMessageRef,
}) => {
  const [showPlan, setShowPlan] = useState(false);
  if (!selectedPaper) {
    return (
      <S.Placeholder>
        <S.ThemeToggleButton 
          style={{ position: 'absolute', top: '20px', right: '20px' }}
          onClick={onToggleTheme}
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </S.ThemeToggleButton>
        <S.PlaceholderIcon>📄</S.PlaceholderIcon>
        <h2 style={{ fontSize: '1.875rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '12px' }}>Paper Reading Agent</h2>
        <p style={{ fontSize: '1.125rem', maxWidth: '480px', lineHeight: 1.6, marginBottom: '32px' }}>Upload a PDF research paper or provide a link to start analyzing and chatting.</p>
        <Button onClick={onShowUpload} style={{ padding: '12px 24px', fontSize: '1rem' }}>
          Upload Your Paper
        </Button>
      </S.Placeholder>
    );
  }

  return (
    <S.ChatContainer>
      <S.ChatHeader>
        <h2>{selectedPaper.title}</h2>
        <S.ThemeToggleButton
          onClick={onToggleTheme}
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </S.ThemeToggleButton>
      </S.ChatHeader>

      {selectedPaper?.reading_plan && selectedPaper.reading_plan.length > 0 && (
        <S.ReadingPlanSection>
          <S.PlanHeader onClick={() => setShowPlan(!showPlan)}>
            <S.PlanToggleIcon $isOpen={showPlan}>▶</S.PlanToggleIcon>
            Reading Plan ({selectedPaper.reading_plan.length} steps)
          </S.PlanHeader>
          {showPlan && (
            <S.PlanList>
              {selectedPaper.reading_plan.map((item) => (
                <S.PlanItem key={item.step}>
                  <S.StepNumber>{item.step}</S.StepNumber>
                  <S.StepContent>
                    <S.StepTitle>{item.title}</S.StepTitle>
                    <S.StepDesc>{item.description}</S.StepDesc>
                    {item.key_topics && item.key_topics.length > 0 && (
                      <S.StepTopics>
                        {item.key_topics.map((topic, idx) => (
                          <S.TopicTag key={idx}>{topic}</S.TopicTag>
                        ))}
                      </S.StepTopics>
                    )}
                  </S.StepContent>
                </S.PlanItem>
              ))}
            </S.PlanList>
          )}
        </S.ReadingPlanSection>
      )}

      <S.MessagesArea ref={messagesContainerRef}>
        {messages.map((message, index) => (
          <MessageItem
            key={message.id}
            message={message}
            renderContent={convertMarkdownToHtml}
            isLast={index === messages.length - 1}
            messageRef={lastMessageRef}
          />
        ))}
        {isTyping && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <S.TypingIndicatorContainer>
              <S.ThinkingStage>
                <span>{thinkingStage || 'Thinking'}</span>
              </S.ThinkingStage>
              <S.TypingDots>
                <span></span>
                <span></span>
                <span></span>
              </S.TypingDots>
            </S.TypingIndicatorContainer>
          </div>
        )}
      </S.MessagesArea>
      
      <S.MessageInputArea>
        <Input
          type="text"
          placeholder="Ask a question about this paper..."
          value={currentMessage}
          onChange={(e) => onMessageChange(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !isTyping && onSendMessage()}
          disabled={isTyping}
        />
        <Button 
          onClick={onSendMessage} 
          disabled={isTyping || !currentMessage.trim()}
          style={{ padding: '0 20px' }}
        >
          {isTyping ? 'Thinking' : 'Send'}
        </Button>
      </S.MessageInputArea>
    </S.ChatContainer>
  );
};

export default ChatInterface;
