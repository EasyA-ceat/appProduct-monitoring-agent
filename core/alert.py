"""
报警引擎 - 评估报警条件并触发报警

功能：
- 评估报警条件
- 触发报警通知
- 发送飞书报警消息
"""

import os
import yaml
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertEngine:
    """报警引擎 - 评估报警条件并触发报警"""

    def __init__(self, feishu_integration=None, rules_file: str = None):
        """
        初始化报警引擎

        Args:
            feishu_integration: 飞书集成实例
            rules_file: 报警规则配置文件路径
        """
        self.feishu = feishu_integration
        self.rules_file = rules_file
        self.rules = self._load_rules() if rules_file else []

    def _load_rules(self) -> List[Dict]:
        """加载报警规则"""
        if not os.path.exists(self.rules_file):
            logger.warning(f"报警规则文件不存在: {self.rules_file}")
            return []

        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('rules', [])
        except Exception as e:
            logger.error(f"加载报警规则失败: {e}")
            return []

    def evaluate(self, state: Optional[Dict], metrics: Optional[Dict]) -> List[Dict]:
        """
        评估是否触发报警

        Args:
            state: 工作流状态
            metrics: 指标数据

        Returns:
            触发的报警列表
        """
        triggered_alerts = []

        if not state:
            return triggered_alerts

        for rule in self.rules:
            if not rule.get('enabled', False):
                continue

            result = self._evaluate_rule(rule, state, metrics)
            if result:
                triggered_alerts.append(rule)
                logger.info(f"报警规则触发: {rule['name']}")

        return triggered_alerts

    def _evaluate_rule(self, rule: Dict, state: Dict, metrics: Optional[Dict]) -> bool:
        """
        评估单个报警规则

        Args:
            rule: 报警规则
            state: 工作流状态
            metrics: 指标数据

        Returns:
            True 如果规则条件满足
        """
        condition = rule.get('condition', '')
        logger.debug(f"评估规则: {rule['name']}, 条件: {condition}")

        # 工作流失败检测（精确匹配，避免匹配 task.status）
        if condition.strip().startswith("status == 'failed'"):
            return state.get('status') == 'failed'

        # 任务失败检测
        if "task.status == 'failed'" in condition and 'tasks' in state:
            result = any(task.get('status') == 'failed' for task in state.get('tasks', []))
            logger.debug(f"任务失败检测结果: {result}")
            return result

        # 超时检测
        if "duration >" in condition and 'duration' in state:
            # 从条件中提取阈值
            try:
                threshold = int(''.join(filter(str.isdigit, condition)))
                return state.get('duration', 0) > threshold
            except ValueError:
                logger.warning(f"解析超时阈值失败: {condition}")
                return False

        # 重试次数超限检测
        if "retry_count >" in condition:
            try:
                threshold = int(''.join(filter(str.isdigit, condition)))
                retry_count = state.get('retry_count', 0)
                return retry_count > threshold
            except ValueError:
                logger.warning(f"解析重试阈值失败: {condition}")
                return False

        return False

    def trigger_alert(self, alert_type: str, data: Dict) -> bool:
        """
        触发报警

        Args:
            alert_type: 报警类型
            data: 报警数据

        Returns:
            True 如果报警发送成功
        """
        logger.info(f"触发报警: {alert_type}")

        # 构建报警消息
        message = self._build_alert_message(alert_type, data)

        # 发送到飞书
        if self.feishu:
            try:
                self.feishu.send_alert(alert_type, data)
                return True
            except Exception as e:
                logger.error(f"发送飞书报警失败: {e}")
                return False

        # 如果没有飞书集成，打印到日志
        logger.warning(f"报警消息（未发送）: {message}")
        return False

    def _build_alert_message(self, alert_type: str, data: Dict) -> str:
        """
        构建报警消息

        Args:
            alert_type: 报警类型
            data: 报警数据

        Returns:
            报警消息字符串
        """
        lines = []
        lines.append(f"🚨 报警类型: {alert_type}")

        if 'workflow_id' in data:
            lines.append(f"工作流ID: {data['workflow_id']}")

        if 'user_idea' in data:
            lines.append(f"用户想法: {data['user_idea']}")

        if 'status' in data:
            lines.append(f"状态: {data['status']}")

        if 'failed_task' in data:
            lines.append(f"失败任务: {data['failed_task']}")

        if 'error_message' in data:
            lines.append(f"错误信息: {data['error_message']}")

        return "\n".join(lines)

    def trigger_workflow_alerts(self, state: Optional[Dict], metrics: Optional[Dict]) -> None:
        """
        触发所有匹配的报警规则

        Args:
            state: 工作流状态
            metrics: 指标数据
        """
        triggered_alerts = self.evaluate(state, metrics)

        for alert in triggered_alerts:
            self.trigger_alert(alert['name'], {
                'workflow_id': state.get('workflow_id') if state else None,
                'user_idea': state.get('user_idea') if state else None,
                'status': state.get('status') if state else None,
                'severity': alert.get('severity'),
                'message': alert.get('message'),
                'failed_tasks': self._get_failed_tasks(state) if state else [],
                'error_message': self._get_first_error(state) if state else None
            })

    def _get_failed_tasks(self, state: Dict) -> List[str]:
        """获取失败的任务列表"""
        return [task['name'] for task in state.get('tasks', []) if task.get('status') == 'failed']

    def _get_first_error(self, state: Dict) -> Optional[str]:
        """获取第一个错误信息"""
        for task in state.get('tasks', []):
            if task.get('status') == 'failed' and task.get('error'):
                return f"{task['name']}: {task['error']}"
        return None
