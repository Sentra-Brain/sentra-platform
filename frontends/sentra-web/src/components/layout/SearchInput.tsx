// src/components/layout/SearchInput.tsx
import { Search } from 'lucide-react';

export default function SearchInput({ value, onChange }: { value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) {
  return (
    <div className="card relative w-full max-w-md">
      <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--sentra-text)] opacity-60 pointer-events-none" />
      <input
        type="text"
        placeholder="Search..."
        value={value}
        onChange={onChange}
        className="card-input"
      />
    </div>
  );
}
