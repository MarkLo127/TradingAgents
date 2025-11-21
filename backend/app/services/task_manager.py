"""
Redis Task Manager for async analysis processing
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum
import redis
import logging

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RedisTaskManager:
    """Manages async tasks using Redis as storage"""
    
    def __init__(self, redis_url: str):
        """
        Initialize Redis task manager
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5
        )
        self.task_expiry = timedelta(hours=24)
        
    def _task_key(self, task_id: str) -> str:
        """Generate Redis key for task"""
        return f"task:{task_id}"
    
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create a new task
        
        Args:
            task_data: Initial task data
            
        Returns:
            task_id: Unique task identifier
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **task_data
        }
        
        key = self._task_key(task_id)
        self.redis_client.setex(
            key,
            self.task_expiry,
            json.dumps(task)
        )
        
        logger.info(f"Created task {task_id}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task data or None if not found
        """
        key = self._task_key(task_id)
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: Optional[str] = None
    ):
        """
        Update task status and progress
        
        Args:
            task_id: Task identifier
            status: New task status
            progress: Progress message
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found for status update")
            return
        
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        
        if progress:
            task["progress"] = progress
        
        key = self._task_key(task_id)
        self.redis_client.setex(
            key,
            self.task_expiry,
            json.dumps(task)
        )
        
        logger.info(f"Updated task {task_id} status to {status}")
    
    def set_task_result(
        self,
        task_id: str,
        result: Dict[str, Any],
        error: Optional[str] = None
    ):
        """
        Set task result (success or failure)
        
        Args:
            task_id: Task identifier
            result: Task result data
            error: Error message if failed
        """
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task {task_id} not found for result update")
            return
        
        if error:
            task["status"] = TaskStatus.FAILED
            task["error"] = error
        else:
            task["status"] = TaskStatus.COMPLETED
            task["result"] = result
        
        task["updated_at"] = datetime.now().isoformat()
        task["completed_at"] = datetime.now().isoformat()
        
        key = self._task_key(task_id)
        self.redis_client.setex(
            key,
            self.task_expiry,
            json.dumps(task)
        )
        
        status_msg = "completed" if not error else f"failed: {error}"
        logger.info(f"Task {task_id} {status_msg}")
    
    def delete_task(self, task_id: str):
        """
        Delete a task
        
        Args:
            task_id: Task identifier
        """
        key = self._task_key(task_id)
        self.redis_client.delete(key)
        logger.info(f"Deleted task {task_id}")
