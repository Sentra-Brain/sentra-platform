import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ChatProvider } from '../src/context/ChatContext';
import { AuthContext } from '../src/context/AuthContextInstance';
import ChatArea from '../src/components/ChatArea';
import MessageInput from '../src/components/MessageInput';
import { BrowserRouter } from 'react-router-dom';

// Mock dependencies
vi.mock('../src/services/conversationService', () => ({
  conversationService: {
    list: vi.fn().mockResolvedValue([]),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
  },
}));

vi.mock('../src/services/chatService', () => ({
  chatService: {
    sendMessageStream: vi.fn(),
  },
}));

// Mock user data
const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Juan Test',
  disabled: false,
};

const mockAuthContext = {
  user: mockUser,
  logout: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
  isLoading: false,
};

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthContext.Provider value={mockAuthContext}>
      <ChatProvider>
        {children}
      </ChatProvider>
    </AuthContext.Provider>
  </BrowserRouter>
);

describe('Chat UX Improvements', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ChatArea Component', () => {
    it('should display personalized welcome message when no conversation is selected', () => {
      render(
        <TestWrapper>
          <ChatArea />
        </TestWrapper>
      );

      // Check for personalized greeting using first name
      expect(screen.getByText('Welcome back, Juan.')).toBeInTheDocument();
      expect(screen.getByText('Ask anything to start a new conversation.')).toBeInTheDocument();
    });

    it('should handle user with only username (no full_name)', () => {
      const userWithUsernameOnly = {
        ...mockUser,
        full_name: '',
        username: 'testuser',
      };

      const authContextWithUsernameOnly = {
        ...mockAuthContext,
        user: userWithUsernameOnly,
      };

      render(
        <BrowserRouter>
          <AuthContext.Provider value={authContextWithUsernameOnly}>
            <ChatProvider>
              <ChatArea />
            </ChatProvider>
          </AuthContext.Provider>
        </BrowserRouter>
      );

      // Should use capitalized username
      expect(screen.getByText('Welcome back, Testuser.')).toBeInTheDocument();
    });
  });

  describe('MessageInput Component', () => {
    it('should be enabled when no conversation is selected', () => {
      render(
        <TestWrapper>
          <MessageInput />
        </TestWrapper>
      );

      const textarea = screen.getByPlaceholderText('Ask anything to start a new conversation...');
      expect(textarea).toBeInTheDocument();
      expect(textarea).not.toBeDisabled();
    });

    it('should show helpful placeholder text when no conversation is active', () => {
      render(
        <TestWrapper>
          <MessageInput />
        </TestWrapper>
      );

      expect(screen.getByPlaceholderText('Ask anything to start a new conversation...')).toBeInTheDocument();
    });
  });
});