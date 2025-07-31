import { createContext } from "react";
import type { KnowledgeContextType } from "./KnowledgeContext";

export const KnowledgeContext = createContext<KnowledgeContextType | undefined>(undefined);