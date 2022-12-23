# encoding: utf-8
import unittest

import datetime

import counta

class datetime_FixedToday(datetime.datetime):
    @classmethod
    def today(cls):
        return cls(2020, 4, 1, 12, 34, 56)
# 普通に today が返るとテストしづらいので無理やり固定文字列にオーバーライドする
datetime.datetime = datetime_FixedToday

def generate_root_hline(s):
    lines = counta.string2lines(s)
    root_hline = counta.HierarchicalLine.parse(lines)
    return root_hline

class TestUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_indent_depth(self):
        f = self.assertEqual

        e = 0
        a = counta.get_indent_depth('')
        f(e, a)

        e = 0
        a = counta.get_indent_depth('a')
        f(e, a)

        e = 1
        a = counta.get_indent_depth(' aaa')
        f(e, a)

        e = 2
        a = counta.get_indent_depth('  あいう')
        f(e, a)

        e = 3
        a = counta.get_indent_depth('   ')
        f(e, a)

    def test_remove_indent(self):
        f = self.assertEqual

        e = ''
        a = counta.remove_indent('')
        f(e, a)

        e = ''
        a = counta.remove_indent(' ')
        f(e, a)

        e = ''
        a = counta.remove_indent('    ')
        f(e, a)

        e = 'a'
        a = counta.remove_indent('a')
        f(e, a)

        e = 'aa'
        a = counta.remove_indent(' aa')
        f(e, a)

        e = 'abc'
        a = counta.remove_indent('      abc')
        f(e, a)

    def test_validate_datetimestr(self):
        f = counta.is_valid_datetimestr

        self.assertTrue(f('2022/12/22 thu 16:56:43'))
        self.assertTrue(f('2022/12/22 Thu 16:56:43'))
        self.assertTrue(f('2022/12/22 DOW 16:56:43'), 'ちょっと端折ってるので3文字なら何でもいい')

        self.assertFalse(f(''))
        self.assertFalse(f('2022/12/22 16:56:43'))
        self.assertFalse(f('2022/12/22 thu 16:56:1'))
        self.assertFalse(f('2023/02/31 16:56:43'))

