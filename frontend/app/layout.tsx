import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import { Footer } from "@/components/layout/Footer";
import { Toaster } from "sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Todo App - Smart Task Management",
  description: "A beautiful, intuitive task management application that helps you stay productive and organized. Create, manage, and complete your tasks with ease.",
  keywords: ["todo", "task management", "productivity", "organization"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <ThemeProvider>
          <AuthProvider>
            <div className="flex-1 flex flex-col">
              {children}
            </div>
            <Footer />
            <Toaster
              position="bottom-right"
              toastOptions={{
                duration: 3000,
                style: {
                  background: 'var(--color-surface)',
                  color: 'var(--color-foreground)',
                  border: '1px solid var(--color-border)',
                },
                className: 'sonner-toast',
              }}
              theme="system"
            />
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
