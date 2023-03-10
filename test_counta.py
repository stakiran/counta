# encoding: utf-8
import unittest

import datetime

import counta

class datetime_FixedToday(datetime.datetime):
    @classmethod
    def today(cls):
        return cls(2020, 4, 1, 12, 34, 56)
class datetime_FixedToday_2023(datetime.datetime):
    @classmethod
    def today(cls):
        return cls(2023, 4, 1, 12, 34, 56)
class datetime_FixedToday_2024(datetime.datetime):
    @classmethod
    def today(cls):
        return cls(2024, 4, 1, 12, 34, 56)
class datetime_FixedToday_2025(datetime.datetime):
    @classmethod
    def today(cls):
        return cls(2025, 4, 1, 12, 34, 56)
# 普通に today が返るとテストしづらいので無理やり固定文字列にオーバーライドする
datetime.datetime = datetime_FixedToday

def generate_root_hline(s):
    lines = counta.string2lines(s)
    root_hline = counta.HierarchicalLine.parse(lines)
    return root_hline

def print_lines(lines):
    for line in lines:
        print(line)

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
        hline_routine_directive.append(hline)
        hline = counta.HierarchicalLine('2022/12/18 08:06:45 最近乾燥時の音エグいけど大丈夫？', indent_depth=1)
        hline_counter_directive.prepend(hline)
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

    # 1 実際はファイル名修正が入る
    # 2 テストでは何もしてないので入らない
    # 3 が、テストコードは修正が入る前提で書きたい
    # なのだが、これでは 2 のときに手動で修正を入れないといけない。ハマる。
    # ハマりたくないので、より現実を模倣し、テスト時にも修正が入るようオーバーライドする。
    def set_pathbody(self, path_body):
        self._path_body = counta.get_corrected_filename(path_body)

class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self._data_source = DebugSource(path_prefix='', path_suffix='.scb')

    def tearDown(self):
        datetime.datetime = datetime_FixedToday

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
        scb = """[洗濯] [シャッフル] [郵便局]/平日しか空いてないのだるー [お風呂] [食事] [床掃除] [排水溝掃除]/キッチンの奥が手強いんだが
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

        indent1 = ' '
        today_datestr = counta.today_datetimestr()

        a = workspace.counters
        e = 7
        self.assertEqual(e, len(a))
        self.assertEqual('洗濯', a[0].name)
        self.assertEqual(['', '@counta counter', f'{indent1}{today_datestr}'], a[0].to_lines())
        self.assertEqual('郵便局', a[2].name)
        self.assertEqual(['', '@counta counter', f'{indent1}{today_datestr} 平日しか空いてないのだるー'], a[2].to_lines())

    def test_parse_comment_with_brackets(self):
        scb = """[counter1]/普通にコメント [counter2]/コメント中に[ブラケット]あり [counter3]/[ブラケット] [counter4]/aaa[ブラケット] [counter5]/[ブラケット]aaa
[counter6]/[ブラケット]
@counta workspace
"""
        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)

        a = workspace._commenters
        f = self.assertEqual
        f(6, len(a))
        f(['counter1', '普通にコメント'], a[0])
        f(['counter2', 'コメント中に[ブラケット]あり'], a[1])
        f(['counter3', '[ブラケット]'], a[2])
        f(['counter4', 'aaa[ブラケット]'], a[3])
        f(['counter5', '[ブラケット]aaa'], a[4])
        f(['counter6', '[ブラケット]'], a[5])

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

    def test_to_lines_onepass(self):
        counter0 = """まだカウントが無い
@counta counter
"""
        counter1 = """カウントが1つある
@counta counter
 2022/12/24 sat 06:32:59
"""
        counter1_old = """カウントが1つある かなり古い
@counta counter
 2012/08/06 mon 06:01:10
"""
        counterN = """カウントが複数ある
@counta counter
 2022/12/23 sat 06:00:03
 2022/12/22 thu 21:13:11
 2022/11/09 wed 12:34:56
"""
        counter0_convertedname = """まだカウントが無い + ファイル名に変換が走る
@counta counter
"""
        scb = """[まだ存在しないカウンター]
