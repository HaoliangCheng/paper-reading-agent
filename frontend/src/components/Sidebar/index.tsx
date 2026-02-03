import React from 'react';
import { Paper } from '../../types';
import * as S from './SidebarStyles';

interface SidebarProps {
  papers: Paper[];
  selectedPaper: Paper | null;
  onSelectPaper: (paper: Paper) => void;
  onAddPaper: () => void;
  onOpenProfile: () => void;
  onConfirmDelete: (paper: Paper, event: React.MouseEvent) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  papers,
  selectedPaper,
  onSelectPaper,
  onAddPaper,
  onOpenProfile,
  onConfirmDelete,
  isCollapsed,
  onToggleCollapse,
}) => {
  const handleViewPdf = (paper: Paper, event: React.MouseEvent) => {
    event.stopPropagation();
    const filePath = paper.file_path;
    let fileUrl = filePath;
    
    if (!filePath.startsWith('http')) {
      const uploadsIndex = filePath.indexOf('uploads/');
      if (uploadsIndex !== -1) {
        const relativePath = filePath.substring(uploadsIndex);
        fileUrl = `http://localhost:5000/${relativePath}`;
      } else {
        fileUrl = `http://localhost:5000/uploads/${filePath}`;
      }
    }
    
    window.open(fileUrl, '_blank');
  };

  return (
    <S.SidebarContainer isCollapsed={isCollapsed}>
      <S.SidebarHeader isCollapsed={isCollapsed}>
        <h2>Paper Agent</h2>
        <S.HeaderButtons isCollapsed={isCollapsed}>
          <S.ProfileButton
            isCollapsed={isCollapsed}
            onClick={onOpenProfile}
            title="User Profile"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </S.ProfileButton>
          <S.AddButton
            isCollapsed={isCollapsed}
            onClick={onAddPaper}
            title="Add New Paper"
          >
            +
          </S.AddButton>
        </S.HeaderButtons>
      </S.SidebarHeader>
      
      <S.HistorySection>
        {!isCollapsed && <h3>Paper List</h3>}
        <S.PaperList>
          {papers.map(paper => (
            <S.PaperItem
              key={paper.id}
              isSelected={selectedPaper?.id === paper.id}
              isCollapsed={isCollapsed}
              onClick={() => onSelectPaper(paper)}
              title={isCollapsed ? paper.title : undefined}
            >
              {isCollapsed ? (
                <S.PaperIcon>📄</S.PaperIcon>
              ) : (
                <>
                  <S.PaperContent isCollapsed={isCollapsed}>
                    <S.PaperTitle>{paper.title}</S.PaperTitle>
                    <S.PaperMeta>
                      {paper.language} • {new Date(paper.timestamp).toLocaleDateString()}
                    </S.PaperMeta>
                  </S.PaperContent>
                  <S.PaperActions isCollapsed={isCollapsed}>
                    <S.ViewPdfButton
                      onClick={(e) => handleViewPdf(paper, e)}
                      title="Open original PDF in new tab"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                        <polyline points="15 3 21 3 21 9"></polyline>
                        <line x1="10" y1="14" x2="21" y2="3"></line>
                      </svg>
                      PDF
                    </S.ViewPdfButton>
                    <S.DeletePaperButton
                      onClick={(e) => onConfirmDelete(paper, e)}
                      title="Delete paper"
                    >
                      ×
                    </S.DeletePaperButton>
                  </S.PaperActions>
                </>
              )}
            </S.PaperItem>
          ))}
        </S.PaperList>
      </S.HistorySection>

      <S.SidebarFooter>
        <S.CollapseButton onClick={onToggleCollapse} title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}>
          {isCollapsed ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="13 17 18 12 13 7"></polyline>
              <polyline points="6 17 11 12 6 7"></polyline>
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="11 17 6 12 11 7"></polyline>
              <polyline points="18 17 13 12 18 7"></polyline>
            </svg>
          )}
        </S.CollapseButton>
      </S.SidebarFooter>
    </S.SidebarContainer>
  );
};

export default Sidebar;
