import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import DialogBox from '../../components/DialogBox';
import type { Conversation } from '../../types/conversation';

vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <span>{children}</span>,
}));

const emptyConversation: Conversation = { history: [], summary: null };

const filledConversation: Conversation = {
  history: [
    { role: 'user', content: 'What is Plato famous for?' },
    { role: 'assistant', content: 'Plato is famous for his theory of Forms.' },
  ],
  summary: null,
};

describe('DialogBox', () => {
  it('renders an empty list when there are no messages', () => {
    render(<DialogBox currConversation={emptyConversation} isThinking={false} />);
    const list = screen.getByRole('list');
    // Only the thinking indicator could be present, but isThinking=false so list is empty
    expect(list).toBeEmptyDOMElement();
  });

  it('renders a message item for each history entry', () => {
    render(<DialogBox currConversation={filledConversation} isThinking={false} />);
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(2);
  });

  it('labels user messages as "You"', () => {
    render(<DialogBox currConversation={filledConversation} isThinking={false} />);
    expect(screen.getByText('You')).toBeInTheDocument();
  });

  it('labels assistant messages as "Talkrates"', () => {
    render(<DialogBox currConversation={filledConversation} isThinking={false} />);
    expect(screen.getAllByText('Talkrates').length).toBeGreaterThan(0);
  });

  it('sets data-role attribute correctly on message items', () => {
    render(<DialogBox currConversation={filledConversation} isThinking={false} />);
    const items = screen.getAllByRole('listitem');
    expect(items[0]).toHaveAttribute('data-role', 'user');
    expect(items[1]).toHaveAttribute('data-role', 'assistant');
  });

  it('renders message content', () => {
    render(<DialogBox currConversation={filledConversation} isThinking={false} />);
    expect(screen.getByText('What is Plato famous for?')).toBeInTheDocument();
    expect(screen.getByText('Plato is famous for his theory of Forms.')).toBeInTheDocument();
  });

  it('shows the thinking indicator when isThinking is true', () => {
    render(<DialogBox currConversation={emptyConversation} isThinking={true} />);
    expect(screen.getByText('Talkrates')).toBeInTheDocument();
    expect(screen.getByText('Thinking')).toBeInTheDocument();
  });

  it('does not show the thinking indicator when isThinking is false', () => {
    render(<DialogBox currConversation={emptyConversation} isThinking={false} />);
    expect(screen.queryByText('Thinking')).not.toBeInTheDocument();
  });

  it('thinking indicator has the assistant data-role', () => {
    render(<DialogBox currConversation={emptyConversation} isThinking={true} />);
    const thinkingItem = screen.getByText('Thinking').closest('li');
    expect(thinkingItem).toHaveAttribute('data-role', 'assistant');
  });
});
