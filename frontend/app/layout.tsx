import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Zomma Quant - Professional Trading Platform',
  description: 'Advanced quantitative trading platform for professional traders',
  icons: {
    icon: [
      { url: '/Logofiles/For Web/Favicons/browser.png', sizes: '32x32', type: 'image/png' },
      { url: '/Logofiles/For Web/Favicons/Android.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: [
      { url: '/Logofiles/For Web/Favicons/iPhone.png', sizes: '180x180', type: 'image/png' },
    ],
    shortcut: '/Logofiles/For Web/Favicons/browser.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}