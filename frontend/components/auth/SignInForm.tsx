'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/lib/auth';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { toast } from 'sonner';

const signinSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
});

type SigninFormData = z.infer<typeof signinSchema>;

export function SignInForm() {
  const router = useRouter();
  const { signin } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SigninFormData>({
    resolver: zodResolver(signinSchema),
  });

  const onSubmit = async (data: SigninFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await signin(data.email, data.password);
      toast.success('Welcome back!', {
        description: 'You have successfully signed in.',
      });
      router.push('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed. Please check your credentials.';
      setError(errorMessage);
      toast.error('Sign in failed', {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && <ErrorMessage message={error} />}

      <Input
        {...register('email')}
        label="Email"
        type="email"
        placeholder="you@example.com"
        error={errors.email?.message}
        disabled={isLoading}
      />

      <Input
        {...register('password')}
        label="Password"
        type="password"
        placeholder="••••••••"
        error={errors.password?.message}
        disabled={isLoading}
      />

      <Button type="submit" isLoading={isLoading} className="w-full">
        Sign In
      </Button>
    </form>
  );
}
