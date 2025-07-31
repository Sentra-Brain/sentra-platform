// src/hooks/useKnowledgeSources.ts
// Simple state management for knowledge sources
import { useState, useEffect, useCallback } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { notifyError } from '../lib/notify';
import type { KnowledgeSource, CreateKnowledgeSourceRequest } from '../models/knowledgeModels';

export const useKnowledgeSources = () => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSources = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await knowledgeService.listKnowledgeSources();
      setSources(response.sources);
    } catch (err) {
      const errorMessage = 'Failed to load knowledge sources';
      setError(errorMessage);
      notifyError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createSource = useCallback(async (data: CreateKnowledgeSourceRequest): Promise<KnowledgeSource> => {
    const newSource = await knowledgeService.createKnowledgeSource(data);
    setSources(prev => [...prev, newSource]);
    return newSource;
  }, []);

  const updateSourceStatus = useCallback(async (sourceId: string, enabled: boolean): Promise<void> => {
    const updatedSource = await knowledgeService.updateKnowledgeSourceStatus(sourceId, enabled);
    setSources(prev => prev.map(s => s.id === sourceId ? updatedSource : s));
  }, []);

  const getSourceById = useCallback((sourceId: string): KnowledgeSource | undefined => {
    return sources.find(s => s.id === sourceId);
  }, [sources]);

  const getUserUploadSource = useCallback((): KnowledgeSource | undefined => {
    return sources.find(source => 
      source.visibility === 'private' && 
      source.type === 'upload'
    );
  }, [sources]);

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  return {
    sources,
    loading,
    error,
    loadSources,
    createSource,
    updateSourceStatus,
    getSourceById,
    getUserUploadSource,
    refresh: loadSources,
  };
};