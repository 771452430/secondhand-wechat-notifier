# secondhand-wechat-notifier

独立的「HTTP JSON 数据源 -> 微信群通知」服务。默认 preset 可接入 BIP 闲置小市集，也可以通过配置文件接入其他返回 JSON 列表的业务系统。

## Requirements

- macOS
- Python 3.10+
- Mac 微信已安装并登录
- 给终端或后台服务运行环境授权「辅助功能」

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

如果要使用真实微信发送器，并且 `pip install wxauto-mac` 不可用，可以先安装 GitHub 版本：

```bash
pip install "git+https://github.com/PatrickHua/wxauto-mac.git"
```

## Quick Start

```bash
notifier init-config --preset secondhand --output config.yaml
notifier validate-config --config config.yaml
notifier preview --config config.yaml
notifier send-test --config config.yaml
notifier digest-now --config config.yaml
notifier run --config config.yaml
```

开发或无微信环境下可把 `sender.type` 改成 `stdout`，消息会打印到终端，不会调用微信。

## macOS Background Service

```bash
notifier install-service --config /absolute/path/config.yaml
notifier service start
notifier service status
notifier service logs
notifier service stop
notifier uninstall-service
```

后台服务使用 `launchd`，日志默认写入 `~/Library/Logs/secondhand-wechat-notifier.log`。

## Configuration Shape

每个 `source` 描述一个 HTTP JSON 列表接口：

- `url`: 接口 path 或完整 URL
- `method`: 第一版支持 `GET`
- `query`: 固定查询参数
- `items_path`: 响应中列表所在路径，例如 `items` 或 `data.records`
- `id_field`: 唯一 ID 字段路径
- `created_at_field`: 创建时间字段路径
- `detail_url_template`: 详情页模板
- `fields`: 接口字段到模板变量的映射
- `message_template`: 单条新内容通知模板

去重键为 `{source.name}:{id}`，状态保存在本地 SQLite。
