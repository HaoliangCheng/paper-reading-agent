import styled from 'styled-components';

export const SidebarContainer = styled.div<{ isCollapsed: boolean }>`
  width: ${props => props.isCollapsed ? '64px' : '260px'};
  background-color: ${props => props.theme.colors.bgSecondary};
  border-right: 1px solid ${props => props.theme.colors.borderColor};
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 4px 0 15px ${props => props.theme.colors.shadow};
  z-index: 10;
  transition: all 0.3s ease;

  flex-shrink: 0;

  @media (max-width: ${props => props.theme.breakpoints.mobile}) {
    width: ${props => props.isCollapsed ? '64px' : '100%'};
    position: relative;
    z-index: 100;
  }
`;

export const SidebarHeader = styled.div<{ isCollapsed: boolean }>`
  height: ${props => props.isCollapsed ? '112px' : '60px'};
  padding: ${props => props.isCollapsed ? '16px 12px' : '0 16px'};
  border-bottom: none;
  display: flex;
  justify-content: ${props => props.isCollapsed ? 'center' : 'space-between'};
  align-items: center;
  transition: all 0.3s ease;
  flex-shrink: 0;

  h2 {
    display: ${props => props.isCollapsed ? 'none' : 'block'};
    font-size: 1.125rem;
    font-weight: 700;
    color: ${props => props.theme.colors.textPrimary};
    letter-spacing: -0.025em;
    white-space: nowrap;
  }

  // @media (max-width: ${props => props.theme.breakpoints.mobile}) {
  //   height: 60px;
  //   padding: 0 16px;
  //   justify-content: space-between;
    
  //   h2 {
  //     display: block; /* Always show title on mobile header */
  //     font-size: 1.125rem;
  //   }
  // }
`;

export const HeaderButtons = styled.div<{ isCollapsed: boolean }>`
  display: flex;
  flex-direction: ${props => props.isCollapsed ? 'column' : 'row'};
  gap: 8px;
  align-items: center;
`;

export const AddButton = styled.button<{ isCollapsed: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;

  &:hover {
    background-color: ${props => props.theme.colors.primaryHover};
    transform: translateY(-1px);
  }
`;

export const ProfileButton = styled.button<{ isCollapsed: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.bgHover};
  color: ${props => props.theme.colors.textSecondary};
  border: 1px solid ${props => props.theme.colors.borderColor};
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;

  &:hover {
    background-color: ${props => props.theme.colors.borderColor};
    color: ${props => props.theme.colors.textPrimary};
    transform: translateY(-1px);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

export const CollapseButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.textSecondary};
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: ${props => props.theme.borderRadius.md};
  transition: all 0.2s;

  &:hover {
    background-color: ${props => props.theme.colors.bgHover};
    color: ${props => props.theme.colors.textPrimary};
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

export const HistorySection = styled.div`
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;

  h3 {
    padding: 12px 16px 6px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: ${props => props.theme.colors.textSecondary};
    white-space: nowrap;
    
    @media (max-width: ${props => props.theme.breakpoints.mobile}) {
      padding: 10px 16px 4px;
    }
  }
`;

export const PaperList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  scrollbar-width: thin;
  scrollbar-color: ${props => props.theme.colors.borderColorDark} transparent;

  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.borderColorDark};
    border-radius: 10px;
  }
  &::-webkit-scrollbar-thumb:hover {
    background: ${props => props.theme.colors.textTertiary};
  }
`;

export const PaperItem = styled.div<{ isSelected: boolean; isCollapsed: boolean }>`
  padding: ${props => props.isCollapsed ? '8px 0' : '8px 10px'};
  margin-bottom: 6px;
  border-radius: ${props => props.theme.borderRadius.lg};
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: ${props => props.isCollapsed ? 'center' : 'space-between'};
  align-items: center;
  border: 1px solid ${props => props.isSelected ? props.theme.colors.primary : 'transparent'};
  background-color: ${props => props.isSelected ? props.theme.colors.bgHover : 'transparent'};

  &:hover {
    background-color: ${props => props.theme.colors.bgHover};
  }
`;

export const PaperIcon = styled.div`
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
`;

export const PaperContent = styled.div<{ isCollapsed: boolean }>`
  display: ${props => props.isCollapsed ? 'none' : 'block'};
  flex: 1;
  min-width: 0;
  margin-left: 0;
`;

export const PaperTitle = styled.div`
  font-weight: 600;
  font-size: 0.8125rem;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 2px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
  word-wrap: break-word;
  overflow-wrap: break-word;
`;

export const PaperMeta = styled.div`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textTertiary};
`;

export const PaperActions = styled.div<{ isCollapsed: boolean }>`
  display: ${props => props.isCollapsed ? 'none' : 'flex'};
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 12px;
  min-width: 45px;
`;

export const ViewPdfButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  background-color: transparent;
  color: #34d399;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.7;

  &:hover {
    opacity: 1;
    color: #10b981;
    background-color: #ecfdf5;
    border-color: #a7f3d0;
  }

  svg {
    stroke-width: 2.5;
    width: 10px;
    height: 10px;
  }

  .dark-mode & {
    color: #6ee7b7;
    &:hover {
      color: #a7f3d0;
      background-color: rgba(16, 185, 129, 0.1);
      border-color: rgba(16, 185, 129, 0.2);
    }
  }
`;

export const DeletePaperButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  background-color: transparent;
  color: ${props => props.theme.colors.danger};
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0;

  ${PaperItem}:hover & {
    opacity: 0.7;
  }

  &:hover {
    opacity: 1 !important;
    color: ${props => props.theme.colors.dangerHover};
    background-color: #fef2f2;
    border-color: #fecaca;
  }

  .dark-mode & {
    color: #f87171;
    &:hover {
      color: #fca5a5;
      background-color: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.2);
    }
  }
`;

export const SidebarFooter = styled.div`
  padding: 20px;
  border-top: 1px solid ${props => props.theme.colors.borderColor};
  display: flex;
  justify-content: center;
  align-items: center;
`;
