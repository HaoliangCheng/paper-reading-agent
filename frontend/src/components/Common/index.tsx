import styled from 'styled-components';

export const Button = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' }>`
  padding: 10px 20px;
  border-radius: ${props => props.theme.borderRadius.md};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.9375rem;

  ${props => {
    switch (props.variant) {
      case 'danger':
        return `
          background-color: ${props.theme.colors.danger};
          color: white;
          &:hover { background-color: ${props.theme.colors.dangerHover}; transform: translateY(-1px); }
        `;
      case 'secondary':
        return `
          background-color: ${props.theme.colors.bgHover};
          color: ${props.theme.colors.textSecondary};
          border: 1px solid ${props.theme.colors.borderColor};
          &:hover { background-color: ${props.theme.colors.borderColor}; }
        `;
      default:
        return `
          background-color: ${props.theme.colors.primary};
          color: white;
          &:hover { background-color: ${props.theme.colors.primaryHover}; transform: translateY(-1px); }
        `;
    }
  }}

  &:disabled {
    background-color: #cbd5e1;
    cursor: not-allowed;
    transform: none;
    opacity: 0.6;
  }
`;

export const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const ModalContainer = styled.div<{ maxWidth?: string }>`
  background-color: ${props => props.theme.colors.bgSecondary};
  width: 100%;
  max-width: ${props => props.maxWidth || '500px'};
  border-radius: ${props => props.theme.borderRadius.xxl};
  box-shadow: 0 25px 50px -12px ${props => props.theme.colors.shadow};
  overflow: hidden;
  animation: modalIn 0.3s ease-out;

  @keyframes modalIn {
    from { opacity: 0; transform: scale(0.95) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }
`;

export const ModalHeader = styled.div`
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${props => props.theme.colors.borderColor};

  h3 {
    font-size: 1.125rem;
    font-weight: 700;
    color: ${props => props.theme.colors.textPrimary};
  }
`;

export const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;
  line-height: 1;
`;

export const ModalBody = styled.div`
  padding: 24px;
`;

export const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.borderColor};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 0.9375rem;
  transition: all 0.2s;
  background-color: ${props => props.theme.colors.bgSecondary};
  color: ${props => props.theme.colors.textPrimary};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  }

  &:disabled {
    background-color: ${props => props.theme.colors.bgHover};
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

export const Select = styled.select`
  width: 100%;
  padding: 12px;
  border: 1px solid ${props => props.theme.colors.borderColor};
  border-radius: ${props => props.theme.borderRadius.lg};
  font-size: 0.9375rem;
  background-color: ${props => props.theme.colors.bgSecondary};
  color: ${props => props.theme.colors.textPrimary};
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }

  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;
