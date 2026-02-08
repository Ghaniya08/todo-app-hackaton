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

const signupSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name is too long'),
  email: z.string().email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[a-zA-Z]/, 'Password must contain at least one letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
});

type SignupFormData = z.infer<typeof signupSchema>;

export function SignUpForm() {
  const router = useRouter();
  const { signup } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      await signup(data.email, data.password, data.name);
      toast.success('Account created successfully!', {
        description: `Welcome, ${data.name}!`,
      });
      router.push('/dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign up failed. Please try again.';
      setError(errorMessage);
      toast.error('Sign up failed', {
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
        {...register('name')}
        label="Name"
        type="text"
        placeholder="John Doe"
        error={errors.name?.message}
        disabled={isLoading}
      />

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
        helperText="At least 8 characters with letters and numbers"
        disabled={isLoading}
      />

      <Button type="submit" isLoading={isLoading} className="w-full">
        Sign Up
      </Button>
    </form>
  );
}
