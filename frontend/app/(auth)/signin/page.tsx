import { SignInForm } from '@/components/auth/SignInForm';
import Link from 'next/link';

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 animate-fade-in">
        <div>
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-primary-light rounded-2xl flex items-center justify-center shadow-lg">
              <svg
                className="w-10 h-10 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
          </div>
          <h2 className="text-center text-3xl font-bold text-foreground">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-muted">
            Welcome back! Please enter your credentials
          </p>
        </div>

        <div className="mt-8 bg-surface py-8 px-4 shadow-lg border border-border sm:rounded-xl sm:px-10">
          <SignInForm />

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-surface text-muted">
                  Don't have an account?
                </span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                href="/signup"
                className="font-medium text-primary hover:text-primary-dark transition-colors"
              >
                Create an account
              </Link>
            </div>
          </div>
        </div>

        <div className="text-center">
          <Link
            href="/"
            className="text-sm text-muted hover:text-primary transition-colors"
          >
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
