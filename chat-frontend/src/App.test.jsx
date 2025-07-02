import { describe, it } from 'vitest';
import { render } from '@testing-library/react';
import App from './App';

describe('App component', () => {
  it('renders without crashing', () => {
    render(<App />);  // Added semicolon and fixed syntax
  });
});