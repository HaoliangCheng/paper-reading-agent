import styled from 'styled-components';

export const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: ${props => props.theme.colors.bgSecondary};
`;

export const ChatHeader = styled.div`
  height: 80px;
  padding: 0 16px;
  border-bottom: 1px solid ${props => props.theme.colors.borderColor};
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: ${props => props.theme.colors.bgSecondary};

  h2 {
    font-size: 1.125rem;
    font-weight: 700;
    color: ${props => props.theme.colors.textPrimary};
    margin: 0;
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: break-word;
    flex: 1;
  }
`;

export const ThemeToggleButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.lg};
  background-color: ${props => props.theme.colors.bgHover};
  border: 1px solid ${props => props.theme.colors.borderColor};
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 12px;

  &:hover {
    background-color: ${props => props.theme.colors.borderColor};
    transform: scale(1.05);
  }
`;

export const MessagesArea = styled.div`
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: ${props => props.theme.colors.bgTertiary};
`;

export const MessageInputArea = styled.div`
  display: flex;
  padding: 16px;
  gap: 12px;
  border-top: 1px solid ${props => props.theme.colors.borderColor};
  background-color: ${props => props.theme.colors.bgSecondary};
`;

export const TypingIndicatorContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  background-color: ${props => props.theme.colors.bgSecondary};
  border: 1px solid ${props => props.theme.colors.borderColor};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 8px 16px;
  box-shadow: 0 4px 12px ${props => props.theme.colors.shadow};
`;

export const ThinkingStage = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: ${props => props.theme.colors.textPrimary};
  font-weight: 500;
  font-size: 0.9rem;
`;

export const TypingDots = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;

  span {
    width: 4px;
    height: 4px;
    background-color: ${props => props.theme.colors.primary};
    border-radius: 50%;
    opacity: 0.4;
    animation: typing-fade 1.4s infinite;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }

  @keyframes typing-fade {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
  }
`;

export const Placeholder = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  padding: 40px;
  position: relative;
`;

export const PlaceholderIcon = styled.div`
  font-size: 64px;
  margin-bottom: 24px;
  filter: drop-shadow(0 4px 6px ${props => props.theme.colors.shadow});
`;
