import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ModalOverlay, ModalContainer, ModalHeader, ModalBody, Input, Button } from '../Common';
import { UserProfile } from '../../types';

const FormLabel = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
  margin-bottom: 8px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const KeyPointsSection = styled.div`
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid ${props => props.theme.colors.borderColor};
`;

const KeyPointsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
`;

const KeyPointsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
`;

const KeyPointTag = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: ${props => props.theme.colors.bgHover};
  border: 1px solid ${props => props.theme.colors.borderColor};
  border-radius: 9999px;
  font-size: 0.8125rem;
  color: ${props => props.theme.colors.textPrimary};
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.theme.colors.textTertiary};
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: ${props => props.theme.colors.danger};
  }
`;

const AddKeyPointRow = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const SmallInput = styled(Input)`
  flex: 1;
  padding: 8px 12px;
  font-size: 0.875rem;
`;

const SmallButton = styled.button`
  padding: 8px 16px;
  border-radius: ${props => props.theme.borderRadius.md};
  background-color: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;

  &:hover {
    background-color: ${props => props.theme.colors.primaryHover};
  }

  &:disabled {
    background-color: #cbd5e1;
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

const EmptyState = styled.div`
  font-size: 0.8125rem;
  color: ${props => props.theme.colors.textTertiary};
  font-style: italic;
`;

const HelpText = styled.p`
  font-size: 0.75rem;
  color: ${props => props.theme.colors.textTertiary};
  margin-top: 4px;
`;

const FooterActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
`;

interface ProfileModalProps {
  profile: UserProfile;
  onClose: () => void;
  onSave: (profile: UserProfile) => void;
}

const ProfileModal: React.FC<ProfileModalProps> = ({
  profile,
  onClose,
  onSave,
}) => {
  const [name, setName] = useState(profile.name || '');
  const [keyPoints, setKeyPoints] = useState<string[]>(profile.key_points || []);
  const [newKeyPoint, setNewKeyPoint] = useState('');

  useEffect(() => {
    setName(profile.name || '');
    setKeyPoints(profile.key_points || []);
  }, [profile]);

  const handleAddKeyPoint = () => {
    if (newKeyPoint.trim() && !keyPoints.includes(newKeyPoint.trim())) {
      const updatedKeyPoints = [...keyPoints, newKeyPoint.trim()];
      setKeyPoints(updatedKeyPoints);
      setNewKeyPoint('');
      
      // Auto-update backend when adding
      onSave({
        name: name.trim(),
        key_points: updatedKeyPoints,
      });
    }
  };

  const handleRemoveKeyPoint = (index: number) => {
    const updatedKeyPoints = keyPoints.filter((_, i) => i !== index);
    setKeyPoints(updatedKeyPoints);
    
    // Auto-update backend when removing
    onSave({
      name: name.trim(),
      key_points: updatedKeyPoints,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddKeyPoint();
    }
  };

  const handleSave = () => {
    onSave({
      name: name.trim(),
      key_points: keyPoints,
    });
    onClose();
  };

  return (
    <ModalOverlay>
      <ModalContainer maxWidth="520px">
        <ModalHeader>
          <h3>User Profile</h3>
        </ModalHeader>

        <ModalBody>
          <FormGroup>
            <FormLabel>Name (optional)</FormLabel>
            <Input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </FormGroup>

          <KeyPointsSection style={{ marginTop: 0, paddingTop: 0, borderTop: 'none' }}>
            <KeyPointsHeader>
              <FormLabel style={{ marginBottom: 0 }}>Key Insights</FormLabel>
            </KeyPointsHeader>
            <HelpText style={{ marginTop: 0, marginBottom: 12 }}>
              The AI automatically learns about your interests from your questions. You can also add or remove insights manually.
            </HelpText>

            <KeyPointsList>
              {keyPoints.length === 0 ? (
                <EmptyState>No key insights yet. The AI will add them as you chat.</EmptyState>
              ) : (
                keyPoints.map((point, index) => (
                  <KeyPointTag key={index}>
                    {point}
                    <RemoveButton onClick={() => handleRemoveKeyPoint(index)} title="Remove">
                      x
                    </RemoveButton>
                  </KeyPointTag>
                ))
              )}
            </KeyPointsList>

            <AddKeyPointRow>
              <SmallInput
                type="text"
                placeholder="Add a key insight..."
                value={newKeyPoint}
                onChange={(e) => setNewKeyPoint(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <SmallButton
                onClick={handleAddKeyPoint}
                disabled={!newKeyPoint.trim()}
              >
                Add
              </SmallButton>
            </AddKeyPointRow>
          </KeyPointsSection>

          <FooterActions>
            <Button variant="secondary" onClick={onClose} style={{ flex: 1 }}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSave} style={{ flex: 2 }}>
              Save Profile
            </Button>
          </FooterActions>
        </ModalBody>
      </ModalContainer>
    </ModalOverlay>
  );
};

export default ProfileModal;
