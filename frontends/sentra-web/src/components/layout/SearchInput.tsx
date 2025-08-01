// src/components/layout/SearchInput.tsx
import { Search } from 'lucide-react';

export default function SearchInput({ value, onChange }: { value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void }) {
  return (
    <div className="relative w-full max-w-md">
      <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--sentra-text)] opacity-60 pointer-events-none" />
      <input
        type="text"
        placeholder="Search..."
        value={value}
        onChange={onChange}
        className="w-full bg-[var(--sentra-primary)] border border-[var(--sentra-primary-light)] rounded pl-10 pr-3 py-2 text-sm text-[var(--sentra-text)] placeholder:text-[var(--sentra-text)] placeholder:opacity-60 focus:outline-none focus:border-[var(--sentra-accent)] focus:ring-2 focus:ring-[var(--sentra-accent)] transition"
      />
    </div>
  );
}
