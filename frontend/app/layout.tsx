import type { Metadata } from 'next';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'ClaimInvestigator AI | Insurance Claims Investigation Assistant',
  description: 'AI-powered claims investigation workflow assistant for insurance professionals',
  keywords: ['insurance', 'claims', 'investigation', 'AI', 'workflow', 'FNOL'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-gray-50">
        <Providers>
          <div className="min-h-full">
            {/* Navigation */}
            <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  {/* Logo */}
                  <div className="flex items-center">
                    <a href="/" className="flex items-center space-x-3">
                      <div className="w-9 h-9 bg-gradient-to-br from-brand-600 to-brand-800 rounded-lg flex items-center justify-center">
                        <svg
                          className="w-5 h-5 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                      <span className="text-xl font-semibold text-gray-900">
                        ClaimInvestigator<span className="text-brand-600">AI</span>
                      </span>
                    </a>
                  </div>

                  {/* Navigation Links */}
                  <div className="hidden sm:flex sm:items-center sm:space-x-1">
                    <a
                      href="/dashboard"
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-brand-600 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      Dashboard
                    </a>
                    <a
                      href="/dashboard#investigate"
                      className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-brand-600 hover:bg-gray-50 rounded-lg transition-colors"
                    >
                      Investigate Claim
                    </a>
                  </div>

                  {/* Right side */}
                  <div className="flex items-center space-x-4">
                    <span className="badge-blue">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
                      AI Ready
                    </span>
                  </div>
                </div>
              </div>
            </nav>

            {/* Main content */}
            <main>{children}</main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 mt-auto">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
                  <p className="text-sm text-gray-500">
                    ClaimInvestigator AI — Training & Workflow Support Tool
                  </p>
                  <p className="text-xs text-gray-400">
                    Uses synthetic data only. Not for production claims.
                  </p>
                </div>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}