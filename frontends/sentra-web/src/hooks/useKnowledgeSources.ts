// src/hooks/useKnowledgeSources.ts
// Simple state management for knowledge sources with request deduplication
import { useState, useEffect, useCallback, useRef } from 'react';
import { knowledgeService } from '../services/knowledgeService';
import { notifyError } from '../lib/notify';
import { requestCache } from '../lib/requestCache';
import type { KnowledgeSource, CreateKnowledgeSourceRequest } from '../models/knowledgeModels';

export const useKnowledgeSources = () => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initializedRef = useRef(false);

  const loadSources = useCallback(async () => {
    try {
      // Use request cache to prevent duplicate concurrent calls
      const response = await requestCache.get(
        'knowledge/sources',
        () => knowledgeService.listKnowledgeSources(),
        { ttl: 2 * 60 * 1000 } // Cache for 2 minutes
      );
      setSources(response.sources);
      setError(null);
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
    // Invalidate cache since we have new data
    requestCache.invalidate('knowledge/sources');
    return newSource;
  }, []);

  const updateSourceStatus = useCallback(async (sourceId: string, enabled: boolean): Promise<void> => {
    const updatedSource = await knowledgeService.updateKnowledgeSourceStatus(sourceId, enabled);
    setSources(prev => prev.map(s => s.id === sourceId ? updatedSource : s));
    // Invalidate cache since we have updated data
    requestCache.invalidate('knowledge/sources');
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
    // Only load once to prevent multiple calls on every render
    if (!initializedRef.current) {
      initializedRef.current = true;
      console.log('[useKnowledgeSources] Initial load');
      loadSources();
    }
  }, []); // Empty dependencies to run only once

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