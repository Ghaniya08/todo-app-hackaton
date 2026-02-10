/**
 * Tasks page - manage todo items.
 *
 * [Task]: UI-REFACTOR
 * [From]: User request for /dashboard/tasks route
 */

'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { Task, TaskCreate } from '@/types/task';
import { TaskList } from '@/components/tasks/TaskList';
import { TaskForm } from '@/components/tasks/TaskForm';
import { EmptyState } from '@/components/tasks/EmptyState';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { toast } from 'sonner';

export default function TasksPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  useEffect(() => {
    if (user) {
      loadTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

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
        updatedTask.completed ? 'Task completed!' : 'Task marked incomplete',
        { description: updatedTask.title }
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
      toast.success('Task deleted!', {
        description: deletedTask?.title,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.length - completedCount;
  const progressPercentage = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'pending') return !task.completed;
    if (filter === 'completed') return task.completed;
    return true;
  });

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page Header with Stats */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-1">My Tasks</h1>
            <p className="text-muted">
              {tasks.length === 0
                ? 'Create your first task to get started'
                : `Stay organized and productive`
              }
            </p>
          </div>
          {tasks.length > 0 && (
            <div className="flex items-center gap-2">
              <div className="text-right">
                <p className="text-2xl font-bold text-foreground">{progressPercentage}%</p>
                <p className="text-xs text-muted">Complete</p>
              </div>
              <div className="w-16 h-16 relative">
                <svg className="w-16 h-16 transform -rotate-90">
                  <circle
                    cx="32"
                    cy="32"
                    r="28"
                    stroke="currentColor"
                    strokeWidth="6"
                    fill="none"
                    className="text-accent"
                  />
                  <circle
                    cx="32"
                    cy="32"
                    r="28"
                    stroke="currentColor"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${progressPercentage * 1.76} 176`}
                    className="text-primary transition-all duration-500"
                  />
                </svg>
              </div>
            </div>
          )}
        </div>

        {/* Stats Cards */}
        {tasks.length > 0 && (
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-surface rounded-xl border border-border p-4 text-center">
              <p className="text-2xl font-bold text-foreground">{tasks.length}</p>
              <p className="text-xs text-muted">Total Tasks</p>
            </div>
            <div className="bg-surface rounded-xl border border-border p-4 text-center">
              <p className="text-2xl font-bold text-warning">{pendingCount}</p>
              <p className="text-xs text-muted">Pending</p>
            </div>
            <div className="bg-surface rounded-xl border border-border p-4 text-center">
              <p className="text-2xl font-bold text-success">{completedCount}</p>
              <p className="text-xs text-muted">Completed</p>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} onRetry={loadTasks} />
        </div>
      )}

      {/* Create/Edit Task Form */}
      <div className="bg-surface rounded-2xl shadow-sm border border-border p-6 mb-8">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
          {editingTask ? (
            <>
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              Edit Task
            </>
          ) : (
            <>
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </div>
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
      <div className="bg-surface rounded-2xl shadow-sm border border-border overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              Your Tasks
              {tasks.length > 0 && (
                <span className="ml-2 px-2.5 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded-full">
                  {filteredTasks.length}
                </span>
              )}
            </h2>

            {/* Filter Tabs */}
            {tasks.length > 0 && (
              <div className="flex items-center gap-1 bg-accent rounded-lg p-1">
                {[
                  { key: 'all', label: 'All' },
                  { key: 'pending', label: 'Pending' },
                  { key: 'completed', label: 'Done' },
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setFilter(tab.key as typeof filter)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 ${
                      filter === tab.key
                        ? 'bg-surface text-foreground shadow-sm'
                        : 'text-muted hover:text-foreground'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {isLoadingTasks ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <Spinner size="lg" />
              <p className="mt-3 text-sm text-muted">Loading your tasks...</p>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <EmptyState />
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-accent mb-4">
              <svg
                className="h-8 w-8 text-muted"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">No {filter} tasks</h3>
            <p className="text-sm text-muted">
              {filter === 'pending' ? 'All caught up! No pending tasks.' : 'No completed tasks yet.'}
            </p>
          </div>
        ) : (
          <div className="p-4">
            <TaskList
              tasks={filteredTasks}
              onToggleComplete={handleToggleComplete}
              onEdit={setEditingTask}
              onDelete={handleDeleteTask}
            />
          </div>
        )}
      </div>
    </div>
  );
}
