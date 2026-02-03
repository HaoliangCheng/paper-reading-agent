import styled from 'styled-components';

export const AnimationContainer = styled.div`
  width: 100%;
  margin: 16px 0;
  border-radius: ${props => props.theme.borderRadius.md};
  overflow: hidden;
  background-color: ${props => props.theme.colors.bgSecondary};
`;

export const AnimationHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background-color: ${props => props.theme.colors.bgTertiary};
  border-bottom: 1px solid ${props => props.theme.colors.borderColor};
  font-size: 0.8rem;
  color: ${props => props.theme.colors.textSecondary};
`;

export const AnimationLabel = styled.span`
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
`;

export const AnimationIcon = styled.span`
  font-size: 1rem;
`;

export const AnimationIframe = styled.iframe`
  width: 100%;
  height: 400px;
  border: none;
  background-color: white;
`;

export const ExpandButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.primary};
  cursor: pointer;
  font-size: 0.8rem;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.bgSecondary};
  }
`;
