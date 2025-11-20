/**
 * Loading spinner component
 */
import { Spinner } from "@/components/ui/spinner";

interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message = "載入中..." }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-4">
      <Spinner className="h-8 w-8" />
      <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>
    </div>
  );
}
