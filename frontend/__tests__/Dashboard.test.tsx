import "../jest.setup";
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../src/app/dashboard/page';

// Mock the API client
jest.mock('../src/lib/api/client', () => ({
  apiClient: jest.fn().mockResolvedValue({ status: 'Operational', version: '1.0' }),
}));

describe('Dashboard', () => {
  it('renders the dashboard and fetches data', async () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Platform Dashboard')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Operational')).toBeInTheDocument();
    });
  });
});
