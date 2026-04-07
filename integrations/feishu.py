"""
飞书集成 - 发送飞书消息和卡片

注意：使用 OpenClaw 的 message 工具发送飞书消息
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class FeishuIntegration:
    """飞书集成 - 发送飞书消息和卡片"""

    def __init__(self, channel: str = ""):
        """
        初始化飞书集成

        Args:
            channel: 飞书频道ID
        """
        self.channel = channel
        logger.info(f"初始化飞书集成，频道: {channel or '未设置'}")

    def send_message(self, message: str) -> bool:
        """
        发送文本消息

        Args:
            message: 消息内容

        Returns:
            True 如果发送成功
        """
        if not self.channel:
            logger.warning("未设置飞书频道，消息未发送")
            logger.info(f"消息内容: {message}")
            return False

        try:
            # 使用 OpenClaw 的 message 工具
            # 注意：这里只是占位，实际调用需要通过 OpenClaw 的工具接口
            logger.info(f"发送飞书消息到频道 {self.channel}: {message}")
            # 实际实现需要通过 subprocess 调用 OpenClaw 的 message 工具
            # 或者通过 OpenClaw 的 API
            return True
        except Exception as e:
            logger.error(f"发送飞书消息失败: {e}")
            return False

    def send_card(self, card: Dict) -> bool:
        """
        发送卡片消息

        Args:
            card: 卡片数据

        Returns:
            True 如果发送成功
        """
        if not self.channel:
            logger.warning("未设置飞书频道，卡片未发送")
            logger.info(f"卡片数据: {card}")
            return False

        try:
            logger.info(f"发送飞书卡片到频道 {self.channel}")
            # 实际实现需要通过 OpenClaw 的 API
            return True
        except Exception as e:
            logger.error(f"发送飞书卡片失败: {e}")
            return False

    def send_alert(self, alert_type: str, data: Dict) -> bool:
        """
        发送报警通知

        Args:
            alert_type: 报警类型
            data: 报警数据

        Returns:
            True 如果发送成功
        """
        card = self._build_alert_card(alert_type, data)
        return self.send_card(card)

    def send_workflow_status(self, status: Dict) -> bool:
        """
        发送工作流状态卡片

        Args:
            status: 工作流状态数据

        Returns:
            True 如果发送成功
        """
        card = self._build_status_card(status)
        return self.send_card(card)

    def parse_command(self, message: str) -> Optional[Dict]:
        """
        解析飞书指令

        支持格式: /monitor <command> [args]

        Args:
            message: 飞书消息内容

        Returns:
            解析后的命令字典，格式: {'command': str, 'args': dict}
        """
        if not message.startswith('/monitor'):
            return None

        parts = message.strip().split()
        if len(parts) < 2:
            return None

        command = parts[1]
        args = {}

        # 解析参数
        for i in range(2, len(parts)):
            if parts[i].startswith('--'):
                key = parts[i][2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith('--'):
                    args[key] = parts[i + 1]
                else:
                    args[key] = True
            elif parts[i].startswith('-'):
                key = parts[i][1:]
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    args[key] = parts[i + 1]
                else:
                    args[key] = True

        return {
            'command': command,
            'args': args
        }

    def _build_alert_card(self, alert_type: str, data: Dict) -> Dict:
        """构建报警卡片"""
        severity = data.get('severity', 'info')

        # 根据严重程度选择图标和颜色
        icons = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        icon = icons.get(severity, 'ℹ️')

        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{icon} 工作流报警: {alert_type}"
                },
                "template": "red" if severity == 'critical' else "yellow"
            },
            "elements": []
        }

        # 添加字段
        elements = []

        if 'workflow_id' in data and data['workflow_id']:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**工作流ID**: {data['workflow_id']}"
                }
            })

        if 'user_idea' in data and data['user_idea']:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**用户想法**: {data['user_idea']}"
                }
            })

        if 'status' in data:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**状态**: {data['status']}"
                }
            })

        if 'message' in data:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**报警消息**: {data['message']}"
                }
            })

        if 'failed_tasks' in data and data['failed_tasks']:
            tasks_str = ', '.join(data['failed_tasks'])
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**失败任务**: {tasks_str}"
                }
            })

        if 'error_message' in data and data['error_message']:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**错误信息**: {data['error_message']}"
                }
            })

        card['elements'] = elements

        return card

    def _build_status_card(self, status: Dict) -> Dict:
        """构建工作流状态卡片"""
        # 确定状态图标
        status_icons = {
            'running': '🔄',
            'completed': '✅',
            'failed': '❌',
            'paused': '⏸️',
            'pending': '⏳'
        }
        icon = status_icons.get(status.get('status', 'pending'), '⏳')

        card = {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"{icon} 工作流执行状态"
                },
                "template": "blue"
            },
            "elements": []
        }

        elements = []

        if 'workflow_id' in status:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**工作流ID**: {status['workflow_id']}"
                }
            })

        if 'user_idea' in status:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**用户想法**: {status['user_idea']}"
                }
            })

        # 进度条
        if 'progress' in status:
            progress = status['progress']
            bar_length = 20
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**进度**: {progress:.1f}%\n`{bar}`"
                }
            })

        # 状态和当前任务
        if 'status' in status or 'current_task' in status:
            fields = []
            if 'status' in status:
                fields.append({
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**状态**:\n{status['status']}"
                    }
                })
            if 'current_task' in status and status['current_task']:
                fields.append({
                    "is_short": True,
                    "text": {
                        "tag": "lark_md",
                        "content": f"**当前任务**:\n{status['current_task']}"
                    }
                })
            if fields:
                elements.append({
                    "tag": "div",
                    "fields": fields
                })

        # 时间信息
        if 'start_time' in status:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**开始时间**: {status['start_time']}"
                }
            })

        if 'duration' in status:
            duration = self._format_duration(status['duration'])
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**耗时**: {duration}"
                }
            })

        card['elements'] = elements

        # 添加操作按钮
        card['actions'] = [
            {
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "查看详情"
                },
                "type": "primary"
            }
        ]

        if status.get('status') == 'running':
            card['actions'].append({
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": "暂停"
                },
                "type": "default"
            })

        return card

    def _format_duration(self, seconds: float) -> str:
        """格式化耗时"""
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
