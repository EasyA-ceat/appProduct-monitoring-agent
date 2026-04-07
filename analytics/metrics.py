"""
指标分析模块 - 分析历史指标数据

功能：
- 成功率统计
- 耗时分析
- 瓶颈识别
- 趋势分析
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class MetricsAnalyzer:
    """指标分析器 - 分析 appProduct 工作流指标"""

    def __init__(self, app_product_dir: str):
        """
        初始化分析器

        Args:
            app_product_dir: appProduct 项目目录
        """
        self.app_product_dir = app_product_dir
        self.metrics_file = os.path.join(app_product_dir, "logs/metrics.json")
        self.state_file = os.path.join(app_product_dir, "logs/workflow_state.json")

    def load_metrics(self) -> Optional[Dict]:
        """
        加载指标数据

        Returns:
            指标字典
        """
        if not os.path.exists(self.metrics_file):
            logger.warning(f"指标文件不存在: {self.metrics_file}")
            return None

        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            return metrics
        except Exception as e:
            logger.error(f"加载指标文件失败: {e}")
            return None

    def analyze_success_rate(self, days: int = 7) -> Dict:
        """
        分析成功率

        Args:
            days: 分析最近多少天的数据

        Returns:
            成功率分析结果
        """
        metrics = self.load_metrics()
        if not metrics:
            return {
                'overall': 0.0,
                'by_date': {},
                'by_agent': {},
                'message': '没有可用的指标数据'
            }

        # 计算总体成功率
        tasks = metrics.get('tasks', {})
        total = len(tasks)
        successful = sum(1 for t in tasks.values() if t.get('status') == 'completed')

        overall_rate = (successful / total * 100) if total > 0 else 0.0

        # 按日期统计
        by_date = self._group_by_date(tasks)

        # 按Agent统计
        by_agent = self._group_by_agent(tasks)

        return {
            'overall': round(overall_rate, 2),
            'total_workflows': total,
            'successful_workflows': successful,
            'failed_workflows': total - successful,
            'by_date': by_date,
            'by_agent': by_agent
        }

    def analyze_duration(self, days: int = 7) -> Dict:
        """
        分析耗时

        Args:
            days: 分析最近多少天的数据

        Returns:
                       耗时分析结果
        """
        metrics = self.load_metrics()
        if not metrics:
            return {
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'p50_duration': 0,
                'p95_duration': 0,
                'message': '没有可用的指标数据'
            }

        tasks = metrics.get('tasks', {})
        durations = []

        for task in tasks.values():
            duration = task.get('duration', 0)
            if duration > 0:
                durations.append(duration)

        if not durations:
            return {
                'total_duration': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'p50_duration': 0,
                'p95_duration': 0,
                'message': '没有有效的耗时数据'
            }

        import numpy as np
        durations_sorted = sorted(durations)

        return {
            'total_duration': sum(durations),
            'avg_duration': np.mean(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'p50_duration': np.percentile(durations_sorted, 50),
            'p95_duration': np.percentile(durations_sorted, 95),
            'sample_count': len(durations)
        }

    def find_bottleneck(self, days: int = 7) -> Dict:
        """
        识别瓶颈任务

        Args:
            days: 分析最近多少天的数据

        Returns:
            瓶颈分析结果
        """
        metrics = self.load_metrics()
        if not metrics:
            return {
                'bottleneck_task': None,
                'bottleneck_agent': None,
                'message': '没有可用的指标数据'
            }

        tasks = metrics.get('tasks', {})

        # 按任务名称统计平均耗时
        task_durations = defaultdict(list)
        for task_name, task_data in tasks.items():
            duration = task_data.get('duration', 0)
            if duration > 0:
                # 提取agent名称
                agent_name = task_name.split('_')[0] if '_' in task_name else task_name
                task_durations[agent_name].append(duration)

        # 计算各任务平均耗时
        task_avg_durations = {}
        for agent, durations in task_durations.items():
            if durations:
                task_avg_durations[agent] = sum(durations) / len(durations)

        if not task_avg_durations:
            return {
                'bottleneck_task': None,
                'bottleneck_agent': None,
                'message': '没有有效的耗时数据'
            }

        # 找到最最耗时的任务
        bottleneck = max(task_avg_durations.items(), key=lambda x: x[1])

        return {
            'bottleneck_task': bottleneck[0],
            'bottleneck_agent': bottleneck[0],
            'bottleneck_duration': bottleneck[1],
            'bottleneck_samples': len(task_durations[bottleneck[0]]),
            'all_task_durations': task_avg_durations
        }

    def analyze_token_usage(self) -> Dict:
        """
        分析Token使用量

        Returns:
            Token使用量分析结果
        """
        metrics = self.load_metrics()
        if not metrics:
            return {
                'total_tokens': 0,
                'avg_tokens': 0,
                'message': '没有可用的指标数据'
            }

        tasks = metrics.get('tasks', {})
        token_usages = []

        for task in tasks.values():
            tokens = task.get('token_usage', 0)
            if tokens > 0:
                token_usages.append(tokens)

        if not token_usages:
            return {
                'total_tokens': 0,
                'avg_tokens': 0,
                'message': '没有有效的Token使用数据'
            }

        return {
            'total_tokens': sum(token_usages),
            'avg_tokens': sum(token_usages) / len(token_usages),
            'min_tokens': min(token_usages),
            'max_tokens': max(token_usages),
            'sample_count': len(token_usages)
        }

    def generate_report(self, days: int = 7) -> Dict:
        """
        生成综合分析报告

        Args:
            days: 分析最近多少天的数据

        Returns:
            综合分析报告
        """
        success_rate = self.analyze_success_rate(days)
        duration_analysis = self.analyze_duration(days)
        bottleneck = self.find_bottleneck(days)
        token_usage = self.analyze_token_usage()

        return {
            'analysis_date': datetime.now().isoformat(),
            'analysis_period_days': days,
            'success_rate': success_rate,
            'duration_analysis': duration_analysis,
            'bottleneck': bottleneck,
            'token_usage': token_usage
        }

    def _group_by_date(self, tasks: Dict) -> Dict:
        """按日期分组统计"""
        by_date = defaultdict(lambda: {'total': 0, 'successful': 0})

        for task in tasks.values():
            end_time = task.get('end_time')
            if end_time:
                try:
                    # 解析日期
                    dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    date_str = dt.strftime('%Y-%m-%d')
                    by_date[date_str]['total'] += 1
                    if task.get('status') == 'completed':
                        by_date[date_str]['successful'] += 1
                except Exception as e:
                    logger.warning(f"解析日期失败: {e}")

        # 计算成功率
        result = {}
        for date, data in by_date.items():
            rate = (data['successful'] / data['total'] * 100) if data['total'] > 0 else 0.0
            result[date] = {
                'total': data['total'],
                'successful': data['successful'],
                'success_rate': round(rate, 2)
            }

        return result

    def _group_by_agent(self, tasks: Dict) -> Dict:
        """按Agent分组统计"""
        by_agent = defaultdict(lambda: {'total': 0, 'successful': 0})

        for task_name, task_data in tasks.items():
            # 提取agent名称
            agent_name = task_name.split('_')[0] if '_' in task_name else task_name
            by_agent[agent_name]['total'] += 1
            if task_data.get('status') == 'completed':
                by_agent[agent_name]['successful'] += 1

        # 计算成功率
        result = {}
        for agent, data in by_agent.items():
            rate = (data['successful'] / data['total'] * 100) if data['total'] > 0 else 0.0
            result[agent] = {
                'total': data['total'],
                'successful': data['successful'],
                'success_rate': round(rate, 2)
            }

        return result
