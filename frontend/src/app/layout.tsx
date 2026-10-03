import './globals.css';
import { AppShell } from '@/components/AppShell';
import { AuthProvider } from '@/lib/auth';

export const metadata = {
  title: 'UPAY NEXUS AI',
  description: 'Fintech intelligence platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <AppShell>
            {children}
          </AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
