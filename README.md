# ChatLogs 插件

## 插件简介

ChatLogs 是一款为 [lang-bot](https://github.com/RockChinQ/LangBot) 设计的多平台聊天历史记录插件，支持将对话流水线回复的消息结构化存储到 Elasticsearch 或 MySQL（预留）。插件具备高扩展性、低耦合、配置灵活等特点，适合多场景运维和数据分析。

---

## 主要功能

- 支持多平台（如飞书、微信、钉钉、Slack、Discord）聊天历史记录，平台可独立开关
- 支持多种存储后端，当前实现 Elasticsearch，预留 MySQL 支持
- 仅记录通过 lang-bot 流水线回复的有效消息，避免无效日志
- 配置项全部通过 WebUI 管理，支持热更新，无需重启
- 插件启用/禁用由 lang-bot 统一管理，逻辑简洁
- 结构化日志，便于后续检索、分析和可视化
- 高度解耦，便于扩展新平台和新存储类型

---

## 安装与依赖

1. 将 `chatLogs` 目录放入 lang-bot 插件目录（如 `plugins/`）。
2. 启动 lang-bot，插件会自动安装依赖（见 `requirements.txt`）。
3. 进入 WebUI 插件管理界面，启用 ChatLogs 插件并配置参数。

**依赖：**
- elasticsearch >=7.0.0,<10.0.0
- PyYAML >=5.0.0,<7.0.0

---

## 配置说明

所有配置项均可在 WebUI 插件管理界面动态设置：

- **存储类型**：`storage_type`，可选 `es`（Elasticsearch）或 `mysql`（MySQL，预留）
- **平台独立开关**：如 `lark_log_enabled`、`wechatpad_log_enabled` 等，控制是否记录该平台消息
- **存储配置**：
  - 选择 es 时，填写 es_host、es_port、es_index、es_username、es_password、es_scheme
  - 选择 mysql 时，填写 mysql_host、mysql_port、mysql_db、mysql_user、mysql_password
- 只有当前存储类型相关的配置项会显示，界面简洁
- 插件启用/禁用由 lang-bot 统一管理，无需额外配置

---

## 使用流程

1. 启用插件，选择存储类型并填写相关配置，勾选需要记录的平台开关
2. 插件自动初始化存储后端，注册事件监听器
3. 有消息通过 lang-bot 流水线被回复时，自动判断平台和开关，结构化写入日志
4. 日志内容包括平台、会话ID、用户ID、回复内容、时间戳等
5. 存储异常自动捕获并输出错误日志，不影响主流程

---

## 扩展性

- **扩展新平台**：在 `sessionlog/` 目录下新增对应平台的判断逻辑，并在 main.py 调用即可
- **扩展新存储**：在 `storage/` 目录下新增存储实现，并在 main.py 的 `initialize` 里注册即可
- **日志字段扩展**：在 main.py 的 log 字典中补充即可

---

## 注意事项

- MySQL 存储为预留功能，当前未实现实际写入
- 只有平台名被正确识别且平台独立开关开启时才会记录日志
- 插件启用/禁用、配置热更新均由 lang-bot 统一管理
- 存储异常会被捕获并输出日志，不影响主流程

---

## 目录结构

```
chatLogs/
  main.py
  manifest.yaml
  requirements.txt
  storage/
    __init__.py
    es_storage.py
    mysql_storage.py
  sessionlog/
    __init__.py
    lark.py
  icon.png
  __init__.py
```

---

## 贡献与反馈

如需扩展新平台、新存储或有其它建议，欢迎提交 issue 或 PR。 