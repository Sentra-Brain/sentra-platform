import { createContext } from "react";
import type { ChatContextType } from "./ChatContext";

export const ChatContext = createContext<ChatContextType | undefined>(undefined);