[カウンター0] [カウンター1] [カウンターN]
[カウンター1 old] 
[カウント0 変換が走る(^_^)/ファイル名]
@counta workspace
"""

        self._data_source.set_pathbody('カウンター0') 
        self._data_source.write_lines(counta.string2lines(counter0))
        self._data_source.set_pathbody('カウンター1') 
        self._data_source.write_lines(counta.string2lines(counter1))
        self._data_source.set_pathbody('カウンター1 old')
        self._data_source.write_lines(counta.string2lines(counter1_old))
        self._data_source.set_pathbody('カウンターN') 
        self._data_source.write_lines(counta.string2lines(counterN))
        self._data_source.set_pathbody('カウント0 変換が走る(^_^)/ファイル名')
        self._data_source.write_lines(counta.string2lines(counter0_convertedname))

        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)
        lines = workspace.to_lines()

        self.assertEqual('@counta workspace', lines[1])

        count_line = lines[0]
        displayed_counternames = count_line.split(' ')
        self.assertEqual(6, len(displayed_counternames))
        # 新しいカウントはその順で並ぶ
        self.assertEqual('[カウンター1]', displayed_counternames[0])
        self.assertEqual('[カウンターN]', displayed_counternames[1])
        # 新規作成時にカウントされる分は fixed today で見分けがつかないのでテストしない
        pass
        # 古くしたカウントは最後になるはず
        self.assertEqual('[カウンター1_old]', displayed_counternames[-1])

    def test_to_lines_after_count(self):
        counter0 = """@counta counter
"""
        counter1 = """@counta counter
 2022/12/24 sat 06:32:59
"""
        counter2 = """@counta counter
 2012/08/06 mon 06:01:10
"""
        scb = """[counter0] [counter1] [counter2]
@counta workspace
"""

        self._data_source.set_pathbody('counter0') 
        self._data_source.write_lines(counta.string2lines(counter0))
        self._data_source.set_pathbody('counter1') 
        self._data_source.write_lines(counta.string2lines(counter1))
        self._data_source.set_pathbody('counter2') 
        self._data_source.write_lines(counta.string2lines(counter2))

        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)

        # 元データのままだと 1, 0, 2 の順になる
        # add_count() により 0, 1, 2 になるはず
        datetime.datetime = datetime_FixedToday_2023
        for counter in workspace.counters:
            n = counter.name
            if n=='counter0':
                datetime.datetime = datetime_FixedToday_2025
                counter.add_count()
                continue
            if n=='counter1':
                datetime.datetime = datetime_FixedToday_2024
                counter.add_count()
                datetime.datetime = datetime_FixedToday_2023
                counter.add_count()
                continue

        lines = workspace.to_lines()

        self.assertEqual('@counta workspace', lines[1])

        count_line = lines[0]
        displayed_counternames = count_line.split(' ')
        self.assertEqual(3, len(displayed_counternames))
        self.assertEqual('[counter0]', displayed_counternames[0])
        self.assertEqual('[counter1]', displayed_counternames[1])
        self.assertEqual('[counter2]', displayed_counternames[2])

    def test_add_comment_from_me(self):
        counter_contents = """@counta counter
 2022/12/25 17:34:25
"""
        scb = """[counter1]
