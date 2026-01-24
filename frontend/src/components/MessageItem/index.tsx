import React, { useLayoutEffect, useRef, memo, useMemo } from 'react';
import { Message } from '../../types';
import * as S from './MessageStyles';

interface MessageItemProps {
  message: Message;
  renderContent: (text: string) => string;
  isLast?: boolean;
  messageRef?: React.RefObject<any>;
}

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  renderContent,
  isLast,
  messageRef,
}) => {
  const contentRef = useRef<HTMLDivElement>(null);

  const htmlContent = useMemo(() => {
    return message.isUser ? message.text : renderContent(message.text);
  }, [message.text, message.isUser, renderContent]);

  useLayoutEffect(() => {
    // Only render math for messages that aren't from the user
    if (!message.isUser && contentRef.current && window.renderMathInElement) {
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
