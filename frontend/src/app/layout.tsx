import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'FalconXoft Hardware Store | Concurrency-Safe E-Commerce MVP',
  description: 'High-Integrity E-Commerce Store with Real-Time Stock Control, Concurrency-Safe Checkout, Mock Payment Gateway, and Order Lifecycle Management.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
