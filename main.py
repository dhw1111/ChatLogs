# 新版插件机制：所有配置项通过manifest.yaml声明，self.config读取，无config.yaml依赖
import os
import sys
import subprocess

def install_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        try:
            import elasticsearch  # noqa: F401
            import yaml  # noqa: F401
        except ImportError:
            print("[chatLogs] Installing requirements...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])

install_requirements()

from pkg.plugin.context import register, handler, BasePlugin, EventContext
from pkg.plugin.events import NormalMessageResponded
from datetime import datetime
from .storage.es_storage import ESStorage
from .storage.mysql_storage import MySQLStorage
from .sessionlog.lark import should_record_lark

@register(
    name="ChatLogs",
    description="聊天日志插件，仅记录通过流水线回复规则的多平台消息到ES/MySQL",
    version="1.0.0",
    author="dhw"
)
class ChatLogsPlugin(BasePlugin):
    def __init__(self, host):
        super().__init__(host)
        self.storage = None

    async def initialize(self):
        storage_type = self.config.get('storage_type', 'es')
        if storage_type == 'es':
            self.storage = ESStorage(self.config)
        elif storage_type == 'mysql':
            self.storage = MySQLStorage(self.config)
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")

    def _get_event_platform(self, ctx: EventContext):
        session = getattr(ctx.event, 'session', None)
        if session and hasattr(session, 'platform') and getattr(session, 'platform'):
            return getattr(session, 'platform')
        query = getattr(ctx.event, 'query', None)
        if query and hasattr(query, 'platform') and getattr(query, 'platform'):
            return getattr(query, 'platform')
        event_obj = getattr(ctx.event, 'source_platform_object', None)
        if event_obj and hasattr(event_obj, 'platform') and getattr(event_obj, 'platform'):
            return getattr(event_obj, 'platform')
        if hasattr(ctx.event, 'platform') and getattr(ctx.event, 'platform'):
            return getattr(ctx.event, 'platform')
        return None

    def _should_log(self, platform_name: str = None):
        # 只依赖当前平台独立开关，插件启用/禁用交由lang-bot统一管理
        if platform_name:
            enabled_key = f'{platform_name}_log_enabled'
            return self.config.get(enabled_key, True)
        return True

    @handler(NormalMessageResponded)
    async def on_normal_message_responded(self, ctx: EventContext):
        platform = self._get_event_platform(ctx)
        if not platform:
            self.ap.logger.warning("无法识别消息平台，跳过聊天日志记录")
            return
        # 只记录飞书平台（lark），便于后续扩展其它平台
        if not should_record_lark(platform):
            return
        if not self._should_log(platform):
            return
        response_text = getattr(ctx.event, 'response_text', '')
        reply = getattr(ctx.event, 'reply', None)
        if (not response_text or response_text.strip() == '') and (not reply or len(reply) == 0):
            return
        log = {
            'type': 'pipeline_responded',
            'platform': platform,
            'launcher_type': getattr(ctx.event, 'launcher_type', ''),
            'launcher_id': getattr(ctx.event, 'launcher_id', ''),
            'sender_id': getattr(ctx.event, 'sender_id', ''),
            'response_text': response_text,
            'reply': reply,
            'funcs_called': getattr(ctx.event, 'funcs_called', []),
            'timestamp': datetime.now().isoformat(),
        }
        try:
            if self.storage:
                self.storage.save_log(log)
        except Exception as e:
            self.ap.logger.error(f"保存聊天日志失败: {e}") 