import "../jest.setup";
import { render, screen, waitFor } from '@testing-library/react';
import Fraud from '../src/app/fraud/page';

jest.mock('../src/lib/api/client', () => ({
  apiClient: jest.fn().mockResolvedValue({ items: [{ id: 'SIG-991', type: 'Account Takeover', severity: 'High', status: 'Open' }] }),
}));

describe('Fraud', () => {
  it('renders fraud signals', async () => {
    render(<Fraud />);
    
    expect(screen.getByText('Fraud Overview')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('SIG-991')).toBeInTheDocument();
    });
  });
});
