import { Analytics } from '@vercel/analytics/next';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>ARIA - AI Voice Assistant Control Center</title>
        <meta name="description" content="AI Voice Assistant featuring real-time speech recognition, NLP, and system automation engine." />
      </head>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
