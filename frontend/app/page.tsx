'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { Button } from '@/components/ui/Button';
import { useEffect, useRef } from 'react';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const hasNavigated = useRef(false);

  // Prevent navigation loops
  useEffect(() => {
    hasNavigated.current = false;
  }, []);

  const handleGetStarted = () => {
    if (hasNavigated.current) return;
    hasNavigated.current = true;

    if (isAuthenticated) {
      router.push('/dashboard');
    } else {
      router.push('/signup');
    }
  };

  const handleSignIn = () => {
    if (hasNavigated.current) return;
    hasNavigated.current = true;
    router.push('/signin');
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-surface/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-light rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-white"
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
              <span className="text-xl font-semibold text-foreground">Todo App</span>
            </div>

            <div className="flex items-center gap-4">
              <ThemeToggle />
              {!isLoading && (
                <>
                  {isAuthenticated ? (
                    <Button onClick={() => router.push('/dashboard')} size="sm">
                      Dashboard
                    </Button>
                  ) : (
                    <>
                      <Button onClick={handleSignIn} variant="ghost" size="sm" className="hidden sm:inline-flex">
                        Sign In
                      </Button>
                      <Button onClick={handleGetStarted} size="sm">
                        Get Started
                      </Button>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="max-w-4xl mx-auto text-center animate-fade-in">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
            Organize Your Life with{' '}
            <span className="bg-gradient-to-r from-primary via-primary-light to-primary-lighter bg-clip-text text-transparent">
              Smart Todo Management
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-muted mb-8 max-w-2xl mx-auto leading-relaxed">
            A beautiful, intuitive task management application that helps you stay productive and organized.
            Create, manage, and complete your tasks with ease.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
            {!isLoading && (
              <>
                {isAuthenticated ? (
                  <Button onClick={() => router.push('/dashboard')} size="lg" className="w-full sm:w-auto">
                    Go to Dashboard
                  </Button>
                ) : (
                  <>
                    <Button onClick={handleGetStarted} size="lg" className="w-full sm:w-auto">
                      Get Started Free
                    </Button>
                    <Button onClick={handleSignIn} variant="secondary" size="lg" className="w-full sm:w-auto">
                      Sign In
                    </Button>
                  </>
                )}
              </>
            )}
          </div>

          {/* Feature Preview */}
          <div className="relative max-w-3xl mx-auto animate-slide-up">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-primary-light/20 to-primary-lighter/20 blur-3xl -z-10" />
            <div className="bg-surface border border-border rounded-2xl shadow-2xl p-6 sm:p-8">
              <div className="space-y-4"> 
                {[
                  { title: 'Complete project proposal', completed: true },
                  { title: 'Review team feedback', completed: true },
                  { title: 'Prepare presentation slides', completed: false },
                  { title: 'Schedule client meeting', completed: false },
                ].map((task, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-4 bg-background rounded-lg border border-border hover:border-primary transition-colors"
                  >
                    <div
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        task.completed
                          ? 'bg-primary border-primary'
                          : 'border-border'
                      }`}
                    >
                      {task.completed && (
                        <svg
                          className="w-3 h-3 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={3}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                    <span
                      className={`text-left ${
                        task.completed ? 'line-through text-muted' : 'text-foreground'
                      }`}
                    >
                      {task.title}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-20 bg-accent/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 animate-slide-up">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-4">
              Everything You Need to Stay Productive
            </h2>
            <p className="text-lg text-muted max-w-2xl mx-auto">
              Powerful features designed to help you manage tasks efficiently and achieve your goals.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4v16m8-8H4"
                  />
                ),
                title: 'Quick Task Creation',
                description: 'Add new tasks instantly with our intuitive interface. Stay focused on what matters.',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                ),
                title: 'Track Progress',
                description: 'Mark tasks as complete and visualize your productivity with clear status indicators.',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                ),
                title: 'Easy Editing',
                description: 'Update task details anytime. Keep your todo list current and relevant.',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                ),
                title: 'Secure & Private',
                description: 'Your data is protected with JWT authentication. Only you can access your tasks.',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                  />
                ),
                title: 'Dark Mode',
                description: 'Switch between light and dark themes for comfortable viewing any time of day.',
              },
              {
                icon: (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                ),
                title: 'Mobile Responsive',
                description: 'Access your tasks from any device. Fully optimized for mobile, tablet, and desktop.',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-surface border border-border rounded-xl p-6 hover:border-primary transition-all duration-300 hover:shadow-lg animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <svg
                    className="w-6 h-6 text-primary"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    {feature.icon}
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-muted leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-4xl mx-auto text-center animate-fade-in">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-6">
            Ready to Get Organized?
          </h2>
          <p className="text-lg text-muted mb-8 max-w-2xl mx-auto">
            Join thousands of users who are already managing their tasks more effectively.
          </p>
          {!isLoading && !isAuthenticated && (
            <Button onClick={handleGetStarted} size="lg">
              Start Managing Tasks Now
            </Button>
          )}
        </div>
      </section>
    </div>
  );
}
