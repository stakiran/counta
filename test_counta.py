# encoding: utf-8
import unittest

import counta

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

class EmptySource(counta.DataSource):
    def __init__(self, path_prefix='', path_suffix=''):
        super().__init__(path_prefix, path_suffix)

    @property
    def fullpath(self):
        fullpath = f'{self._path_prefix}{self._path_body}{self._path_suffix}'
        return fullpath

    def exists(self):
        return True

    def read_as_lines(self):
        return []

    def write_lines(self, lines):
        return

class TestWorkspace(unittest.TestCase):
    def setUp(self):
        self._data_source = EmptySource(path_prefix='', path_suffix='.scb')

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

if __name__ == '__main__':
    unittest.main()
