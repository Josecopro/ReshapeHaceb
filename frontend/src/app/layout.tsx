import type { Metadata } from 'next';
import '@/styles/global.scss';

export const metadata: Metadata = {
  title: 'Chain of Thought Visualizer | Reshape',
  description: 'Interactive 3D graph visualizer for AI Agent Chain of Thought reasoning.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
