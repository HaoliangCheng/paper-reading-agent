import React from 'react';
import styled from 'styled-components';
import { ModalOverlay, ModalContainer, ModalHeader, ModalBody, CloseButton, Input, Select, Button } from '../Common';

const Tabs = styled.div`
  display: flex;
  padding: 4px;
  background-color: ${props => props.theme.colors.bgHover};
  margin-bottom: 20px;
  border-radius: ${props => props.theme.borderRadius.lg};
`;

const TabButton = styled.button<{ active: boolean }>`
  flex: 1;
  padding: 8px;
  border: none;
  background: ${props => props.active ? props.theme.colors.bgSecondary : 'none'};
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  cursor: pointer;
  border-radius: ${props => props.theme.borderRadius.md};
  transition: all 0.2s;
  box-shadow: ${props => props.active ? `0 1px 3px ${props.theme.colors.shadow}` : 'none'};
`;

const FileDropZone = styled.div<{ disabled: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border: 2px dashed ${props => props.theme.colors.borderColor};
  border-radius: ${props => props.theme.borderRadius.xl};
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.2s;
  height: 120px;
  background-color: ${props => props.theme.colors.bgSecondary};
  opacity: ${props => props.disabled ? 0.6 : 1};

  &:hover {
    border-color: ${props => !props.disabled && props.theme.colors.primary};
    background-color: ${props => !props.disabled && props.theme.colors.bgHover};
  }
`;

const LoadingSpinner = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &::after {
    content: "";
    width: 16px;
    height: 16px;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

interface UploadModalProps {
  isLoading: boolean;
  uploadTab: 'file' | 'link';
  setUploadTab: (tab: 'file' | 'link') => void;
  selectedFile: File | null;
  paperUrl: string;
  setPaperUrl: (url: string) => void;
  selectedLanguage: string;
  setSelectedLanguage: (lang: string) => void;
  thinkingStage: string;
  onClose: () => void;
  onAnalyze: () => void;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  fileInputRef: React.RefObject<any>;
}

const UploadModal: React.FC<UploadModalProps> = ({
  isLoading,
  uploadTab,
  setUploadTab,
  selectedFile,
  paperUrl,
  setPaperUrl,
  selectedLanguage,
  setSelectedLanguage,
  thinkingStage,
  onClose,
  onAnalyze,
  onFileChange,
  fileInputRef,
}) => {
  const triggerFileInput = () => {
    if (!isLoading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const languages = ['English', '中文'];

  return (
    <ModalOverlay onClick={() => !isLoading && onClose()}>
      <ModalContainer onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <h3>Add New Paper</h3>
          {!isLoading && <CloseButton onClick={onClose}>×</CloseButton>}
        </ModalHeader>
        
        <ModalBody>
          <Tabs>
            <TabButton 
              active={uploadTab === 'file'}
              onClick={() => setUploadTab('file')}
              disabled={isLoading}
            >
              Upload File
            </TabButton>
            <TabButton 
              active={uploadTab === 'link'}
              onClick={() => setUploadTab('link')}
              disabled={isLoading}
            >
              Paste Link
            </TabButton>
          </Tabs>

          {uploadTab === 'file' ? (
            <div style={{ height: '120px' }}>
              <input
                type="file"
                accept=".pdf"
                onChange={onFileChange}
                ref={fileInputRef}
                style={{ display: 'none' }}
                id="modal-file-upload"
              />
              <FileDropZone 
                onClick={triggerFileInput} 
                disabled={isLoading}
              >
                <div style={{ fontSize: '32px', marginBottom: '8px' }}>📁</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                  {selectedFile ? selectedFile.name : 'Choose PDF'}
                </div>
              </FileDropZone>
            </div>
          ) : (
            <div style={{ height: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <Input
                type="text"
                placeholder="Paste PDF link (e.g. ArXiv URL)"
                value={paperUrl}
                onChange={(e) => setPaperUrl(e.target.value)}
                disabled={isLoading}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '8px', marginLeft: '4px' }}>
                Tip: ArXiv abstract links work automatically!
              </p>
            </div>
          )}

          <div style={{ marginTop: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
              Output Language:
            </label>
            <Select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              disabled={isLoading}
            >
              {languages.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </Select>
          </div>

          <Button
            onClick={onAnalyze}
            disabled={isLoading || (uploadTab === 'file' ? !selectedFile : !paperUrl.trim())}
            style={{ width: '100%', marginTop: '24px', height: '48px' }}
          >
            {isLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
                <LoadingSpinner />
                <span>{thinkingStage || 'Analyzing Paper...'}</span>
              </div>
            ) : (
              'Analyze and Add'
            )}
          </Button>
          
          {isLoading && (
            <p style={{ marginTop: '12px', fontSize: '0.8125rem', color: 'var(--text-secondary)', textAlign: 'center', lineHeight: 1.4 }}>
              This process usually takes about 1 minute. Please don't close this window.
            </p>
          )}
        </ModalBody>
      </ModalContainer>
    </ModalOverlay>
  );
};

export default UploadModal;