class TestHierarchicalLine(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_interactive_normal(self):
        scb = """scb page sample
a
a
a
 b
a
 b
 b
a
 b
  c
 b
  c
  c
 b
  c
a
blank, blank1, blank2

 
  
a
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        s = counta.HierarchicalLine.to_string(root_hline)

        a = s
        e = scb
        self.assertEqual(e, a)

    def test_parse_interactive_abnormal(self):
        scb = """矯正するパターン
a
 b
  c
a
  c ここは-1段矯正される
a
   d ここは-2段矯正される
a
  c
  c ここは、上のcが深さ1になるので、その下にぶら下がる形になる。矯正されない
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        s = counta.HierarchicalLine.to_string(root_hline)

        expect = """矯正するパターン
a
 b
  c
a
 c ここは-1段矯正される
a
 d ここは-2段矯正される
a
 c
  c ここは、上のcが深さ1になるので、その下にぶら下がる形になる。矯正されない
"""

        actual = s
        self.assertEqual(expect, actual)

    def test_parse_correctly(self):
        scb = """a
a
a
a
a
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        e = 6
        a = len(root_hline.children)
        self.assertEqual(e, a)

        scb = """a
 b
a
 b
a
 b
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        e = 4
        a = len(root_hline.children)
        self.assertEqual(e, a)

        scb = """a
 b
 c
a
 b
 c
a
 b
 c
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        e = 4
        a = len(root_hline.children)
        self.assertEqual(e, a)

        scb = """a
 b
  c
a
 b
  c
   d


a
a
 b
  c
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        e = 7
        a = len(root_hline.children)
        self.assertEqual(e, a)

    def test_object_editing(self):
        scb = """洗濯
今のところ
 ドラム式洗濯乾燥機使用中
 2日に1回ペース
  毎日だと寿命エグいので
  たまに冬物上着などイレギュラーを洗うときは3日連続になる

@counta routine
 @2
 2022/12/18
 2022/12/19

@counta counter
 2022/12/17 07:18:33
 2022/12/16 07:18:31
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        e = 7
        a = len(root_hline.children)
        self.assertEqual(e, a, 'トップレベル要素の数が一致する')

        hline_routine_directive = root_hline.children[3]
        hline_counter_directive = root_hline.children[5]

        e = '@counta routine'
        a = hline_routine_directive.line
        self.assertEqual(e, a, 'ディレクティブがちゃんとパースされている')
        e = '@counta counter'
        a = hline_counter_directive.line
        self.assertEqual(e, a)

        hline = counta.HierarchicalLine('2022/12/21', indent_depth=1)
        hline_routine_directive.children.append(hline)
        hline = counta.HierarchicalLine('2022/12/18 08:06:45 最近乾燥時の音エグいけど大丈夫？', indent_depth=1)
        hline_counter_directive.children.insert(0, hline)
        actual = counta.HierarchicalLine.to_string(root_hline)
        expect = """洗濯
今のところ
 ドラム式洗濯乾燥機使用中
 2日に1回ペース
  毎日だと寿命エグいので
  たまに冬物上着などイレギュラーを洗うときは3日連続になる

@counta routine
 @2
 2022/12/18
 2022/12/19
 2022/12/21

@counta counter
 2022/12/18 08:06:45 最近乾燥時の音エグいけど大丈夫？
 2022/12/17 07:18:33
 2022/12/16 07:18:31
"""
        self.assertEqual(expect, actual)

    def test_flat(self):
        scb = """flatのテスト
a
 b
  c
 b
  c
   d
a
 b
a
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        hlines = counta.HierarchicalLine.flat(root_hline)

        e = 11 + 1 # rootがある
        a = len(hlines)
        self.assertEqual(e, a)

        e = 'a'
        a = hlines[2].line
        self.assertEqual(e, a)

        e = ['d', 3]
        a = [hlines[7].line, hlines[7].indent_depth]
        self.assertEqual(e, a)

    def test_append_guard(self):
        scb = 'line'
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        line = 'この行を挿入します'
        with self.assertRaises(RuntimeError):
            root_hline.append(line)

        hline = counta.HierarchicalLine(line, indent_depth=0)
        root_hline.append(hline)

class DebugSource(counta.DataSource):
    def __init__(self, path_prefix='', path_suffix=''):
        super().__init__(path_prefix, path_suffix)
        self._data = {}

    @property
    def fullpath(self):
        fullpath = f'{self._path_prefix}{self._path_body}{self._path_suffix}'
        return fullpath

    def exists(self):
        key = self.fullpath
        return key in self._data

    def read_as_lines(self):
        key = self.fullpath
        lines = self._data[key]
        return lines

    def write_lines(self, lines):
        key = self.fullpath
        self._data[key] = lines

class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self._data_source = DebugSource(path_prefix='', path_suffix='.scb')

    def tearDown(self):
        pass

    def test_line2counternames(self):
        f = counta.Workspace.line2pairs_of_countername_and_comment

        def extract_counternames(pairs):
            return [pair[0] for pair in pairs]

        # コメントなしで純粋に取り出せてるか一通り見る

        e = []
        a = extract_counternames(f(''))
        self.assertEqual(e, a)

        e = ['a']
        a = extract_counternames(f('[a]'))
        self.assertEqual(e, a)

        e = ['あいう']
        a = extract_counternames(f('[あいう]'))
        self.assertEqual(e, a)

        e = ['あいう', 'さしす']
        a = extract_counternames(f('[あいう]かきく[さしす]'))
        self.assertEqual(e, a)

        e = ['かきく', 'さしす', 'なに']
        a = extract_counternames(f('あいう[かきく][さしす]たちつてと[なに]ぬねの'))
        self.assertEqual(e, a)

        e = ['洗濯', 'シャッフル', 'プロジェクト1', 'お風呂', '郵便局']
        a = extract_counternames(f('[洗濯] [シャッフル] [プロジェクト1] [お風呂] [郵便局]'))
        self.assertEqual(e, a)

        # コメントも取れるか見る

        a = f('/')
        self.assertEqual(0, len(a))

        a = f('/ここはそもそもカウンターじゃないのでパースされない')
        self.assertEqual(0, len(a))

        a = f('[洗濯]/乾燥の音が最近うるさくてねぇ')
        self.assertEqual(['洗濯', '乾燥の音が最近うるさくてねぇ'], a[0])

        a = f('[洗濯]/')
        self.assertEqual(['洗濯', ''], a[0])

        a = f('[洗濯]/a')
        self.assertEqual(['洗濯', 'a'], a[0])

        a = f('[aaa] [bbb]/comment1 [ccc]/comment2')
        self.assertEqual(['aaa', ''], a[0])
        self.assertEqual(['bbb', 'comment1'], a[1])
        self.assertEqual(['ccc', 'comment2'], a[2])

    def test_parse_onepass(self):
        scb = """[洗濯]/ [シャッフル] [郵便局]/平日しか空いてないのだるー [お風呂] [食事] [床掃除] [排水溝掃除]/キッチンの奥が手強いんだが
@counta workspace
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)

        a = workspace._commenters
        f = self.assertEqual
        f(['洗濯', ''], a[0])
        f(['シャッフル', ''], a[1])
        f(['郵便局', '平日しか空いてないのだるー'], a[2])
        f(['お風呂', ''], a[3])
        f(['食事', ''], a[4])
        f(['床掃除', ''], a[5])
        f(['排水溝掃除', 'キッチンの奥が手強いんだが'], a[6])

        a = workspace.counters
        e = 7
        self.assertEqual(e, len(a))
        self.assertEqual('洗濯', a[0].name)
        self.assertEqual(['', '@counta counter'], a[0].to_lines())
        self.assertEqual('郵便局', a[2].name)
        indent1 = ' '
        self.assertEqual(['', '@counta counter', f'{indent1}{counta.today_datetimestr()} 平日しか空いてないのだるー'], a[2].to_lines())

    def test_parse_error(self):
        scb = """[counter1] [counter2]
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        workspace = counta.Workspace(self._data_source)
        with self.assertRaises(RuntimeError):
            workspace.parse(root_hline)

        scb = """[counter1] [counter2]
 @counta workspace
トップラインに書かないとエラー
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        workspace = counta.Workspace(self._data_source)
        with self.assertRaises(RuntimeError):
            workspace.parse(root_hline)

class TestCounter(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def generate_counter(s, name='カウンター名を入れてください'):
        root_hline = generate_root_hline(s)
        counter = counta.Counter.parse(root_hline)
        counter.name = name
        return counter

    def test_from_0(self):
        counter = self.generate_counter("""カウンターのてすと
てきとうに
 コンテンツを
 追加して
その後で
 counter directiveを追加しておく

@counta counter
""", 'テストカウンター1')

        self.assertEqual('テストカウンター1', counter.name)
        self.assertEqual(0, counter.count)

    def test_from_multi(self):
        counter = self.generate_counter("""カウンターのてすと
てきとうに
 コンテンツを
 追加して
その後で
 counter directiveを追加しておく

@counta counter
 2022/12/31 DOW 23:59:59 新年だぁぁぁ！
 2022/12/22 DOW 12:34:56
""", 'テストカウンター2')

        self.assertEqual(2, counter.count)

        ce0 = counter.count_elements_by_object[0]
        self.assertEqual('2022/12/31 DOW 23:59:59', ce0.datetime)
        self.assertEqual('新年だぁぁぁ！', ce0.comment)

    def test_adding(self):
        counter = self.generate_counter("""最初からだけどガンガン足してく
@counta counter
""", 'テストカウンター3')

        counter.add_count()
        counter.add_count()
        counter.add_count('with comment')

        self.assertEqual(3, counter.count)
        ce0 = counter.count_elements_by_object[0]
        self.assertEqual(f'{counta.today_datetimestr()}', ce0.datetime)
        self.assertEqual('', ce0.comment)
        ce2 = counter.count_elements_by_object[2]
        self.assertEqual(f'{counta.today_datetimestr()}', ce2.datetime)
        self.assertEqual('with comment', ce2.comment)

    def test_from_in_case_of_invalid(self):
        counter = self.generate_counter("""カウンターのてすと
@counta counter
 2022/12/31 DOW 23:59:1 桁が足りません
""", 'coutername')
        with self.assertRaises(RuntimeError):
            counter.count_elements_by_object[0]

        counter = self.generate_counter("""カウンターのてすと
@counta counter
 2022/12/31 23:59:59 曜日がありません
""", 'coutername')
        with self.assertRaises(RuntimeError):
            counter.count_elements_by_object[0]

        counter = self.generate_counter("""カウンターのてすと
@counta counter
 2022/12/31 DOW 25:59:59 無効な日付時刻です
""", 'coutername')
        with self.assertRaises(RuntimeError):
            counter.count_elements_by_object[0]

    def test_serialize_deserialize(self):
        counter = self.generate_counter("""aaa
 bbb
  ccc

@counta counter
 2022/12/22 thu 19:04:12 count1
 2022/12/22 thu 19:14:12 count2

ディレクティブはどこに書いてもいいよ
 hello
 `print('hello')`
""", 'coutername')

        counter.add_count()
        counter.add_count('コメント')

        todaystr = counta.today_datetimestr()
        expect = f"""aaa
 bbb
  ccc

@counta counter
 2022/12/22 thu 19:04:12 count1
 2022/12/22 thu 19:14:12 count2
 {todaystr}
 {todaystr} コメント

ディレクティブはどこに書いてもいいよ
 hello
 `print('hello')`
"""
        actual = counta.lines2string(counter.to_lines())
        self.assertEqual(expect, actual)

    def test_for_sort(self):
        counter = self.generate_counter("""カウンター
@counta counter
 2022/12/21 wed 19:04:12 あ
 2022/12/20 tue 19:04:12 い
 2022/12/19 mon 19:04:12 う
""", 'coutername')

        e = '2022/12/21 wed 19:04:12'
        a = counter.get_latest_datetime()
        self.assertEqual(e, a)

        e = '2022/12/19 mon 19:04:12'
        a = counter.get_oldest_datetime()
        self.assertEqual(e, a)

if __name__ == '__main__':
    unittest.main()
