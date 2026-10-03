import "../jest.setup";
import { render, screen, waitFor } from '@testing-library/react';
import Alerts from '../src/app/alerts/page';

jest.mock('../src/lib/api/client', () => ({
  apiClient: jest.fn().mockResolvedValue([{ id: "123", type: "System error", severity: "HIGH", status: "OPEN" }]),
}));

describe('Alerts', () => {
  it('renders alerts list', async () => {
    render(<Alerts />);
    expect(screen.getByText('Ops Alerts')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/System error/i)).toBeInTheDocument();
    });
  });
});
