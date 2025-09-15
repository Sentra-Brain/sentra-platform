import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@store/hooks';
import { fetchAgents, selectAgent } from '../agentsSlice';

export function AgentSelector() {
  const dispatch = useAppDispatch();
  const { available, loading, error, selected } = useAppSelector(s => s.agents);

  useEffect(() => {
    if (!available.length && !loading) {
      dispatch(fetchAgents());
    }
  }, [available.length, loading, dispatch]);

  if (loading && !available.length) return <div className="text-sm text-gray-500">Loading agents...</div>;
  if (error) return <div className="text-sm text-red-500">Failed to load agents</div>;

  return (
    <div className="flex items-center gap-2">
      <label className="text-xs font-medium text-gray-500">Agent:</label>
      <select
        value={selected || ''}
        onChange={e => dispatch(selectAgent(e.target.value))}
        className="border rounded px-2 py-1 text-sm"
      >
        {available.map((a: string) => (
          <option key={a} value={a}>{a}</option>
        ))}
      </select>
    </div>
  );
}

export default AgentSelector;
