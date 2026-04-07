"""
工作流触发器 - 触发 appProduct 工作流执行
"""

import subprocess
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowTrigger:
    """工作流触发器"""

    def __init__(self, app_product_dir: str):
        """
        初始化触发器

        Args:
            app_product_dir: appProduct 项目目录
        """
        self.app_product_dir = app_product_dir
        self.workflows = {}

    def trigger(self, idea: str, async_mode: bool = False) -> str:
        """
        触发工作流

        Args:
            idea: 用户想法
            async_mode: 是否异步执行

        Returns:
            工作流ID
        """
        workflow_id = f"wf-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        logger.info(f"触发工作流: {workflow_id}, 想法: {idea}, 异步: {async_mode}")

        if async_mode:
            # 异步执行
            self._trigger_async(workflow_id, idea)
        else:
            # 同步执行
            self._trigger_sync(workflow_id, idea)

        self.workflows[workflow_id] = {
            'idea': idea,
            'async': async_mode,
            'started_at': datetime.now().isoformat()
        }

        return workflow_id

    def _trigger_sync(self, workflow_id: str, idea: str) -> None:
        """同步触发工作流"""
        try:
            cmd = [
                'python3',
                f'{self.app_product_dir}/src/main.py',
                'run',
                '--idea', idea
            ]
            logger.info(f"执行命令: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, cwd=self.app_product_dir)
        except Exception as e:
            logger.error(f"同步执行失败: {e}")

    def _trigger_async(self, workflow_id: str, idea: str) -> None:
        """异步触发工作流"""
        try:
            cmd = [
                'python3',
                f'{self.app_product_dir}/src/main.py',
                'run',
                '--idea', idea
            ]
            logger.info(f"后台执行命令: {' '.join(cmd)}")
            subprocess.Popen(cmd, cwd=self.app_product_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logger.error(f"异步执行失败: {e}")

    def get_status(self, workflow_id: str) -> Optional[Dict]:
        """
        获取工作流状态

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流状态
        """
        return self.workflows.get(workflow_id)

    def get_result(self, workflow_id: str) -> Optional[Dict]:
        """
        获取工作流结果

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流结果
        """
        # TODO: 从 appProduct 的输出目录读取结果
        return None
