"""
测试 utils/i18n.py 语言模块
覆盖：语言切换、文案翻译、模板翻译、英文到中文的反向映射
"""
import importlib
import pytest

import utils.i18n as i18n


@pytest.fixture
def isolated_lang(tmp_path, monkeypatch):
    """把语言文件指向临时目录，并在测试后恢复默认中文"""
    lang_file = tmp_path / "i18n.lang"
    monkeypatch.setattr(i18n, '_LANG_FILE', str(lang_file))
    monkeypatch.setattr(i18n, '_current', None)
    yield lang_file
    i18n._current = None


class TestGetSetLang:
    def test_default_is_chinese(self, isolated_lang):
        assert i18n.get_lang() == 'zh'

    def test_set_lang_persists(self, isolated_lang):
        i18n.set_lang('en')
        assert isolated_lang.read_text(encoding='utf-8') == 'en'
        # 模拟重启：清空内存缓存后从文件读取
        i18n._current = None
        assert i18n.get_lang() == 'en'

    def test_set_lang_back_to_chinese(self, isolated_lang):
        i18n.set_lang('en')
        i18n.set_lang('zh')
        i18n._current = None
        assert i18n.get_lang() == 'zh'


class TestTranslate:
    def test_chinese_passthrough(self, isolated_lang):
        i18n.set_lang('zh')
        assert i18n._('筛选账单') == '筛选账单'

    def test_english_translation(self, isolated_lang):
        i18n.set_lang('en')
        assert i18n._('筛选账单') == 'Filter Bills'
        assert i18n._('记账本') == 'Bookkeeping'

    def test_missing_key_fallback(self, isolated_lang):
        i18n.set_lang('en')
        # 词典里没有的文案原样返回，保证界面不因漏翻而崩溃
        assert i18n._('不存在的文案xyz') == '不存在的文案xyz'

    def test_template_translation(self, isolated_lang):
        i18n.set_lang('en')
        text = i18n._t('已从{source}导入 {n} 条记录').format(source='CSV', n=3)
        assert text == 'Imported 3 records from CSV'

    def test_template_chinese(self, isolated_lang):
        i18n.set_lang('zh')
        text = i18n._t('已从{source}导入 {n} 条记录').format(source='CSV', n=3)
        assert text == '已从CSV导入 3 条记录'


class TestToZh:
    def test_reverse_mapping_english(self, isolated_lang):
        i18n.set_lang('en')
        assert i18n.to_zh('Expense') == '支出'
        assert i18n.to_zh('All') == '全部'
        # 分类（餐饮等）属于数据层，有意不翻译，原样返回
        assert i18n.to_zh('餐饮') == '餐饮'

    def test_reverse_mapping_chinese_mode(self, isolated_lang):
        i18n.set_lang('zh')
        # 中文模式下原样返回
        assert i18n.to_zh('支出') == '支出'

    def test_reverse_mapping_unknown(self, isolated_lang):
        i18n.set_lang('en')
        assert i18n.to_zh('SomethingElse') == 'SomethingElse'


class TestDictionaryIntegrity:
    def test_templates_have_matching_placeholders(self):
        """中英模板必须使用一致的命名占位符"""
        import re
        for zh_t, en_t in i18n.EN_TEMPLATES.items():
            zh_keys = set(re.findall(r'\{(\w+)\}', zh_t))
            en_keys = set(re.findall(r'\{(\w+)\}', en_t))
            assert zh_keys == en_keys, f'模板占位符不一致: {zh_t}'

    def test_reverse_map_consistency(self):
        """反向映射的英文值能映射回其中文键（多个中文同译时容忍二选一）"""
        from collections import Counter
        en_counts = Counter(i18n.EN.values())
        for zh_text, en_text in i18n.EN.items():
            if en_counts[en_text] > 1:
                continue  # 同义多译（如月度/每月收支柱状图）允许映射到任一键
            assert i18n._REV[en_text] == zh_text
