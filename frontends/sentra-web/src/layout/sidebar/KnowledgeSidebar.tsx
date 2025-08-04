// features/knowledge/components/KnowledgeSidebar.tsx
import { BookUser, Users, Building2, type LucideIcon } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import SidebarSection from '../sidebar/Shared/SidebarSection';
import type { KnowledgeSourceVisibility } from '@features/knowledge/types/knowledgeModels';

const visibilityOptions: {
  id: KnowledgeSourceVisibility;
  label: string;
  icon: LucideIcon;
}[] = [
  { id: 'private', label: 'My Sources', icon: BookUser },
  { id: 'shared', label: 'Shared with Me', icon: Users },
  { id: 'org-wide', label: 'Organization', icon: Building2 },
];

export default function KnowledgeSidebar() {
  const { pathname } = useLocation();

  const getActiveVisibility = (): KnowledgeSourceVisibility | null => {
    if (pathname.startsWith('/k/private')) return 'private';
    if (pathname.startsWith('/k/shared')) return 'shared';
    if (pathname.startsWith('/k/org')) return 'org-wide';
    return null;
  };

  const active = getActiveVisibility();

  return (
    <SidebarSection title="Sources">
      <ul className="flex flex-col gap-1">
        {visibilityOptions.map(({ id, label, icon: Icon }) => {
          const path = `/k/${id}`;
          const isActive = active === id;

          return (
            <li key={id}>
              <Link
                to={path}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[var(--sentra-accent)] text-[var(--sentra-primary)]'
                    : 'hover:bg-[var(--sentra-primary-light)] text-[var(--sentra-neutral)]'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                <span>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </SidebarSection>
  );
}
