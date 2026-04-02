import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import QueryForm from '../../components/QueryForm';
import type { Conversation, Conversations } from '../../types/conversation';

vi.mock('../../api/conversationApi', () => ({
  postQuery: vi.fn(),
}));

import { postQuery } from '../../api/conversationApi';
const mockPostQuery = vi.mocked(postQuery);

const emptyConversation: Conversation = { history: [], summary: null };

function buildProps(overrides: Partial<Parameters<typeof QueryForm>[0]> = {}) {
  return {
    currConversation: emptyConversation,
    setCurrConversation: vi.fn(),
    setConversations: vi.fn<[React.SetStateAction<Conversations>]>(),
    currConversationId: '',
    setCurrConversationId: vi.fn(),
    addIdToStorage: vi.fn(),
    setIsThinking: vi.fn(),
    ...overrides,
  };
}

beforeEach(() => vi.clearAllMocks());

describe('QueryForm rendering', () => {
  it('renders the textarea', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByPlaceholderText('Ask a question...')).toBeInTheDocument();
  });

  it('renders the submit button', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument();
  });

  it('renders the mode labels', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByText('Instruction')).toBeInTheDocument();
    expect(screen.getByText('Dialogue')).toBeInTheDocument();
  });

  it('renders the mode toggle checkbox', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  it('submit button is enabled initially', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled();
  });
});

describe('QueryForm interactions', () => {
  it('updates textarea as user types', async () => {
    const user = userEvent.setup();
    render(<QueryForm {...buildProps()} />);
    const textarea = screen.getByPlaceholderText('Ask a question...');

    await user.type(textarea, 'Hello world');

    expect(textarea).toHaveValue('Hello world');
  });

  it('toggle is unchecked (Instruction mode) by default', () => {
    render(<QueryForm {...buildProps()} />);
    expect(screen.getByRole('checkbox')).not.toBeChecked();
  });

  it('toggle becomes checked when clicked (switches to Dialogue mode)', async () => {
    const user = userEvent.setup();
    render(<QueryForm {...buildProps()} />);
    const toggle = screen.getByRole('checkbox');

    await user.click(toggle);

    expect(toggle).toBeChecked();
  });

  it('submit button shows "..." and is disabled while submitting', async () => {
    const user = userEvent.setup();
    let resolveQuery!: (v: unknown) => void;
    mockPostQuery.mockReturnValueOnce(new Promise(res => { resolveQuery = res; }) as ReturnType<typeof postQuery>);

    render(<QueryForm {...buildProps()} />);
    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A question');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(screen.getByRole('button', { name: '...' })).toBeDisabled();

    resolveQuery({
      role: 'assistant',
      content: 'Answer',
      conversation_id: 'conv-1',
      summary: null,
    });

    await waitFor(() => expect(screen.getByRole('button', { name: 'Submit' })).not.toBeDisabled());
  });
});

describe('QueryForm submission', () => {
  const serverResponse = {
    role: 'assistant' as const,
    content: 'Consciousness is a hard problem.',
    conversation_id: 'new-conv-id',
    summary: null,
  };

  it('calls postQuery with the typed content', async () => {
    const user = userEvent.setup();
    mockPostQuery.mockResolvedValueOnce(serverResponse);
    render(<QueryForm {...buildProps()} />);

    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A question');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(mockPostQuery).toHaveBeenCalledOnce());
    expect(mockPostQuery).toHaveBeenCalledWith(
      expect.objectContaining({ content: 'A question', role: 'user' })
    );
  });

  it('passes dialogue_mode=true when toggle is on', async () => {
    const user = userEvent.setup();
    mockPostQuery.mockResolvedValueOnce(serverResponse);
    render(<QueryForm {...buildProps()} />);

    await user.click(screen.getByRole('checkbox'));
    await user.type(screen.getByPlaceholderText('Ask a question...'), 'Test');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(mockPostQuery).toHaveBeenCalledOnce());
    expect(mockPostQuery).toHaveBeenCalledWith(
      expect.objectContaining({ dialogue_mode: true })
    );
  });

  it('clears the textarea after submission', async () => {
    const user = userEvent.setup();
    mockPostQuery.mockResolvedValueOnce(serverResponse);
    render(<QueryForm {...buildProps()} />);

    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A question');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(screen.getByPlaceholderText('Ask a question...')).toHaveValue(''));
  });

  it('calls setIsThinking(true) before the query and setIsThinking(false) after', async () => {
    const user = userEvent.setup();
    const setIsThinking = vi.fn();
    mockPostQuery.mockResolvedValueOnce(serverResponse);
    render(<QueryForm {...buildProps({ setIsThinking })} />);

    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A question');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(setIsThinking).toHaveBeenCalledWith(false));
    expect(setIsThinking.mock.calls[0][0]).toBe(true);
    expect(setIsThinking.mock.calls[1][0]).toBe(false);
  });

  it('stores the new conversation ID when starting a fresh conversation', async () => {
    const user = userEvent.setup();
    const addIdToStorage = vi.fn();
    const setCurrConversationId = vi.fn();
    mockPostQuery.mockResolvedValueOnce(serverResponse);

    render(<QueryForm {...buildProps({ addIdToStorage, setCurrConversationId, currConversationId: '' })} />);

    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A question');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(addIdToStorage).toHaveBeenCalledWith('new-conv-id'));
    expect(setCurrConversationId).toHaveBeenCalledWith('new-conv-id');
  });

  it('does not call addIdToStorage when continuing an existing conversation', async () => {
    const user = userEvent.setup();
    const addIdToStorage = vi.fn();
    mockPostQuery.mockResolvedValueOnce({ ...serverResponse, conversation_id: 'existing-id' });

    render(<QueryForm {...buildProps({ addIdToStorage, currConversationId: 'existing-id' })} />);

    await user.type(screen.getByPlaceholderText('Ask a question...'), 'A follow-up');
    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => expect(mockPostQuery).toHaveBeenCalled());
    expect(addIdToStorage).not.toHaveBeenCalled();
  });
});
