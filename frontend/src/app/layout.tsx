import '@/styles/global.css';

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ subsets: ['latin'] });

import faviconBrowser from '../../public/logoFiles/web/favicons/browser.png';
import faviconAndroid from '../../public/logoFiles/web/favicons/android.png';
import faviconIphone from '../../public/logoFiles/web/favicons/iphone.png';

export const metadata: Metadata = {
  title: 'Zomma Quant - Professional Trading Platform',
  description:
    'Advanced quantitative trading platform for professional traders',
  icons: {
    icon: [
      {
        url: faviconBrowser.src,
        sizes: '32x32',
        type: 'image/png',
      },
      {
        url: faviconAndroid.src,
        sizes: '192x192',
        type: 'image/png',
      },
    ],
    apple: [
      {
        url: faviconIphone.src,
        sizes: '180x180',
        type: 'image/png',
      },
    ],
    shortcut: faviconBrowser.src,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='pt-BR' suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute='class'
          defaultTheme='dark'
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
