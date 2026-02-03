import React, { useLayoutEffect, useRef, memo, useMemo } from 'react';
import { Message } from '../../types';
import AnimationRenderer from '../AnimationRenderer';
import * as S from './MessageStyles';

interface MessageItemProps {
  message: Message;
  renderContent: (text: string) => string;
  isLast?: boolean;
  messageRef?: React.RefObject<any>;
}

interface MessagePart {
  type: 'text' | 'animation';
  content: string;
}

/**
 * Parse message content to extract animation blocks.
 * Supports:
 * 1. Explicit markers: <<<ANIMATION_START>>> ... <<<ANIMATION_END>>>
 * 2. Raw HTML documents: <!DOCTYPE html>...</html> or <html>...</html>
 *
 * Returns an array of parts, each being either text or animation content.
 */
const parseMessageContent = (text: string): MessagePart[] => {
  const parts: MessagePart[] = [];
  let remainingText = text;

  // First, try explicit markers
  const markerRegex = /<<<ANIMATION_START>>>([\s\S]*?)<<<ANIMATION_END>>>/g;
  let lastIndex = 0;
  let match;

  while ((match = markerRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: 'animation', content: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }

  if (parts.length > 0) {
    // Found explicit markers
    if (lastIndex < text.length) {
      parts.push({ type: 'text', content: text.slice(lastIndex) });
    }
    return parts;
  }

  // Fallback: detect raw HTML documents
  // Pattern 1: <!DOCTYPE html>...followed by </html>
  // Pattern 2: <html>...</html>
  const htmlDocRegex = /(<!DOCTYPE\s+html[^>]*>[\s\S]*?<\/html>|<html[^>]*>[\s\S]*?<\/html>)/gi;
  lastIndex = 0;

  while ((match = htmlDocRegex.exec(remainingText)) !== null) {
    if (match.index > lastIndex) {
      const textBefore = remainingText.slice(lastIndex, match.index).trim();
      if (textBefore) {
        parts.push({ type: 'text', content: textBefore });
      }
    }
    parts.push({ type: 'animation', content: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }

  if (parts.length > 0) {
    if (lastIndex < remainingText.length) {
      const textAfter = remainingText.slice(lastIndex).trim();
      if (textAfter) {
        parts.push({ type: 'text', content: textAfter });
      }
    }
    return parts;
  }

  // No animations found, return whole text
  return [{ type: 'text', content: text }];
};

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  renderContent,
  isLast,
  messageRef,
}) => {
  const contentRef = useRef<HTMLDivElement>(null);

  // Parse message to separate text and animation parts
  const messageParts = useMemo(() => {
    return parseMessageContent(message.text);
  }, [message.text]);

  // Check if there are any animations in this message
  const hasAnimations = messageParts.some(part => part.type === 'animation');

  useLayoutEffect(() => {
    // Render math for all messages to ensure consistency
    if (contentRef.current && window.renderMathInElement) {
      window.renderMathInElement(contentRef.current, {
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
  }); // Run on every render to be safe

  // If message has animations, render parts separately
  if (hasAnimations) {
    return (
      <S.MessageWrapper isUser={message.isUser} ref={isLast ? messageRef : null}>
        <S.MessageContentWithAnimation ref={contentRef} isUser={message.isUser}>
          {messageParts.map((part, index) => {
            if (part.type === 'animation') {
              return <AnimationRenderer key={index} htmlContent={part.content} />;
            }
            // Render text part with markdown processing
            const htmlContent = renderContent(part.content);
            return (
              <S.TextPart
                key={index}
                isUser={message.isUser}
                dangerouslySetInnerHTML={{ __html: htmlContent }}
              />
            );
          })}
        </S.MessageContentWithAnimation>
      </S.MessageWrapper>
    );
  }

  // Standard rendering for messages without animations
  const htmlContent = renderContent(message.text);

  return (
    <S.MessageWrapper isUser={message.isUser} ref={isLast ? messageRef : null}>
      <S.MessageContent
        ref={contentRef}
        isUser={message.isUser}
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </S.MessageWrapper>
  );
};

// Use memo to prevent re-renders when parent types in textbox
export default memo(MessageItem);