[counter2  ] [  counter3] [cou  nter4]
[counter5]/ [counter6]/comment1 [cou  nter7]/comment2 [cou  nter8]/
@counta workspace
"""

        self._data_source.set_pathbody('counter2') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter3') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter4') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter5') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter6') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter7') 
        self._data_source.write_lines(counta.string2lines(counter_contents))
        self._data_source.set_pathbody('counter8') 
        self._data_source.write_lines(counta.string2lines(counter_contents))

        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)

        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)

        c1, c2, c3, c4, c5, c6, c7, c8 = workspace.counters
        self.assertEqual(1, len(c1.count_elements_by_lines))
        indent1 = ' '
        todaystr = counta.today_datetimestr()
        added_line = f'{indent1}{todaystr}'
        self.assertEqual(f'{added_line}', c2.count_elements_by_lines[0])
        self.assertEqual(f'{added_line}', c3.count_elements_by_lines[0])
        self.assertEqual(f'{added_line}', c4.count_elements_by_lines[0])
        self.assertEqual(f'{added_line}', c5.count_elements_by_lines[0])
        self.assertEqual(f'{added_line} comment1', c6.count_elements_by_lines[0])
        self.assertEqual(f'{added_line} comment2', c7.count_elements_by_lines[0])
        self.assertEqual(f'{added_line}', c8.count_elements_by_lines[0])

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
        self.assertEqual('with comment', ce0.comment)
        ce2 = counter.count_elements_by_object[2]
        self.assertEqual(f'{counta.today_datetimestr()}', ce2.datetime)
        self.assertEqual('', ce2.comment)

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
 {todaystr} コメント
 {todaystr}
 2022/12/22 thu 19:04:12 count1
 2022/12/22 thu 19:14:12 count2

ディレクティブはどこに書いてもいいよ
 hello
 `print('hello')`
"""
        actual = counta.lines2string(counter.to_lines())
        self.assertEqual(expect, actual)

    def test_tolines_from_empty_to_added(self):
        empty = ''
        counter = self.generate_counter(empty, 'coutername')

        counter.add_count()

        # わかりづらいけど、commenter2counter の default_counterfile_is_empty のところで最初に空行を一つ入れている
        actual = counter.to_lines()
        self.assertEqual(3, len(actual))
        indent1 = ' '
        todaystr = counta.today_datetimestr()
        self.assertEqual(empty, actual[0])
        self.assertEqual('@counta counter', actual[1])
        self.assertEqual(f'{indent1}{todaystr}', actual[2])

    def test_tolines_from_empty_only(self):
        empty = ''
        counter = self.generate_counter(empty, 'coutername')

        actual = counter.to_lines()
        self.assertEqual(2, len(actual))
        self.assertEqual(empty, actual[0])
        self.assertEqual('@counta counter', actual[1])

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

        counter = self.generate_counter("""カウンター
@counta counter
 2022/12/20 tue 19:04:12 い
 2022/12/21 wed 19:04:12 あ
 2022/12/19 mon 19:04:12 う

ソートしてるのでcount elementの順番がばらばらでも問題ない

""", 'coutername')

        e = '2022/12/21 wed 19:04:12'
        a = counter.get_latest_datetime()
        self.assertEqual(e, a)
        e = '2022/12/19 mon 19:04:12'
        a = counter.get_oldest_datetime()
        self.assertEqual(e, a)

        counter = self.generate_counter("""カウンター
@counta counter

count elementが無い場合でもエラーは出ない

""", 'coutername')

        e = ''
        a = counter.get_latest_datetime()
        self.assertEqual(e, a)
        a = counter.get_oldest_datetime()
        self.assertEqual(e, a)

class TestReport(unittest.TestCase):
    def setUp(self):
        self._data_source = DebugSource(path_prefix='', path_suffix='.scb')

    def tearDown(self):
        datetime.datetime = datetime_FixedToday

    def test(self):
        counter1 = """@counta counter
 2022/12/30 fri 08:30:02
 2022/12/29 thu 09:10:44
 2022/12/28 wed 11:11:11
 2022/11/24 thu 06:00:03
"""
        counter2 = """@counta counter
 2022/12/30 fri 06:00:01
"""
        counter3 = """@counta counter
 2022/12/28 wed 16:12:03
 2022/11/01 tue 22:16:33
 2012/08/06 mon 06:01:10
"""
        scb = """[カウンター1] [カウンター2] [カウンター3]
@counta workspace
"""

        self._data_source.set_pathbody('カウンター1')
        self._data_source.write_lines(counta.string2lines(counter1))
        self._data_source.set_pathbody('カウンター2')
        self._data_source.write_lines(counta.string2lines(counter2))
        self._data_source.set_pathbody('カウンター3')
        self._data_source.write_lines(counta.string2lines(counter3))

        lines = counta.string2lines(scb)
        root_hline = counta.HierarchicalLine.parse(lines)
        workspace = counta.Workspace(self._data_source)
        workspace.parse(root_hline)

        report = counta.Report(workspace)
        report.update()

        lines = report.daily_to_lines()
        print_lines(lines)
        lines = report.monthly_to_lines()
        print_lines(lines)

if __name__ == '__main__':
    unittest.main()
