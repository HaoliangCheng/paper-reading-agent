import React from 'react';
import styled from 'styled-components';
import { ModalOverlay, ModalContainer, ModalHeader, ModalBody, CloseButton, Button } from '../Common';
import { Paper } from '../../types';

const WarningIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  text-align: center;
`;

const ConfirmText = styled.p`
  font-size: 1rem;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 8px;
  line-height: 1.5;
  text-align: center;
`;

const SubText = styled.p`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: 24px;
  text-align: center;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  justify-content: center;
`;

interface DeleteModalProps {
  paper: Paper;
  onClose: () => void;
  onConfirm: () => void;
}

const DeleteModal: React.FC<DeleteModalProps> = ({
  paper,
  onClose,
  onConfirm,
}) => {
  return (
    <ModalOverlay onClick={onClose}>
      <ModalContainer maxWidth="400px" onClick={(e) => e.stopPropagation()}>
        <ModalHeader>
          <h3>Delete Paper</h3>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>
        <ModalBody>
          <WarningIcon>⚠️</WarningIcon>
          <ConfirmText>Are you sure you want to delete <strong>"{paper.title}"</strong>?</ConfirmText>
          <SubText>This action cannot be undone and all chat history will be lost.</SubText>
          
          <ActionButtons>
            <Button variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="danger" onClick={onConfirm}>
              Delete Paper
            </Button>
          </ActionButtons>
        </ModalBody>
      </ModalContainer>
    </ModalOverlay>
  );
};

export default DeleteModal;
