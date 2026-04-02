import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ConversationList from '../../components/ConversationList';
import type { Conversation, Conversations } from '../../types/conversation';

vi.mock('../../api/conversationApi', () => ({
  deleteConversation: vi.fn(),
}));

import { deleteConversation } from '../../api/conversationApi';
const mockDelete = vi.mocked(deleteConversation);

const conv1: Conversation = { history: [{ role: 'user', content: 'Hi' }], summary: 'First chat' };
const conv2: Conversation = { history: [], summary: null };

const conversations: Conversations = {
  'id-1': conv1,
  'id-2': conv2,
};

function buildProps(overrides: Partial<Parameters<typeof ConversationList>[0]> = {}) {
  return {
    conversations,
    setConversations: vi.fn<[React.SetStateAction<Conversations>]>(),
    currConversationId: '',
    setCurrConversationId: vi.fn(),
    setCurrConversation: vi.fn<[React.SetStateAction<Conversation>]>(),
    removeIdFromStorage: vi.fn(),
    ...overrides,
  };
}

beforeEach(() => vi.clearAllMocks());

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------
describe('ConversationList rendering', () => {
  it('renders a list item for each conversation', () => {
    render(<ConversationList {...buildProps()} />);
    // Two conversations + the "New conversation" link
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(3);
  });

  it('shows the summary when available', () => {
    render(<ConversationList {...buildProps()} />);
    expect(screen.getByText('First chat')).toBeInTheDocument();
  });

  it('falls back to the conversation ID when summary is null', () => {
    render(<ConversationList {...buildProps()} />);
    expect(screen.getByText('id-2')).toBeInTheDocument();
  });

  it('renders the "New conversation" link', () => {
    render(<ConversationList {...buildProps()} />);
    expect(screen.getByText('+ New conversation')).toBeInTheDocument();
  });

  it('applies the active class to the current conversation link', () => {
    render(<ConversationList {...buildProps({ currConversationId: 'id-1' })} />);
    const activeLink = screen.getByText('First chat');
    expect(activeLink).toHaveClass('active');
  });

  it('does not apply the active class to non-current conversations', () => {
    render(<ConversationList {...buildProps({ currConversationId: 'id-1' })} />);
    const inactiveLink = screen.getByText('id-2');
    expect(inactiveLink).not.toHaveClass('active');
  });
});

// ---------------------------------------------------------------------------
// Switching conversations
// ---------------------------------------------------------------------------
describe('switching conversations', () => {
  it('calls setCurrConversationId with the clicked conversation ID', async () => {
    const user = userEvent.setup();
    const setCurrConversationId = vi.fn();
    render(<ConversationList {...buildProps({ setCurrConversationId })} />);

    await user.click(screen.getByText('First chat'));

    expect(setCurrConversationId).toHaveBeenCalledWith('id-1');
  });

  it('calls setCurrConversation with the conversation data when switching', async () => {
    const user = userEvent.setup();
    const setCurrConversation = vi.fn();
    render(<ConversationList {...buildProps({ setCurrConversation })} />);

    await user.click(screen.getByText('First chat'));

    expect(setCurrConversation).toHaveBeenCalledWith(conv1);
  });

  it('does not switch when clicking the already-active conversation', async () => {
    const user = userEvent.setup();
    const setCurrConversationId = vi.fn();
    render(<ConversationList {...buildProps({ currConversationId: 'id-1', setCurrConversationId })} />);

    await user.click(screen.getByText('First chat'));

    expect(setCurrConversationId).not.toHaveBeenCalled();
  });

  it('resets state when clicking "New conversation"', async () => {
    const user = userEvent.setup();
    const setCurrConversationId = vi.fn();
    const setCurrConversation = vi.fn();
    render(<ConversationList {...buildProps({ currConversationId: 'id-1', setCurrConversationId, setCurrConversation })} />);

    await user.click(screen.getByText('+ New conversation'));

    expect(setCurrConversationId).toHaveBeenCalledWith('');
    expect(setCurrConversation).toHaveBeenCalledWith({ history: [], summary: null });
  });
});

// ---------------------------------------------------------------------------
// Deleting conversations
// ---------------------------------------------------------------------------
describe('deleting conversations', () => {
  it('calls deleteConversation API with the conversation ID', async () => {
    const user = userEvent.setup();
    mockDelete.mockResolvedValueOnce();
    render(<ConversationList {...buildProps()} />);

    const deleteForms = screen.getAllByRole('button', { name: '×' });
    await user.click(deleteForms[0]);

    await waitFor(() => expect(mockDelete).toHaveBeenCalledWith('id-1'));
  });

  it('calls removeIdFromStorage after successful deletion', async () => {
    const user = userEvent.setup();
    const removeIdFromStorage = vi.fn();
    mockDelete.mockResolvedValueOnce();
    render(<ConversationList {...buildProps({ removeIdFromStorage })} />);

    await user.click(screen.getAllByRole('button', { name: '×' })[0]);

    await waitFor(() => expect(removeIdFromStorage).toHaveBeenCalledWith('id-1'));
  });

  it('removes the conversation from state after deletion', async () => {
    const user = userEvent.setup();
    const setConversations = vi.fn();
    mockDelete.mockResolvedValueOnce();
    render(<ConversationList {...buildProps({ setConversations })} />);

    await user.click(screen.getAllByRole('button', { name: '×' })[0]);

    await waitFor(() => expect(setConversations).toHaveBeenCalled());
    const updatedConvos: Conversations = setConversations.mock.calls[0][0] as Conversations;
    expect(updatedConvos).not.toHaveProperty('id-1');
    expect(updatedConvos).toHaveProperty('id-2');
  });

  it('resets the current conversation when the active one is deleted', async () => {
    const user = userEvent.setup();
    const setCurrConversationId = vi.fn();
    const setCurrConversation = vi.fn();
    mockDelete.mockResolvedValueOnce();

    render(<ConversationList {...buildProps({
      currConversationId: 'id-1',
      setCurrConversationId,
      setCurrConversation,
    })} />);

    await user.click(screen.getAllByRole('button', { name: '×' })[0]);

    await waitFor(() => expect(setCurrConversationId).toHaveBeenCalledWith(''));
    expect(setCurrConversation).toHaveBeenCalledWith({ history: [], summary: null });
  });

  it('does not reset current conversation when a different one is deleted', async () => {
    const user = userEvent.setup();
    const setCurrConversationId = vi.fn();
    mockDelete.mockResolvedValueOnce();

    render(<ConversationList {...buildProps({
      currConversationId: 'id-2',
      setCurrConversationId,
    })} />);

    // Delete id-1 (the first delete button)
    await user.click(screen.getAllByRole('button', { name: '×' })[0]);

    await waitFor(() => expect(mockDelete).toHaveBeenCalled());
    expect(setCurrConversationId).not.toHaveBeenCalled();
  });
});
