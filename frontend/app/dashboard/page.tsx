/**
 * Dashboard page - redirects to tasks by default.
 *
 * [Task]: UI-REFACTOR
 * [From]: User request for /dashboard/tasks and /dashboard/chat routes
 */

import { redirect } from 'next/navigation';

export default function DashboardPage() {
  redirect('/dashboard/tasks');
}
