"""
报警引擎单元测试
"""

import os
import tempfile
import shutil
import unittest
from core.alert import AlertEngine


class TestAlertEngine(unittest.TestCase):
    """测试 AlertEngine 类"""

    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 创建测试报警规则文件（使用唯一文件名）
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        self.rules_file = os.path.join(self.temp_dir, f"alert_rules_{unique_id}.yaml")
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            f.write("""
rules:
  - name: workflow_failure
    enabled: true
    condition: "status == 'failed'"
    severity: "critical"
    message: "工作流执行失败"

  - name: task_failure
    enabled: true
    condition: "any(task.status == 'failed' for task in tasks)"
    severity: "warning"
    message: "任务执行失败"

  - name: timeout
    enabled: true
    condition: "duration > 3600"
    severity: "warning"
    message: "工作流执行超时（1小时）"

  - name: retry_exceeded
    enabled: true
    condition: "retry_count > 3"
    severity: "critical"
    message: "重试次数超限"
""")

        # 初始化报警引擎
        self.alert_engine = AlertEngine(rules_file=self.rules_file)

    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_load_rules(self):
        """测试加载报警规则"""
        self.assertEqual(len(self.alert_engine.rules), 4)
        self.assertEqual(self.alert_engine.rules[0]['name'], 'workflow_failure')

    def test_evaluate_workflow_failure(self):
        """测试工作流失败报警"""
        state = {
            'workflow_id': 'test-001',
            'status': 'failed',
            'tasks': []
        }

        alerts = self.alert_engine.evaluate(state, None)
        # 工作流失败时应该触发 workflow_failure 报警
        self.assertGreaterEqual(len(alerts), 1)
        self.assertIn('workflow_failure', [a['name'] for a in alerts])

    def test_evaluate_task_failure(self):
        """测试任务失败报警"""
        import logging
        logging.basicConfig(level=logging.DEBUG)

        state = {
            'workflow_id': 'test-001',
            'status': 'running',
            'tasks': [
                {'name': 'research_agent', 'status': 'completed'},
                {'name': 'product_agent', 'status': 'failed'}
            ]
        }

        alerts = self.alert_engine.evaluate(state, None)
        # 任务失败时应该触发 task_failure 报警
        print(f"\n规则列表: {[r['name'] for r in self.alert_engine.rules]}")
        print(f"触发的报警: {[a['name'] for a in alerts]}")
        self.assertGreaterEqual(len(alerts), 1)
        self.assertIn('task_failure', [a['name'] for a in alerts])

    def test_evaluate_timeout(self):
        """测试超时报警"""
        state = {
            'workflow_id': 'test-001',
            'status': 'running',
            'duration': 4000,  # 超过1小时
            'tasks': []
        }

        alerts = self.alert_engine.evaluate(state, None)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['name'], 'timeout')

    def test_evaluate_no_alert(self):
        """测试无报警触发"""
        state = {
            'workflow_id': 'test-001',
            'status': 'running',
            'duration': 1800,  # 30分钟
            'tasks': [
                {'name': 'research_agent', 'status': 'completed'}
            ]
        }

        alerts = self.alert_engine.evaluate(state, None)
        self.assertEqual(len(alerts), 0)

    def test_get_failed_tasks(self):
        """测试获取失败任务"""
        state = {
            'workflow_id': 'test-001',
            'tasks': [
                {'name': 'research_agent', 'status': 'completed'},
                {'name': 'product_agent', 'status': 'failed', 'error': 'API error'},
                {'name': 'design_agent', 'status': 'failed', 'error': 'Template error'}
            ]
        }

        failed = self.alert_engine._get_failed_tasks(state)
        self.assertEqual(len(failed), 2)
        self.assertIn('product_agent', failed)
        self.assertIn('design_agent', failed)

    def test_get_first_error(self):
        """测试获取第一个错误"""
        state = {
            'workflow_id': 'test-001',
            'tasks': [
                {'name': 'research_agent', 'status': 'completed'},
                {'name': 'product_agent', 'status': 'failed', 'error': 'API error'},
                {'name': 'design_agent', 'status': 'failed', 'error': 'Template error'}
            ]
        }

        error = self.alert_engine._get_first_error(state)
        self.assertIsNotNone(error)
        self.assertIn('product_agent', error)


if __name__ == '__main__':
    unittest.main()
