import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Header from '../../components/Header';

describe('Header', () => {
  it('renders the app title', () => {
    render(<Header />);
    expect(screen.getByText('Talkrates')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<Header />);
    expect(screen.getByText('The Suitable Tutor')).toBeInTheDocument();
  });

  it('renders the title inside an h1', () => {
    render(<Header />);
    const h1 = screen.getByRole('heading', { level: 1 });
    expect(h1).toBeInTheDocument();
  });
});
