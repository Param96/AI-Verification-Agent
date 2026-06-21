import "./globals.css";

export const metadata = {
  title: "Enterprise Verify Platform",
  description: "AI-powered Document Intelligence & Verification",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header className="glass-header animate-fade-in">
          <div className="brand">Verify.ai</div>
          <nav style={{ display: 'flex', gap: '1.5rem', color: 'var(--text-secondary)' }}>
            <a href="#" style={{ color: 'var(--text-primary)' }}>Dashboard</a>
            <a href="#">Jobs</a>
            <a href="#">Settings</a>
          </nav>
        </header>
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
