"""
核心监控模块 - 负责监控 appProduct 工作流状态

功能：
- 读取并解析 appProduct 的状态文件
- 监控工作流状态变化
- 计算工作流进度
- 收集监控数据
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class WorkflowMonitor:
    """工作流监控器 - 监控 appProduct 工作流状态"""

    def __init__(self, app_product_dir: str):
        """
        初始化监控器

        Args:
            app_product_dir: appProduct 项目目录
        """
        self.app_product_dir = app_product_dir
        self.state_file = os.path.join(app_product_dir, "logs/workflow_state.json")
        self.metrics_file = os.path.join(app_product_dir, "logs/metrics.json")
        self.log_file = os.path.join(app_product_dir, "logs/workflow.log")

        # 缓存当前状态，用于检测变化
        self._last_state = None
        self._last_metrics = None

    def get_current_status(self) -> Optional[Dict]:
        """
        获取当前工作流状态

        Returns:
            工作流状态字典，如果文件不存在返回 None
        """
        if not os.path.exists(self.state_file):
            logger.warning(f"状态文件不存在: {self.state_file}")
            return None

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            logger.debug(f"成功读取状态文件: {state}")
            return state
        except json.JSONDecodeError as e:
            logger.error(f"解析状态文件失败: {e}")
            return None
        except Exception as e:
            logger.error(f"读取状态文件异常: {e}")
            return None

    def get_metrics(self) -> Optional[Dict]:
        """
        获取指标数据

        Returns:
            指标字典，如果文件不存在返回 None
        """
        if not os.path.exists(self.metrics_file):
            logger.warning(f"指标文件不存在: {self.metrics_file}")
            return None

        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            logger.debug(f"成功读取指标文件: {metrics}")
            return metrics
        except json.JSONDecodeError as e:
            logger.error(f"解析指标文件失败: {e}")
            return None
        except Exception as e:
            logger.error(f"读取指标文件异常: {e}")
            return None

    def calculate_progress(self) -> float:
        """
        计算工作流进度（0-100）

        根据已完成的任务数除以总任务数计算进度

        Returns:
            进度百分比（0-100）
        """
        state = self.get_current_status()
        if not state:
            return 0.0

        tasks = state.get('tasks', [])
        if not tasks:
            return 0.0

        # 定义任务列表（按 appProduct 的 9 个任务）
        all_tasks = [
            'research_agent',
            'product_agent',
            'research_product_agent',
            'design_agent',
            'architecture_agent',
            'development_agent',
            'security_agent',
            'testing_agent',
            'deployment_agent'
        ]

        # 统计已完成的任务数
        completed_count = 0
        for task_name in all_tasks:
            task = next((t for t in tasks if t.get('name') == task_name), None)
            if task and task.get('status') == 'completed':
                completed_count += 1

        progress = (completed_count / len(all_tasks)) * 100
        logger.debug(f"工作流进度: {progress:.2f}% ({completed_count}/{len(all_tasks)})")
        return progress

    def get_current_task(self) -> Optional[str]:
        """
        获取当前正在执行的任务

        Returns:
            当前任务名称，如果没有正在执行的任务返回 None
        """
        state = self.get_current_status()
        if not state:
            return None

        tasks = state.get('tasks', [])
        for task in tasks:
            if task.get('status') == 'in_progress':
                return task.get('name')

        return None

    def watch(self, callback: Optional[Callable[[Dict, Dict], None]] = None,
              interval: int = 5) -> None:
        """
        监控工作流状态变化

        Args:
            callback: 状态变化回调函数，接收 (old_state, new_state, old_metrics, new_metrics)
            interval: 监控间隔（秒）
        """
        logger.info(f"开始监控工作流，间隔 {interval} 秒")

        while True:
            try:
                # 获取当前状态和指标
                current_state = self.get_current_status()
                current_metrics = self.get_metrics()

                # 检测状态变化
                state_changed = self._detect_state_change(self._last_state, current_state)
                metrics_changed = self._detect_metrics_change(self(self._last_metrics, current_metrics))

                if state_changed or metrics_changed:
                    logger.info("检测到状态或指标变化")

                    # 调用回调函数
                    if callback:
                        callback(self._last_state, current_state, self._last_metrics, current_metrics)

                # 更新缓存
                self._last_state = current_state
                self._last_metrics = current_metrics

                # 等待下一次检查
                time.sleep(interval)

            except KeyboardInterrupt:
                logger.info("接收到中断信号，停止监控")
                break
            except Exception as e:
                logger.error(f"监控过程中发生异常: {e}")
                time.sleep(interval)

    def _detect_state_change(self, old_state: Optional[Dict], new_state: Optional[Dict]) -> bool:
        """检测状态是否发生变化"""
        if old_state is None and new_state is not None:
            return True
        if old_state is not None and new_state is None:
            return True
        if old_state is None or new_state is None:
            return False

        # 比较关键状态字段
        return (
            old_state.get('status') != new_state.get('status') or
            old_state.get('workflow_id') != new_state.get('workflow_id')
        )

    def _detect_metrics_change(self, old_metrics: Optional[Dict], new_metrics: Optional[Dict]) -> bool:
        """检测指标是否发生变化"""
        if old_metrics is None and new_metrics is not None:
            return True
        if old_metrics is not None and new_metrics is None:
            return True
        if old_metrics is None or new_metrics is None:
            return False

        # 比较任务数量
        old_tasks = old_metrics.get('tasks', {})
        new_tasks = new_metrics.get('tasks', {})
        return len(old_tasks) != len(new_tasks)

    def get_workflow_summary(self) -> Dict:
        """
        获取工作流摘要信息

        Returns:
            工作流摘要字典
        """
        state = self.get_current_status()
        if not state:
            return {
                'status': 'not_started',
                'message': '工作流尚未开始'
            }

        summary = {
            'workflow_id': state.get('workflow_id', 'unknown'),
            'user_idea': state.get('user_idea', ''),
            'status': state.get('status', 'unknown'),
            'progress': self.calculate_progress(),
            'current_task': self.get_current_task(),
            'start_time': state.get('start_time'),
            'end_time': state.get('end_time'),
        }

        # 计算耗时
        if summary.get('start_time') and summary.get('end_time'):
            try:
                start = datetime.fromisoformat(summary['start_time'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(summary['end_time'].replace('Z', '+00:00'))
                summary['duration'] = (end - start).total_seconds()
            except Exception as e:
                logger.error(f"计算耗时失败: {e}")
                summary['duration'] = 0
        elif summary.get('start_time'):
            try:
                start = datetime.fromisoformat(summary['start_time'].replace('Z', '+00:00'))
                summary['duration'] = (datetime.now() - start).total_seconds()
            except Exception as e:
                logger.error(f"计算耗时失败: {e}")
                summary['duration'] = 0

        return summary

    def get_failed_tasks(self) -> List[Dict]:
        """
        获取所有失败的任务

        Returns:
            失败任务列表
        """
        state = self.get_current_status()
        if not state:
            return []

        failed_tasks = []
        for task in state.get('tasks', []):
            if task.get('status') == 'failed':
                failed_tasks.append({
                    'name': task.get('name'),
                    'error': task.get('error', 'Unknown error'),
                    'start_time': task.get('start_time'),
                    'end_time': task.get('end_time')
                })

        return failed_tasks

    def is_workflow_failed(self) -> bool:
        """
        检查工作流是否失败

        Returns:
            True 如果工作流状态为 failed
        """
        state = self.get_current_status()
        if not state:
            return False

        return state.get('status') == 'failed'

    def is_any_task_failed(self) -> bool:
        """
        检查是否有任务失败

        Returns:
            True 如果有任务状态为 failed
        """
        return len(self.get_failed_tasks()) > 0

    def format_duration(self, seconds: float) -> str:
        """
        格式化耗时

        Args:
            seconds: 秒数

        Returns:
            格式化后的字符串（如 "1h 30m 15s"）
        """
        if seconds < 0:
            return "0s"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)
