import React, { useState } from 'react';
import * as S from './AnimationStyles';

interface AnimationRendererProps {
  htmlContent: string;
}

const AnimationRenderer: React.FC<AnimationRendererProps> = ({ htmlContent }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <S.AnimationContainer>
      <S.AnimationHeader>
        <S.AnimationLabel>
          <S.AnimationIcon>🎬</S.AnimationIcon>
          Interactive Animation
        </S.AnimationLabel>
        <S.ExpandButton onClick={toggleExpand}>
          {isExpanded ? 'Collapse' : 'Expand'}
        </S.ExpandButton>
      </S.AnimationHeader>
      <S.AnimationIframe
        srcDoc={htmlContent}
        sandbox="allow-scripts"
        title="Animation"
        style={{ height: isExpanded ? '600px' : '400px' }}
      />
    </S.AnimationContainer>
  );
};

export default AnimationRenderer;
