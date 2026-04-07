"""
主入口文件
"""

import os
import sys
import logging
import yaml

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.monitor import WorkflowMonitor
from core.alert import AlertEngine
from core.scheduler import WorkflowScheduler
from integrations.feishu import FeishuIntegration
from management.trigger import WorkflowTrigger
from management.controller import WorkflowController
from analytics.metrics import MetricsAnalyzer
from analytics.reporter import Reporter


def load_config(config_path: str = "config/agent_config.yaml") -> dict:
    """加载配置文件"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logging(level: str = "INFO") -> None:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AppProduct 工作流监控管理 Agent - 天开")
    parser.add_argument('--config', default='config/agent_config.yaml', help='配置文件路径')
    parser.add_argument('--log-level', default='INFO', help='日志级别')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # start 命令
    start_parser = subparsers.add_parser('start', help='启动监控服务')

    # status 命令
    status_parser = subparsers.add_parser('status', help='查看状态')
    status_parser.add_argument('--workflow-id', help='工作流ID')

    # metrics 命令
    metrics_parser = subparsers.add_parser('metrics', help='查看指标')
    metrics_parser.add_argument('--days', type=int, default=7, help='分析最近多少天的数据')

    # trigger 命令
    trigger_parser = subparsers.add_parser('trigger', help='触发工作流')
    trigger_parser.add_argument('--idea', required=True, help='用户想法')
    trigger_parser.add_argument('--async', action='store_true', help='异步执行')

    # pause 命令
    pause_parser = subparsers.add_parser('pause', help='暂停工作流')
    pause_parser.add_argument('--workflow-id', required=True, help='工作流ID')

    # resume 命令
    resume_parser = subparsers.add_parser('resume', help='恢复工作流')
    resume_parser.add_argument('--workflow-id', required=True, help='工作流ID')

    args = parser.parse_args()

    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)

    # 设置日志
    setup_logging(args.log_level or config.get('logging', {}).get('level', 'INFO'))

    logger = logging.getLogger(__name__)
    logger.info("天开 - AppProduct 工作流监控管理 Agent")

    # 初始化组件
    app_product_dir = config.get('app_product_dir')
    if not app_product_dir or not os.path.exists(app_product_dir):
        logger.error(f"appProduct 目录不存在: {app_product_dir}")
        sys.exit(1)

    # 初始化监控器
    monitor = WorkflowMonitor(app_product_dir)

    # 初始化飞书集成
    feishu_config = config.get('feishu', {})
    if feishu_config.get('enabled'):
        feishu = FeishuIntegration(feishu_config.get('channel', ''))
    else:
        feishu = None

    # 初始化报警引擎
    alert_config = config.get('alert', {})
    if alert_config.get('enabled'):
        rules_file = os.path.join(project_root, alert_config.get('rules_file', 'config/alert_rules.yaml'))
        alert_engine = AlertEngine(feishu, rules_file)
    else:
        alert_engine = None

    # 执行命令
    if args.command == 'start':
        logger.info("启动监控服务...")
        # TODO: 实现监控服务启动逻辑

    elif args.command == 'status':
        summary = monitor.get_workflow_summary()
        print("\n工作流状态:")
        print(f"  工作流ID: {summary.get('workflow_id', 'N/A')}")
        print(f"  用户想法: {summary.get('user_idea', 'N/A')}")
        print(f"  状态: {summary.get('status', 'N/A')}")
        print(f"  进度: {summary.get('progress', 0):.1f}%")
        print(f"  当前任务: {summary.get('current_task', 'N/A')}")

    elif args.command == 'metrics':
        analyzer = MetricsAnalyzer(app_product_dir)
        report = analyzer.generate_report(args.days)

        print(f"\n指标分析报告（最近 {args.days} 天）:")
        print(f"  总体成功率: {report['success_rate']['overall']}%")
        print(f"  总执行次数: {report['success_rate']['total_workflows']}")
        print(f"  平均耗时: {report['duration_analysis'].get('avg_duration', 0):.1f} 秒")
        print(f"  瓶颈任务: {report['bottleneck'].get('bottleneck_task', 'N/A')}")

    elif args.command == 'trigger':
        trigger = WorkflowTrigger(app_product_dir)
        workflow_id = trigger.trigger(args.idea, args.async)
        print(f"工作流已触发，ID: {workflow_id}")
        print(f"异步模式: {args.async}")

    elif args.command == 'pause':
        controller = WorkflowController(app_product_dir)
        if controller.pause(args.workflow_id):
            print(f"工作流 {args.workflow_id} 已暂停")
        else:
            print(f"暂停工作流失败")

    elif args.command == 'resume':
        controller = WorkflowController(app_product_dir)
        if controller.resume(args.workflow_id):
            print(f"工作流 {args.workflow_id} 已恢复")
        else:
            print(f"恢复工作流失败")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
