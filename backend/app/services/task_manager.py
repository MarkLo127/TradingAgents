"""
In-Memory Task Manager for managing async analysis tasks
"""
import uuid
import json
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class InMemoryTaskManager:
    """
    Manages async tasks using in-memory storage with thread safety.
    
    Note: Tasks will be lost if the server restarts.
    Consider using Redis for production if persistence is needed.
    """
    
    def __init__(self):
        """Initialize in-memory task storage"""
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._cleanup_interval = 3600  # 1 hour
        self._task_expiry = 86400  # 24 hours
        
        # Start background cleanup thread
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start a background thread to clean up expired tasks"""
        def cleanup_worker():
            while True:
                threading.Event().wait(self._cleanup_interval)
                self._cleanup_expired_tasks()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired_tasks(self):
        """Remove tasks older than expiry time"""
        with self._lock:
            current_time = datetime.now()
            expired_keys = []
            
            for task_id, task_data in self._tasks.items():
                created_at = datetime.fromisoformat(task_data.get("created_at", ""))
                if current_time - created_at > timedelta(seconds=self._task_expiry):
                    expired_keys.append(task_id)
            
            for key in expired_keys:
                del self._tasks[key]
    
    def create_task(self, initial_data: Dict[str, Any]) -> str:
        """
        Create a new task with initial data
        
        Args:
            initial_data: Initial task data
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "progress": "Task created",
            "result": None,
            "error": None,
            "created_at": datetime.now().isoformat(),
            **initial_data
        }
        
        with self._lock:
            self._tasks[task_id] = task_data
        
        return task_id
    
    def update_task_status(self, task_id: str, status: str, progress: Optional[str] = None):
        """
        Update task status and optional progress message
        
        Args:
            task_id: Task ID
            status: New status (pending, running, completed, failed)
            progress: Optional progress message
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = status
                if progress:
                    self._tasks[task_id]["progress"] = progress
                self._tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    def update_task_progress(self, task_id: str, progress: str):
        """
        Update task progress message
        
        Args:
            task_id: Task ID
            progress: Progress message
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["progress"] = progress
                self._tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    def set_task_result(self, task_id: str, result: Any):
        """
        Set task result and mark as completed
        
        Args:
            task_id: Task ID
            result: Task result (will be JSON serialized)
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "completed"
                self._tasks[task_id]["result"] = result
                self._tasks[task_id]["progress"] = "Analysis completed"
                self._tasks[task_id]["completed_at"] = datetime.now().isoformat()
    
    def set_task_error(self, task_id: str, error: str):
        """
        Set task error and mark as failed
        
        Args:
            task_id: Task ID
            error: Error message
        """
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = error
                self._tasks[task_id]["progress"] = "Analysis failed"
                self._tasks[task_id]["failed_at"] = datetime.now().isoformat()
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task data by ID
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status information
        
        Args:
            task_id: Task ID
            
        Returns:
            Dictionary with task status information including all required fields
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            "task_id": task["task_id"],
            "status": task["status"],
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at", task.get("created_at")),  # Fallback to created_at if updated_at not set
            "progress": task.get("progress"),
            "result": task.get("result"),
            "error": task.get("error"),
            "completed_at": task.get("completed_at"),
        }
    
    def delete_task(self, task_id: str):
        """
        Delete a task
        
        Args:
            task_id: Task ID
        """
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tasks (for debugging)
        
        Returns:
            Dictionary of all tasks
        """
        with self._lock:
            return self._tasks.copy()


# Global task manager instance
task_manager = InMemoryTaskManager()
