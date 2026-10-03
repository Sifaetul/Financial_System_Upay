import "../jest.setup";
import { render, screen, waitFor } from '@testing-library/react';
import Transactions from '../src/app/transactions/page';

jest.mock('../src/lib/api/client', () => ({
  apiClient: jest.fn().mockResolvedValue({ items: [{ id: 'TX-1001', date: '2026-10-01', amount: '$150.00', status: 'Completed' }] }),
}));

describe('Transactions', () => {
  it('renders transactions table', async () => {
    render(<Transactions />);
    
    expect(screen.getByText('Transactions')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('TX-1001')).toBeInTheDocument();
    });
  });
});
