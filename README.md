# 天开 - AppProduct 工作流监控管理 Agent

## 📋 项目简介

"天开" 是一个专业的 AppProduct 工作流监控管理 Agent，用于监控和管理基于 CrewAI 的多 Agent 协作系统。

## ✨ 核心功能

### 监控功能
- ✅ 实时监控工作流执行状态
- ✅ 成功率统计（总体、按日期、按Agent）
- ✅ 耗时分析（平均、分位数、最大最小）
- ✅ 瓶颈任务识别
- ✅ Token使用量分析

### 管理功能
- ✅ 手动触发工作流（同步/异步）
- ✅ 暂停/恢复工作流
- ✅ 工作流状态查询
- ✅ 指标数据查询

### 报警功能
- ✅ 工作流失败自动报警
- ✅ 任务失败自动报警
- ✅ 超时报警（可配置）
- ✅ 重试次数超限报警
- ✅ 报警规则可配置

### 飞书集成
- ✅ 飞书消息通知
- ✅ 飞书卡片消息
- ✅ 飞书指令解析
- ✅ 报警通知卡片
- ✅ 工作流状态卡片

## 🏗️ 项目结构

```
appProduct-monitoring-agent/
├── core/
│   ├── __init__.py
│   ├── monitor.py          # 核心监控逻辑
│   ├── alert.py            # 报警引擎
│   └── scheduler.py        # 任务调度器
├── integrations/
│   ├── __init__.py
│   ├── feishu.py          # 飞书集成
│   └── cli.py             # CLI接口
├── analytics/
│   ├── __init__.py
│   ├── metrics.py         # 指标分析
│   └── reporter.py        # 报告生成
├── management/
│   ├── __init__.py
│   ├── trigger.py         # 触发器
│   └── controller.py      # 工作流控制器
├── config/
│   ├── agent_config.yaml   # Agent配置
│   └── alert_rules.yaml   # 报警规则
├── tests/
│   ├── test_monitor.py     # 监控模块测试
│   └── test_alert.py      # 报警模块测试
├── main.py                # 主入口
├── requirements.txt       # 依赖项
└── README.md              # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config/agent_config.yaml` 文件，配置以下内容：

```yaml
# appProduct 项目目录
app_product_dir: "/path/to/appProduct"

# 监控配置
monitoring:
  interval: 5  # 监控间隔（秒）
  enable_auto_start: false  # 自动启动监控

# 飞书集成配置
feishu:
  enabled: true
  app_id: "your_app_id"
  app_secret: "your_app_secret"
  channel: "your_channel_id"  # 飞书频道ID（可选）

# 报警配置
alert:
  enabled: true
  rules_file: "config/alert_rules.yaml"
```

### 3. 运行

```bash
# 查看帮助
python main.py --help

# 查看状态
python main.py status

# 查看指标
python main.py metrics --days 7

# 触发工作流
python main.py trigger --idea "我想做一个待办APP"

# 异步触发工作流
python main.py trigger --idea "我想做一个待办APP" --async

# 暂停工作流
python main.py pause --workflow-id wf-20260403-001

# 恢复工作流
python main.py resume --workflow-id wf-20260403-001
```

## 📊 使用示例

### 查看工作流状态

```bash
$ python main.py status

工作流状态:
  工作流ID: wf-20260403-001
  用户想法: 我想做一个待办APP
  状态: running
  进度: 55.6%
  当前任务: development_agent
```

### 查看指标分析

```bash
$ python main.py metrics --days 7

指标分析报告（最近 7 天）:
  总体成功率: 95.0%
  总执行次数: 20
  平均耗时: 2540.0 秒
  瓶颈任务: development_agent
```

### 触发工作流

```bash
$ python main.py trigger --idea "我想做一个电商APP" --async

工作流已触发，ID: wf-20260403-002
异步模式: True
```

## ⚙️ 配置说明

### 报警规则配置

编辑 `config/alert_rules.yaml` 文件：

```yaml
rules:
  # 工作流失败报警
  - name: workflow_failure
    enabled: true
    condition: "status == 'failed'"
    severity: "critical"
    message: "🚨 工作流执行失败"

  # 任务失败报警
  - name: task_failure
    enabled: true
    condition: "any(task.status == 'failed' for task in tasks)"
    severity: "warning"
    message: "⚠️ 任务执行失败"

  # 超时报警（1小时）
  - name: timeout
    enabled: true
    condition: "duration > 3600"
    severity: "warning"
    message: "⏰ 工作流执行超时（1小时）"

  # 重试次数超限
  - name: retry_exceeded
    enabled: true
    condition: "retry_count > 3"
    severity: "critical"
    message: "🔄 重试次数超限"
```

## 🧪 测试

运行单元测试：

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_monitor.py -v
pytest tests/test_alert.py -v
```

## 📝 开发进度

- ✅ 阶段1：核心监控功能（完成）
  - 项目结构创建
  - 核心监控模块
  - 指标分析模块
  - 报告生成器
  - 单元测试（9个测试用例全部通过）

- ✅ 阶段2：报警系统（完成）
  - 报警引擎实现
  - 飞书集成实现
  - 报警规则配置
  - 单元测试（7个测试用例全部通过）

- 🔄 阶段3：管理功能（部分完成）
  - 工作流触发器实现
  - 工作流控制器实现
  - CLI命令接口实现
  - 任务调度器（待完善）

- ⏳ 阶段4：飞书深度集成（待完成）

- ⏳ 阶段5：测试与优化（待完成）

## 🔧 技术栈

- **编程语言**: Python 3.8+
- **CLI框架**: Click
- **任务调度**: APScheduler
- **文件监控**: watchdog
- **配置管理**: YAML
- **飞书集成**: OpenClaw 的 `message` 工具
- **测试框架**: pytest

## 📚 相关文档

- [需求分析与技术方案](../appProduct-monitoring-agent-design.md)
- [工作流架构图](../appProduct-workflow-architecture-diagram.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

- 项目负责人: Product Analyst
- 开发者: Coder

---

**项目版本**: v1.0
**创建日期**: 2026-04-03
**Agent名称**: 天开
