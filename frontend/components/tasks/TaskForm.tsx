'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Task, TaskCreate } from '@/types/task';
import { useEffect } from 'react';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title is too long'),
  description: z.string().max(1000, 'Description is too long').optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: TaskCreate) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export function TaskForm({ task, onSubmit, onCancel, isLoading = false }: TaskFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: task ? {
      title: task.title,
      description: task.description || '',
    } : undefined,
  });

  useEffect(() => {
    if (task) {
      reset({
        title: task.title,
        description: task.description || '',
      });
    }
  }, [task, reset]);

  const handleFormSubmit = async (data: TaskFormData) => {
    await onSubmit({
      title: data.title,
      description: data.description || undefined,
    });
    if (!task) {
      reset(); // Clear form after creating new task
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Input
        {...register('title')}
        label="Title"
        placeholder="Enter task title"
        error={errors.title?.message}
        disabled={isLoading}
      />

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-foreground mb-1.5">
          Description (optional)
        </label>
        <textarea
          {...register('description')}
          id="description"
          rows={3}
          className="block w-full px-3 py-2 bg-surface border border-border rounded-lg shadow-sm text-foreground placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-accent disabled:cursor-not-allowed transition-all duration-200 hover:border-primary"
          placeholder="Enter task description"
          disabled={isLoading}
        />
        {errors.description && (
          <p className="mt-1.5 text-sm text-error">{errors.description.message}</p>
        )}
      </div>

      <div className="flex gap-2 pt-2">
        <Button type="submit" isLoading={isLoading}>
          {task ? 'Update Task' : 'Add Task'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
