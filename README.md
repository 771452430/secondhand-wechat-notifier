# secondhand-wechat-notifier

通用的 macOS 微信群通知工具：从一个或多个 HTTP JSON 列表接口读取新内容，按模板生成消息，并发送到指定微信群。

这个项目不是 BIP 闲置小市集的内部模块。它可以独立安装、独立运行；BIP 闲置小市集只是内置的一个示例 preset。任何能提供 JSON 列表接口的业务系统，都可以通过配置文件接入。

## Features

- 支持多个 HTTP JSON 数据源。
- 支持字段映射、详情链接模板和消息模板。
- 使用本地 SQLite 记录已发送内容，避免重复通知。
- 支持 `stdout` 发送器，方便无微信环境下预览和调试。
- 支持 macOS 微信发送器，通过辅助功能操作 Mac 微信。
- 支持 launchd 后台服务，适合长期轮询运行。

## Requirements

- macOS
- Python 3.10+
- 如果要真实发送到微信：
  - Mac 微信已安装并登录
  - 终端或后台服务运行环境已授权「辅助功能」
  - 安装真实微信发送器依赖

## Install

开发或本机直接使用：

```bash
git clone git@github.com:771452430/secondhand-wechat-notifier.git
cd secondhand-wechat-notifier
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

如果要调用真实 Mac 微信发送器，再安装 macOS 依赖：

```bash
pip install -e ".[mac]"
```

如果 `wxauto-mac` 没有随环境安装成功，可以安装 GitHub 版本：

```bash
pip install "git+https://github.com/PatrickHua/wxauto-mac.git"
```

安装后命令为：

```bash
wechat-notifier --help
```

## Quick Start

生成 BIP 闲置小市集示例配置：

```bash
wechat-notifier init-config --preset secondhand --output config.yaml
```

先把配置里的发送器改成 `stdout`，这样不会真的调用微信：

```yaml
sender:
  type: "stdout"
```

验证配置并预览消息：

```bash
wechat-notifier validate-config --config config.yaml
wechat-notifier preview --config config.yaml
```

发送一次测试消息：

```bash
wechat-notifier send-test --config config.yaml
```

立即拉取数据并发送新内容：

```bash
wechat-notifier digest-now --config config.yaml
```

长期轮询运行：

```bash
wechat-notifier run --config config.yaml
```

## Configuration

配置文件使用 YAML。最小结构包括站点、微信群、发送器、本地存储和数据源。

```yaml
site:
  api_base_url: "https://example.com/api/v1"
  web_base_url: "https://example.com"

wechat:
  group_name: "业务通知群"

sender:
  type: "stdout"

poll:
  enabled: true
  interval_seconds: 60

storage:
  sqlite_path: "./notifier-state.sqlite3"

sources:
  - name: "orders"
    label: "订单"
    url: "/orders"
    method: "GET"
    query:
      page: 1
      pageSize: 10
    items_path: "items"
    id_field: "id"
    created_at_field: "createdAt"
    detail_url_template: "{web_base_url}/orders/{id}"
    fields:
      title: "title"
      buyer: "buyer.name"
      price: "price"
    message_template: |
      【新订单】{title}
      买家：{buyer}
      金额：{price}
      详情：{url}
```

每个 `source` 描述一个 HTTP JSON 列表接口：

- `url`: 接口 path 或完整 URL。
- `method`: 当前支持 `GET`。
- `query`: 固定查询参数。
- `items_path`: 响应中列表所在路径，例如 `items` 或 `data.records`。
- `id_field`: 唯一 ID 字段路径，用于去重。
- `created_at_field`: 创建时间字段路径，用于展示和排序。
- `detail_url_template`: 详情页 URL 模板。
- `fields`: 接口字段到模板变量的映射，支持点路径和数组下标。
- `message_template`: 单条新内容通知模板。

去重键为 `{source.name}:{id}`，状态保存在本地 SQLite。

## BIP 闲置小市集 Preset

内置 `secondhand` preset 会生成两个数据源：

- `/listings`: 新闲置通知。
- `/wanted-posts`: 新求购通知。

它只是一个示例模板。其他项目可以复制生成的 `config.yaml`，替换 `site`、`wechat` 和 `sources` 后直接使用。

## macOS Background Service

安装 launchd 服务：

```bash
wechat-notifier install-service --config /absolute/path/config.yaml
```

管理服务：

```bash
wechat-notifier service start
wechat-notifier service status
wechat-notifier service logs
wechat-notifier service stop
wechat-notifier uninstall-service
```

后台服务日志默认写入：

```text
~/Library/Logs/secondhand-wechat-notifier.log
```

真实微信发送需要给服务运行环境授予 macOS「辅助功能」权限。如果服务能运行但无法操作微信，优先检查系统设置里的隐私与安全性授权。

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

建议先用 `stdout` sender 验证配置和模板，再切换到真实微信发送。
