"""
集成测试 - 测试完整工作流
"""

import os
import tempfile
import json
import unittest
import time
from core.monitor import WorkflowMonitor
from core.alert import AlertEngine
from analytics.metrics import MetricsAnalyzer
from analytics.reporter import Reporter


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = os.path.join(self.temp_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)

        # 创建测试状态文件
        self.state_file = os.path.join(self.logs_dir, "workflow_state.json")
        self.metrics_file = os.path.join(self.logs_dir, "metrics.json")

        # 创建测试报警规则文件
        self.rules_file = os.path.join(self.temp_dir, "alert_rules.yaml")
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
    message: "任务执行"
""")

    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_monitor_to_alert_flow(self):
        """测试监控到报警的完整流程"""
        # 初始化监控器
        monitor = WorkflowMonitor(self.temp_dir)

        # 初始化报警引擎
        alert_engine = AlertEngine(rules_file=self.rules_file)

        # 创建失败的工作流状态
        state = {
            'workflow_id': 'wf-test-001',
            'user_idea': '测试想法',
            'status': 'failed',
            'start_time': '2026-04-03T10:00:00',
            'end_time': '2026-04-03T10:30:00',
            'duration': 1800,
            'tasks': [
                {'name': 'research_agent', 'status': 'completed'},
                {'name': 'product_agent', 'status': 'failed', 'error': 'API error'}
            ]
        }

        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        # 检查监控器能读取状态
        status = monitor.get_current_status()
        self.assertIsNotNone(status)
        self.assertEqual(status['status'], 'failed')

        # 检查能计算进度
        progress = monitor.calculate_progress()
        self.assertGreater(progress, 0)

        # 检查能获取失败任务
        failed_tasks = monitor.get_failed_tasks()
        self.assertEqual(len(failed_tasks), 1)
        self.assertEqual(failed_tasks[0]['name'], 'product_agent')

        # 检查报警引擎能触发报警
        alerts = alert_engine.evaluate(status, None)
        self.assertGreater(len(alerts), 0)

    def test_metrics_to_report_flow(self):
        """测试指标分析到报告生成的完整流程"""
        # 创建测试指标数据
        metrics = {
            'tasks': {
                'task1': {
                    'status': 'completed',
                    'duration': 120,
                    'token_usage': 1000
                },
                'task2': {
                    'status': 'completed',
                    'duration': 180,
                    'token_usage': 1500
                },
                'task3': {
                    'status': 'failed',
                    'duration': 90,
                    'token_usage': 800
                }
            }
        }

        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # 初始化分析器
        analyzer = MetricsAnalyzer(self.temp_dir)

        # 分析成功率
        success_rate = analyzer.analyze_success_rate()
        self.assertGreater(success_rate['total_workflows'], 0)
        self.assertIn('overall', success_rate)

        # 分析耗时
        duration = analyzer.analyze_duration()
        self.assertGreater(duration['avg_duration'], 0)

        # 生成综合报告
        report = analyzer.generate_report()
        self.assertIn('success_rate', report)
        self.assertIn('duration_analysis', report)
        self.assertIn('bottleneck', report)

        # 生成 Markdown 报告
        reporter = Reporter()
        markdown = reporter.generate_markdown_report(report)
        self.assertIn('成功率统计', markdown)
        self.assertIn('耗时分析', markdown)


if __name__ == '__main__':
    unittest.main()
