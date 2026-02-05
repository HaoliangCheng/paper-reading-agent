import styled from 'styled-components';

export const MessageWrapper = styled.div<{ isUser: boolean }>`
  display: flex;
  width: 100%;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
`;

export const MessageContent = styled.div<{ isUser: boolean }>`
  max-width: 80%;
  padding: 10px 16px;
  border-radius: ${props => props.theme.borderRadius.xl};
  font-size: 0.9375rem;
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
  background-color: ${props => props.isUser ? props.theme.colors.primary : props.theme.colors.bgSecondary};
  color: ${props => props.isUser ? 'white' : props.theme.colors.textPrimary};
  border-bottom-right-radius: ${props => props.isUser ? '4px' : props.theme.borderRadius.xl};
  border-bottom-left-radius: ${props => props.isUser ? props.theme.borderRadius.xl : '4px'};
  box-shadow: ${props => props.isUser ? 'none' : `0 1px 3px ${props.theme.colors.shadow}`};
  border: ${props => props.isUser ? 'none' : `1px solid ${props.theme.colors.borderColor}`};

  img {
    max-width: 100%;
    height: auto;
    border-radius: ${props => props.theme.borderRadius.md};
    margin: 12px auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: block;
  }

  h1, h2, h3 {
    margin: 0.5em 0 0.5em 0;
    font-weight: 700;
    line-height: 1.2;
  }

  h1 { font-size: 1.25rem; border-bottom: 1px solid ${props => props.theme.colors.borderColor}; padding-bottom: 0.5rem; }
  h2 { font-size: 1.1rem; }
  h3 { font-size: 1rem; }

  p { margin: 0.75em 0; }
  p:first-child { margin-top: 0; }
  p:last-child { margin-bottom: 0; }

  ul, ol { margin: 0.75em 0; padding-left: 1.5rem; }
  li { margin: 0.4em 0; }

  a {
    color: ${props => props.isUser ? '#d1fae5' : props.theme.colors.primary};
    text-decoration: underline;
    transition: color 0.2s;
    &:hover { color: ${props => props.isUser ? 'white' : props.theme.colors.primaryHover}; }
  }

  code {
    background-color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.2)' : props.theme.colors.codeBg};
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 0.85em;
    color: ${props => props.isUser ? 'white' : props.theme.colors.codeText};
  }

  pre {
    background-color: ${props => props.theme.colors.codeBg};
    color: ${props => props.theme.colors.codeText};
    padding: 16px;
    border-radius: ${props => props.theme.borderRadius.md};
    overflow-x: auto;
    margin: 12px 0;
    border: 1px solid ${props => props.theme.colors.codeBorder};
  }

  pre code {
    background-color: transparent;
    padding: 0;
    color: inherit;
  }

  blockquote {
    border-left: 4px solid ${props => props.isUser ? 'rgba(255, 255, 255, 0.4)' : props.theme.colors.primary};
    padding-left: 16px;
    margin: 12px 0;
    color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.8)' : props.theme.colors.textSecondary};
    font-style: italic;
  }
`;

// Container for messages that include animations - needs to handle mixed content
export const MessageContentWithAnimation = styled(MessageContent)`
  /* Wider to accommodate animations */
  max-width: 90%;
`;

// Wrapper for text parts within a message that has animations
export const TextPart = styled.div<{ isUser?: boolean }>`
  /* Inherit text styles from parent MessageContent */

  img {
    max-width: 100%;
    height: auto;
    border-radius: ${props => props.theme.borderRadius.md};
    margin: 12px auto;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    display: block;
  }

  h1, h2, h3 {
    margin: 0.5em 0 0.5em 0;
    font-weight: 700;
    line-height: 1.2;
  }

  h1 { font-size: 1.25rem; border-bottom: 1px solid ${props => props.theme.colors.borderColor}; padding-bottom: 0.5rem; }
  h2 { font-size: 1.1rem; }
  h3 { font-size: 1rem; }

  p { margin: 0.75em 0; }
  p:first-child { margin-top: 0; }
  p:last-child { margin-bottom: 0; }

  ul, ol { margin: 0.75em 0; padding-left: 1.5rem; }
  li { margin: 0.4em 0; }

  a {
    color: ${props => props.isUser ? '#d1fae5' : props.theme.colors.primary};
    text-decoration: underline;
    transition: color 0.2s;
    &:hover { color: ${props => props.isUser ? 'white' : props.theme.colors.primaryHover}; }
  }

  code {
    background-color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.2)' : props.theme.colors.codeBg};
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 0.85em;
    color: ${props => props.isUser ? 'white' : props.theme.colors.codeText};
  }

  pre {
    background-color: ${props => props.theme.colors.codeBg};
    color: ${props => props.theme.colors.codeText};
    padding: 16px;
    border-radius: ${props => props.theme.borderRadius.md};
    overflow-x: auto;
    margin: 12px 0;
    border: 1px solid ${props => props.theme.colors.codeBorder};
  }

  pre code {
    background-color: transparent;
    padding: 0;
    color: inherit;
  }

  blockquote {
    border-left: 4px solid ${props => props.isUser ? 'rgba(255, 255, 255, 0.4)' : props.theme.colors.primary};
    padding-left: 16px;
    margin: 12px 0;
    color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.8)' : props.theme.colors.textSecondary};
    font-style: italic;
  }
`;
