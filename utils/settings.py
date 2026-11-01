"""应用设置：以 JSON 文件持久化用户偏好（字体大小等），默认设置内置。

设置文件与语言配置同目录：database/settings.json
"""
import json
import os

_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'settings.json')

# 内置默认值：None 表示跟随系统默认（Tk 默认字号 + 2）
DEFAULTS = {
    'menu_font_size': None,   # 菜单字号（绝对像素值）
    'ui_font_size': None,     # 界面正文字号（绝对像素值）
}

_cache = None


def _load():
    """从文件读取设置并与默认值合并"""
    data = {}
    try:
        if os.path.exists(_SETTINGS_FILE):
            with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
    except Exception:
        data = {}
    settings = dict(DEFAULTS)
    if isinstance(data, dict):
        settings.update({k: v for k, v in data.items() if k in DEFAULTS})
    return settings


def get_settings():
    """当前设置（带内存缓存）"""
    global _cache
    if _cache is None:
        _cache = _load()
    return dict(_cache)


def set_setting(key, value):
    """更新单项设置并持久化"""
    global _cache
    if key not in DEFAULTS:
        raise KeyError(f'未知设置项: {key}')
    settings = get_settings()
    settings[key] = value
    _cache = settings
    try:
        os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return settings
