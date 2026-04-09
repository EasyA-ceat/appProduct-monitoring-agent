
"""
任务调度器 - 定时监控和管理工作流
"""

import logging
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class WorkflowScheduler:
    """工作流调度器"""

    def __init__(self):
        """初始化调度器"""
        self.active_workflows = {}
        self.scheduler = BackgroundScheduler()
        self._running = False

    def schedule_monitoring(self, monitor_callback: Callable, interval: int = 5):
        """
        定时监控

        Args:
            monitor_callback: 监控回调函数
            interval: 监控间隔（秒）
        """
        logger.info(f"启动定时监控，间隔: {interval}秒")

        if self._running:
            logger.warning("调度器已在运行")
            return

        try:
            self.scheduler.add_job(
                monitor_callback,
                trigger=IntervalTrigger(seconds=interval),
                id='workflow_monitoring',
                name='工作流监控',
                replace_existing=True
            )
            self.scheduler.start()
            self._running = True
            logger.info("定时监控已启动")
        except Exception as e:
            logger.error(f"启动定时监控失败: {e}")

    def stop_monitoring(self):
        """停止监控"""
        if not self._running:
            logger.warning("调度器未运行")
            return

        try:
            self.scheduler.remove_job('workflow_monitoring')
            self.scheduler.shutdown()
            self._running = False
            logger.info("定时监控已停止")
        except Exception as e:
            logger.error(f"停止定时监控失败: {e}")

    def add_job(self, job_id: str, func: Callable, trigger, **kwargs):
        """
        添加定时任务

        Args:
            job_id: 任务ID
            func: 任务函数
            trigger: 触发器
            **kwargs: 其他参数
        """
        try:
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"已添加定时任务: {job_id}")
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")

    def remove_job(self, job_id: str):
        """
        移除定时任务

        Args:
            job_id: 任务ID
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除定时任务: {job_id}")
        except Exception as e:
            logger.error(f"移除定时任务失败: {e}")

    def is_running(self):
        """
        检查调度器是否正在运行

        Returns:
            True 如果调度器正在运行
        """
        return self._running

