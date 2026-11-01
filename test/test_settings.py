"""
测试 utils/settings.py 设置模块
覆盖：默认设置、持久化、单项更新、未知键拒绝、损坏文件回退
"""
import json
import pytest

import utils.settings as settings


@pytest.fixture
def isolated_settings(tmp_path, monkeypatch):
    """把设置文件指向临时目录，并在测试后清空缓存"""
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings, '_SETTINGS_FILE', str(settings_file))
    monkeypatch.setattr(settings, '_cache', None)
    yield settings_file
    settings._cache = None


class TestDefaults:
    def test_default_settings(self, isolated_settings):
        s = settings.get_settings()
        assert s['menu_font_size'] is None
        assert s['ui_font_size'] is None

    def test_defaults_are_copies(self, isolated_settings):
        s = settings.get_settings()
        s['ui_font_size'] = 99
        # 修改返回值不影响内部缓存
        assert settings.get_settings()['ui_font_size'] is None


class TestSetSetting:
    def test_set_and_persist(self, isolated_settings):
        settings.set_setting('menu_font_size', 16)
        assert isolated_settings.exists()
        on_disk = json.loads(isolated_settings.read_text(encoding='utf-8'))
        assert on_disk['menu_font_size'] == 16

    def test_reload_from_disk(self, isolated_settings):
        settings.set_setting('ui_font_size', 18)
        settings._cache = None  # 模拟重启
        assert settings.get_settings()['ui_font_size'] == 18

    def test_update_keeps_other_keys(self, isolated_settings):
        settings.set_setting('ui_font_size', 14)
        settings.set_setting('menu_font_size', 16)
        s = settings.get_settings()
        assert s['ui_font_size'] == 14
        assert s['menu_font_size'] == 16

    def test_unknown_key_rejected(self, isolated_settings):
        with pytest.raises(KeyError):
            settings.set_setting('not_a_setting', 1)


class TestRobustness:
    def test_corrupt_file_falls_back_to_defaults(self, isolated_settings):
        isolated_settings.write_text('{invalid json', encoding='utf-8')
        settings._cache = None
        s = settings.get_settings()
        assert s == settings.DEFAULTS

    def test_non_dict_file_falls_back(self, isolated_settings):
        isolated_settings.write_text('[1, 2, 3]', encoding='utf-8')
        settings._cache = None
        assert settings.get_settings() == settings.DEFAULTS

    def test_unknown_keys_in_file_ignored(self, isolated_settings):
        isolated_settings.write_text(
            json.dumps({'ui_font_size': 15, 'hack': True}), encoding='utf-8')
        settings._cache = None
        s = settings.get_settings()
        assert s['ui_font_size'] == 15
        assert 'hack' not in s
