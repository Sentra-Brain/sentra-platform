// src/layout/SearchInput.tsx
import { Search } from 'lucide-react';
import { useState } from 'react';

export default function SearchInput() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="relative w-full max-w-md hidden sm:flex">
      <Search
        size={16}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--sentra-text)] opacity-60 pointer-events-none"
      />
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search..."
        aria-label="Global search"
        className="
          w-full bg-[var(--sentra-primary)] 
          border border-[var(--sentra-primary-light)] 
          pl-10 pr-3 py-2 
          text-sm text-[var(--sentra-text)] 
          rounded transition 
          placeholder:text-[var(--sentra-text)] placeholder:opacity-60 
          focus:outline-none focus:border-[var(--sentra-accent)] focus:ring-1/2 focus:ring-[var(--sentra-accent)]
        "
      />
    </div>
  );
}
