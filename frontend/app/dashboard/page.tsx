'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { Task, TaskCreate, TaskUpdate } from '@/types/task';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskForm } from '@/components/tasks/TaskForm';
import { EmptyState } from '@/components/tasks/EmptyState';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Button } from '@/components/ui/Button';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { toast } from 'sonner';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, signout } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    // Redirect to signin if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/signin');
      return;
    }

    // Load tasks once authenticated
    if (isAuthenticated && user) {
      loadTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, authLoading, user]);

  const loadTasks = async () => {
    if (!user) return;

    setIsLoadingTasks(true);
    setError(null);

    try {
      const taskList = await api.tasks.list(user.id);
      setTasks(taskList);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load tasks';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    if (!user) return;

    setIsCreating(true);
    setError(null);

    try {
      const newTask = await api.tasks.create(user.id, data);
      setTasks([newTask, ...tasks]);
      toast.success('Task created successfully!', {
        description: data.title,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateTask = async (data: TaskCreate) => {
    if (!user || !editingTask) return;

    setIsUpdating(true);
    setError(null);

    try {
      const updatedTask = await api.tasks.update(user.id, editingTask.id, data);
      setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
      setEditingTask(null);
      toast.success('Task updated successfully!', {
        description: data.title,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setIsUpdating(false);
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    if (!user) return;

    try {
      const updatedTask = await api.tasks.toggleComplete(user.id, taskId);
      setTasks(tasks.map((t) => (t.id === updatedTask.id ? updatedTask : t)));
      toast.success(
        updatedTask.completed ? 'Task marked as complete!' : 'Task marked as incomplete',
        {
          description: updatedTask.title,
        }
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    if (!user) return;

    try {
      await api.tasks.delete(user.id, taskId);
      const deletedTask = tasks.find((t) => t.id === taskId);
      setTasks(tasks.filter((t) => t.id !== taskId));
      toast.success('Task deleted successfully!', {
        description: deletedTask?.title,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const handleSignout = async () => {
    try {
      await signout();
      toast.success('Signed out successfully', {
        description: 'See you next time!',
      });
      router.push('/signin');
    } catch (err) {
      const errorMessage = 'Failed to sign out';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  // Show loading spinner while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Spinner size="lg" />
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-surface shadow-sm border-b border-border sticky top-0 z-40 backdrop-blur-sm bg-surface/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-light rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
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
              <div>
                <h1 className="text-2xl font-bold text-foreground">My Tasks</h1>
                <p className="text-sm text-muted">Welcome back, {user.name}!</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <ThemeToggle />
              <Button variant="ghost" onClick={handleSignout} size="sm">
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 animate-slide-down">
            <ErrorMessage message={error} onRetry={loadTasks} />
          </div>
        )}

        {/* Create/Edit Task Form */}
        <div className="bg-surface p-6 rounded-xl shadow-sm border border-border mb-8 animate-fade-in">
          <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
            {editingTask ? (
              <>
                <svg
                  className="w-5 h-5 text-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                Edit Task
              </>
            ) : (
              <>
                <svg
                  className="w-5 h-5 text-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Create New Task
              </>
            )}
          </h2>
          <TaskForm
            task={editingTask || undefined}
            onSubmit={editingTask ? handleUpdateTask : handleCreateTask}
            onCancel={editingTask ? () => setEditingTask(null) : undefined}
            isLoading={isCreating || isUpdating}
          />
        </div>

        {/* Task List */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
              <svg
                className="w-5 h-5 text-primary"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                />
              </svg>
              Your Tasks
              <span className="ml-2 px-2.5 py-0.5 text-sm font-medium bg-primary/10 text-primary rounded-full">
                {tasks.length}
              </span>
            </h2>
          </div>

          {isLoadingTasks ? (
            <div className="bg-surface p-12 rounded-xl shadow-sm border border-border">
              <Spinner size="lg" />
            </div>
          ) : tasks.length === 0 ? (
            <div className="bg-surface rounded-xl shadow-sm border border-border">
              <EmptyState />
            </div>
          ) : (
            <TaskList
              tasks={tasks}
              onToggleComplete={handleToggleComplete}
              onEdit={setEditingTask}
              onDelete={handleDeleteTask}
            />
          )}
        </div>
      </main>
    </div>
  );
}
