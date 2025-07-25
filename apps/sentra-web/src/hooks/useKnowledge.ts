import { useContext } from 'react';
import { KnowledgeContext } from '../context/KnowledgeContextInstance';

export const useKnowledge = () => {
  const context = useContext(KnowledgeContext);
  if (!context) throw new Error('useKnowledge must be used within a KnowledgeProvider');
  return context;
};