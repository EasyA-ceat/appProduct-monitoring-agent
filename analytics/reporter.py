"""
报告生成器 - 生成 Markdown 和 JSON 格式的分析报告
"""

import json
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class Reporter:
    """报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        pass

    def generate_markdown_report(self, report_data: Dict) -> str:
        """
        生成 Markdown 格式的报告

        Args:
            report_data: 分析报告数据

        Returns:
            Markdown 格式的报告字符串
        """
        lines = []
        lines.append("# AppProduct 工作流执行报告\n")

        # 报告信息
        lines.append(f"**生成时间**: {report_data.get('analysis_date', 'N/A')}")
        lines.append(f"**分析周期**: 最近 {report_data.get('analysis_period_days', 7)} 天\n")

        # 成功率统计
        lines.append("## 📊 成功率统计\n")

        success_rate = report_data.get('success_rate', {})
        lines.append(f"- **总体成功率**: {success_rate.get('overall', 0)}%")
        lines.append(f"- **总执行次数**: {success_rate.get('total_workflows', 0)}")
        lines.append(f"- **成功次数**: {success_rate.get('successful_workflows', 0)}")
        lines.append(f"- **失败次数**: {success_rate.get('failed_workflows', 0)}\n")

        # 按日期统计
        if success_rate.get('by_date'):
            lines.append("### 按日期统计")
            lines.append("| 日期 | 总次数 | 成功次数 | 成功率 |")
            lines.append("|------|--------|----------|--------|")
            for date, data in sorted(success_rate['by_date'].items()):
                lines.append(
                    f"| {date} | {data['total']} | {data['successful']} | {data['success_rate']}% |"
                )
            lines.append("")

        # 按Agent统计
        if success_rate.get('by_agent'):
            lines.append("### 按 Agent 统计")
            lines.append("| Agent | 总次数 | 成功次数 | 成功率 |")
            lines.append("|-------|--------|----------|--------|")
            for agent, data in sorted(success_rate['by_agent'].items()):
                lines.append(
                    f"| {agent} | {data['total']} | {data['successful']} | {data['success_rate']}% |"
                )
            lines.append("")

        # 耗时分析
        lines.append("## ⏱️ 耗时分析\n")

        duration = report_data.get('duration_analysis', {})
        if duration.get('sample_count', 0) > 0:
            lines.append(f"- **平均耗时**: {self._format_duration(duration.get('avg_duration', 0))}")
            lines.append(f"- **最短耗时**: {self._format_duration(duration.get('min_duration', 0))}")
            lines.append(f"- **最长耗时**: {self._format_duration(duration.get('max_duration', 0))}")
            lines.append(f"- **50分位耗时**: {self._format_duration(duration.get('p50_duration', 0))}")
            lines.append(f"- **95分位耗时**: {self._format_duration(duration.get('p95_duration', 0))}")
            lines.append(f"- **样本数量**: {duration.get('sample_count', 0)}\n")
        else:
            lines.append(f"- 暂无耗时数据\n")

        # 瓶颈分析
        lines.append("## 🔍 瓶颈分析\n")

        bottleneck = report_data.get('bottleneck', {})
        if bottleneck.get('bottleneck_task'):
            lines.append(f"**最耗时任务**: {bottleneck.get('bottleneck_task')}")
            lines.append(f"**平均耗时**: {self._format_duration(bottleneck.get('bottleneck_duration', 0))}")
            lines.append(f"**样本数量**: {bottleneck.get('bottleneck_samples', 0)}\n")

            if bottleneck.get('all_task_durations'):
                lines.append("### 所有任务平均耗时")
                lines.append("| 任务 | 平均耗时 |")
                lines.append("|------|----------|")
                for task, duration in sorted(
                    bottleneck['all_task_durations'].items(),
                    key=lambda x: x[1],
                    reverse=True
                ):
                    lines.append(f"| {task} | {self._format_duration(duration)} |")
                lines.append("")
        else:
            lines.append(f"- 暂无瓶颈数据\n")

        # Token使用量
        lines.append("## 💰 Token 使用量\n")

        token_usage = report_data.get('token_usage', {})
        if token_usage.get('sample_count', 0) > 0:
            lines.append(f"- **总Token使用量**: {token_usage.get('total_tokens', 0):,}")
            lines.append(f"- **平均Token使用量**: {token_usage.get('avg_tokens', 0):,.1f}")
            lines.append(f"- **最少Token使用量**: {token_usage.get('min_tokens', 0):,}")
            lines.append(f"- **最多Token使用量**: {token_usage.get('max_tokens', 0):,}")
            lines.append(f"- **样本数量**: {token_usage.get('sample_count', 0)}\n")
        else:
            lines.append(f"- 暂无Token使用数据\n")

        # 报告尾部
        lines.append("---")
        lines.append(f"*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

        return "\n".join(lines)

    def generate_json_report(self, report_data: Dict) -> str:
        """
        生成 JSON 格式的报告

        Args:
            report_data: 分析报告数据

        Returns:
            JSON 格式的报告字符串
        """
        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def save_markdown_report(self, report_data: Dict, output_path: str) -> None:
        """
        保存 Markdown 报告到文件

        Args:
            report_data: 分析报告数据
            output_path: 输出文件路径
        """
        try:
            markdown = self.generate_markdown_report(report_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            logger.info(f"Markdown 报告已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存 Markdown 报告失败: {e}")
            raise

    def save_json_report(self, report_data: Dict, output_path: str) -> None:
        """
        保存 JSON 报告到文件

        Args:
            report_data: 分析报告数据
            output_path: 输出文件路径
        """
        try:
            json_str = self.generate_json_report(report_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            logger.info(f"JSON 报告已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存 JSON 报告失败: {e}")
            raise

    def _format_duration(self, seconds: float) -> str:
        """
        格式化耗时

        Args:
            seconds: 秒数

        Returns:
            格式化后的字符串
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
