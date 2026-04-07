"""
监控模块单元测试
"""

import json
import os
import tempfile
import unittest
from core.monitor import WorkflowMonitor


class TestWorkflowMonitor(unittest.TestCase):
    """测试 WorkflowMonitor 类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 创建 logs 目录
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

        # 创建测试状态文件
        self.state_file = os.path.join(self.logs_dir, "workflow_state.json")
        self.metrics_file = os.path.join(self.logs_dir, "metrics.json")

        # 初始化监控器
        self.monitor = WorkflowMonitor(self.temp_dir)

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_current_status_no_file(self):
        """测试读取不存在的状态文件"""
        status = self.monitor.get_current_status()
        self.assertIsNone(status)

    def test_get_current_status_valid(self):
        """测试读取有效的状态文件"""
        # 创建测试数据
        test_state = {
            "workflow_id": "test-001",
            "user_idea": "测试想法",
            "status": "running",
            "start_time": "2026-04-03T10:00:00",
            "tasks": []
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        # 读取状态
        status = self.monitor.get_current_status()
        self.assertIsNotNone(status)
        self.assertEqual(status['workflow_id'], 'test-001')
        self.assertEqual(status['status'], 'running')

    def test_calculate_progress_no_tasks(self):
        """测试没有任务时的进度计算"""
        test_state = {
            "workflow_id": "test-001",
            "status": "running",
            "tasks": []
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        progress = self.monitor.calculate_progress()
        self.assertEqual(progress, 0.0)

    def test_calculate_progress_partial(self):
        """测试部分完成时的进度计算"""
        test_state = {
            "workflow_id": "test-001",
            "status": "running",
            "tasks": [
                {"name": "research_agent", "status": "completed"},
                {"name": "product_agent", "status": "completed"},
                {"name": "research_product_agent", "status": "in_progress"}
            ]
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        progress = self.monitor.calculate_progress()
        # 2/9 = 22.22%
        self.assertAlmostEqual(progress, 22.22, places=1)

    def test_calculate_progress_all_completed(self):
        """测试全部完成时的进度计算"""
        all_tasks = [
            'research_agent', 'product_agent', 'research_product_agent',
            'design_agent', 'architecture_agent', 'development_agent',
            'security_agent', 'testing_agent', 'deployment_agent'
        ]

        test_tasks = [{"name": task, "status": "completed"} for task in all_tasks]

        test_state = {
            "workflow_id": "test-001",
            "status": "completed",
            "tasks": test_tasks
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        progress = self.monitor.calculate_progress()
        self.assertEqual(progress, 100.0)

    def test_get_current_task(self):
        """测试获取当前正在执行的任务"""
        test_state = {
            "workflow_id": "test-001",
            "status": "running",
            "tasks": [
                {"name": "research_agent", "status": "completed"},
                {"name": "product_agent", "status": "in_progress"},
                {"name": "design_agent", "status": "pending"}
            ]
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        current_task = self.monitor.get_current_task()
        self.assertEqual(current_task, 'product_agent')

    def test_get_failed_tasks(self):
        """测试获取失败的任务"""
        test_state = {
            "workflow_id": "test-001",
            "status": "failed",
            "tasks": [
                {"name": "research_agent", "status": "completed"},
                {"name": "product_agent", "status": "failed"},
                {"name": "research_product_agent", "status": "failed"}
            ]
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        failed_tasks = self.monitor.get_failed_tasks()
        self.assertEqual(len(failed_tasks), 2)
        self.assertEqual(failed_tasks[0]['name'], 'product_agent')
        self.assertEqual(failed_tasks[1]['name'], 'research_product_agent')

    def test_is_workflow_failed(self):
        """测试检查工作流是否失败"""
        test_state = {
            "workflow_id": "test-001",
            "status": "failed",
            "tasks": []
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(test_state, f)

        self.assertTrue(self.monitor.is_workflow_failed())

    def test_format_duration(self):
        """测试耗时格式化"""
        # 测试秒数
        self.assertEqual(self.monitor.format_duration(45), "45s")

        # 测试分钟
        self.assertEqual(self.monitor.format_duration(120), "2m")
        self.assertEqual(self.monitor.format_duration(150), "2m 30s")

        # 测试小时
        self.assertEqual(self.monitor.format_duration(3600), "1h")
        self.assertEqual(self.monitor.format_duration(3665), "1h 1m 5s")


if __name__ == '__main__':
    unittest.main()
