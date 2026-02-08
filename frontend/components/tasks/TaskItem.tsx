'use client';

import { Task } from '@/types/task';
import { Button } from '@/components/ui/Button';
import { ConfirmModal } from '@/components/ui/ConfirmModal';
import { useState } from 'react';

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: number) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: number) => Promise<void>;
}

export function TaskItem({ task, onToggleComplete, onEdit, onDelete }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDeleteClick = () => {
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
      setShowDeleteModal(false);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className={`bg-surface p-4 rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
      task.completed
        ? 'border-success/30 bg-success/5'
        : 'border-border hover:border-primary'
    }`}>
      <div className="flex items-start gap-3">
        <button
          onClick={handleToggle}
          disabled={isToggling || isDeleting}
          className={`mt-1 flex-shrink-0 w-5 h-5 rounded border-2 transition-all duration-200 ${
            task.completed
              ? 'bg-success border-success'
              : 'border-border hover:border-primary'
          } disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center`}
          aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
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
        </button>

        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-medium transition-colors ${
            task.completed ? 'line-through text-muted' : 'text-foreground'
          }`}>
            {task.title}
          </h3>
          {task.description && (
            <p className={`mt-1 text-sm transition-colors ${
              task.completed ? 'line-through text-muted' : 'text-muted'
            }`}>
              {task.description}
            </p>
          )}
          <p className="mt-2 text-xs text-muted flex items-center gap-1">
            <svg
              className="w-3 h-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            Created {new Date(task.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="flex gap-2 flex-shrink-0">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(task)}
            disabled={isDeleting}
            className="hidden sm:inline-flex"
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="danger"
            onClick={handleDeleteClick}
            disabled={isToggling || isDeleting}
          >
            Delete
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteConfirm}
        title="Delete Task"
        message="Are you sure you want to delete this task? This action cannot be undone."
        confirmText="Yes, Delete"
        cancelText="Cancel"
        isLoading={isDeleting}
      />
    </div>
  );
}
