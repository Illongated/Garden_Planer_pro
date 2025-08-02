import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Button } from '../button';

describe('Button', () => {
  it('renders the button with children', () => {
    render(<Button>Click me</Button>);
    const buttonElement = screen.getByRole('button', { name: /click me/i });
    expect(buttonElement).toBeInTheDocument();
  });

  it('applies default variants', () => {
    render(<Button>Click me</Button>);
    const buttonElement = screen.getByRole('button', { name: /click me/i });
    expect(buttonElement).toHaveClass('bg-primary text-primary-foreground');
    expect(buttonElement).toHaveClass('h-10 px-4 py-2');
  });

  it('applies specified variant', () => {
    render(<Button variant="destructive">Click me</Button>);
    const buttonElement = screen.getByRole('button', { name: /click me/i });
    expect(buttonElement).toHaveClass('bg-destructive text-destructive-foreground');
  });

  it('is disabled when the disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    const buttonElement = screen.getByRole('button', { name: /click me/i });
    expect(buttonElement).toBeDisabled();
  });
});
