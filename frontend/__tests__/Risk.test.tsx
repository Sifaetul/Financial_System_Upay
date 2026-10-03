import "../jest.setup";
import { render, screen, waitFor } from '@testing-library/react';
import Risk from '../src/app/risk/page';

jest.mock('../src/lib/api/client', () => ({
  apiClient: jest.fn().mockResolvedValue({ score: '85 / 100', high_severity: '10' }),
}));

describe('Risk', () => {
  it('renders risk score', async () => {
    render(<Risk />);
    
    expect(screen.getByText('Risk Management')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('85 / 100')).toBeInTheDocument();
    });
  });
});
