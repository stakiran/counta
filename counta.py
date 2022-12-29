# encoding: utf-8

import datetime
import os
import sys

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    default_directory = get_default_directory()
    parser.add_argument('-i', '--input-workspace-filename', required=True,
        help='Not path and directory, but filename.')
    parser.add_argument('-d', '--directory', default=default_directory,
        help='Base directory(Must be absolute path). if not given then use "(currentdir)/scb"')

    parser.add_argument('--dryrun',default=False, action='store_true')

    args = parser.parse_args()
    return args

def get_default_directory():
    cwd = os.getcwd()
    folder = 'scb'
    return os.path.join(cwd, folder)

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

LB = '\n'
def string2lines(s):
    return s.split(LB)
def lines2string(lines):
    return LB.join(lines)

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

def get_filename(path):
    return os.path.basename(path)

def get_basename(path):
    return os.path.splitext(get_filename(path))[0]

def get_corrected_filename(filename):
    invalid_chars ='\\/:*?"<>|'
    noisy_chars =' '
    target_chars = invalid_chars + noisy_chars

    after_char = '_'

    ret = filename
    for target_char in target_chars:
        ret = ret.replace(target_char, after_char)
    return ret

def remove_duplicates_from_list(ls):
    return list(dict.fromkeys(ls))

def get_indent_depth(line):
    # https://stackoverflow.com/questions/13648813/what-is-the-pythonic-way-to-count-the-leading-spaces-in-a-string
    return len(line) - len(line.lstrip(' '))

def remove_indent(line):
    return line.lstrip(' ')

def today_datetimestr():
    todaydt = datetime.datetime.today()
    dtstr = todaydt.strftime('%Y/%m/%d %a %H:%M:%S')
    return dtstr

DATETIMESTR_FORMAT = 'yyyy/mm/dd dow hh:mm:ss'
LENGTH_OF_DATETIMESTR_FORMAT = len(DATETIMESTR_FORMAT)
def is_valid_datetimestr(datetimestr):
    # yyyy/mm/dd dow hh:mm:ss

    try:
        datestr, dow, timestr = datetimestr.split(' ')
        y, month, d = [int(elm) for elm in datestr.split('/')]
        h, minute, s = [int(elm) for elm in timestr.split(':')]
        datetime.datetime(year=y, month=month, day=d, hour=h, minute=minute, second=s)
    except:
        return False

    if len(dow)!=3:
        return False

    if len(datetimestr)!=LENGTH_OF_DATETIMESTR_FORMAT:
        return False

    return True

class Stack:
    def __init__(self, ls=[]):
        self._contents = ls

    def pop(self):
        return self._contents.pop()

    def push(self, element):
        self._contents.append(element)

    def peek(self):
        bottompos = len(self._contents) - 1

        is_empty = bottompos==-1

        element = None
        if not is_empty:
            element = self._contents[bottompos]

        return element, is_empty

class LatestStack:
    def __init__(self):
        pass

class HierarchicalLine:
    def parse(lines):
        root_hline = HierarchicalLine('<root>', -1)
        hlines = []
        for line in lines:
            current_indent_depth = get_indent_depth(line)
            line_without_indent = remove_indent(line)
            hline = HierarchicalLine(line_without_indent, current_indent_depth)
            hlines.append(hline)

        stack = Stack()
        stack.push(root_hline)
        for i,current_hline in enumerate(hlines):
            current_depth = current_hline.indent_depth

            parent_hline, _ = stack.peek()
            parent_depth = parent_hline.indent_depth

            # 自分の所属は機械的に親に任せる
            # どの親であるべきかは判断しない（Stackに正しい親が入っているとみなす）

            if current_depth <= parent_depth:
                # n段下がるケースはn回親を遡ればよい
                # わかりづらいが、currentがprevと同じ深さのときは1段下がっている
                backtrack_count = parent_depth - current_depth + 1
                for _ in range(backtrack_count):
                    parent_hline = stack.pop()
                parent_hline, _ = stack.peek()
            parent_hline.append(current_hline)

            # 自分が親になるべきかどうかを判断する
            # そのためには次行を先読みする必要がある

            is_reached_to_end = i==len(hlines)-1
            if is_reached_to_end:
                continue
            next_hline = hlines[i+1]
            next_depth = next_hline.indent_depth

            if next_depth == current_depth+1:
                # 次が1段下がる
                # - 次は自分の子なので自分が親になる
                stack.push(current_hline)
            elif next_depth > current_depth+1:
                # 次がn段下がるケースは文法違反
                # - 不便なので矯正しちゃう（孫以下は自分の子にする）
                # - もちろん自分は親になる
                next_hline.indent_depth = current_depth+1
                stack.push(current_hline)

        return root_hline

    @staticmethod
    def to_lines(hline):
        lines = []

        is_root = hline.indent_depth==-1
        if is_root:
            pass
        else:
            indent = ' '*hline.indent_depth
            line = f'{indent}{hline.line}'
            lines.append(line)

        for child_hline in hline.children:
            child_lines = HierarchicalLine.to_lines(child_hline)
            lines.extend(child_lines)
        
        return lines

    @staticmethod
    def to_string(hline):
        lines = HierarchicalLine.to_lines(hline)
        s = lines2string(lines)
        return s

    @staticmethod
    def flat(hline):
        hlines = []

        hlines.append(hline)
        for child_hline in hline.children:
            child_hlines = HierarchicalLine.flat(child_hline)
            hlines.extend(child_hlines)

        return hlines

    def __init__(self, line, indent_depth):
        self._line = line
        self._indent_depth = indent_depth
        self._childlen = []

    def append(self, hline):
        if not isinstance(hline, HierarchicalLine):
            raise RuntimeError(f'{self} append() must be given an my instance.')
        self._childlen.append(hline)

    def prepend(self, hline):
        if not isinstance(hline, HierarchicalLine):
            raise RuntimeError(f'{self} prepend() must be given an my instance.')
        self._childlen.insert(0, hline)

    @property
    def line(self):
        return self._line

    @property
    def children(self):
        return self._childlen

    @property
    def flatten_children(self):
        return self._childlen

    @property
    def indent_depth(self):
        return self._indent_depth

    @indent_depth.setter
    def indent_depth(self, indent_depth):
        self._indent_depth = indent_depth

SPACE = ' '
COUNT_MARK = f'{SPACE}{SPACE}'

COUNTA_MARK = '@counta'
DIRECTIVE_WORKSPACE = ['workspace', 'w']
DIRECTIVE_DAILY_REPORT = ['reportdaily', 'rd']
DIRECTIVE_COUNTER = ['counter', 'c']
DIRECTIVE_TAG = ['tag', 't']

def get_directive_hline(root_hline, directive_consts):
    for toplevel_hline in root_hline.children:
        line = toplevel_hline.line
        line_by_list = line.split(' ')
        if len(line_by_list) < 2:
            continue
        if line_by_list[0] != COUNTA_MARK:
            continue
        if line_by_list[1] in directive_consts:
            return True, toplevel_hline
        continue
    return False, None

class DataSource:
    def __init__(self, path_prefix='', path_suffix=''):
        self._path_prefix = path_prefix
        self._path_suffix = path_suffix

        self._path_body = ''

    def set_pathbody(self, path_body):
        self._path_body = path_body

    @property
    def path_prefix(self):
        return self._path_prefix

    @property
    def path_suffix(self):
        return self._path_suffix

    @property
    def path_body(self):
        return self._path_body

    @property
    def fullpath(self):
        # 結合方法がデータソース次第かもしれないので i/f にしておく
        raise NotImplementedError()

    def exists(self):
        raise NotImplementedError()

    def read_as_lines(self):
        raise NotImplementedError()

    def write_lines(self, lines):
        raise NotImplementedError()

class FileSource(DataSource):
    def __init__(self, path_prefix='', path_suffix=''):
        super().__init__(path_prefix, path_suffix)

    @property
    def fullpath(self):
        fullpath = ''
        fullpath = os.path.join(self._path_prefix, self._path_body)
        # もっぱら拡張子を想定
        # os.path.join だと delimitor ついちゃうので使わない。
        fullpath = f'{fullpath}{self._path_suffix}'
        return fullpath

    def exists(self):
        return os.path.exists(self.fullpath)

    def read_as_lines(self):
        lines = file2list(self.fullpath)
        return lines

    def write_lines(self, lines):
        list2file(self.fullpath, lines)

NO_COMMENT_BODY = '<no comment body>'
class Workspace:
    def __init__(self, data_source):
        self._data_source = data_source
        self._root_hline = None
        self._counters = []

        # for debug
        self._commenters = []

    @property
    def counters(self):
        return self._counters

    def parse(self, root_hline):
        is_found, _ = get_directive_hline(root_hline, DIRECTIVE_WORKSPACE)
        if not is_found:
            raise RuntimeError('parse error: No workspace directive.')

        self._root_hline = root_hline

        # 単に [countername] の表記を集めればいい
        #  走査しやすさのため flat する（その際、rootは邪魔なので退ける）
        #  パースの都合上、comment の有無もここで調べる（count はもうちょっと後）
        # 便宜上、[countername, comment] のことを commenter と呼ぶことにする
        hlines = HierarchicalLine.flat(root_hline)
        hlines = hlines[1:] 
        all_commenters = []
        for hline in hlines:
            commenters = Workspace.line2pairs_of_countername_and_comment(hline.line)
            all_commenters.extend(commenters)
        self._commenters = all_commenters

        for commenter in all_commenters:
            counter = Workspace.commenter2counter(commenter, self._data_source)
            self._counters.append(counter)

    def to_lines(self):
        directive_lines = f'{COUNTA_MARK} {DIRECTIVE_WORKSPACE[0]}'

        counters = self._counters

        # とりあえず今は date modified 固定
        # ややこしいが、
        #  sortedはasc(昇順)なので、最近順にしたければその逆を取る
        #  まだカウントがないカウンターは新規に等しいので modified されたとみなす
        # sortkeyにcounter.nameを含めている理由
        #  新規されるカウンターがn個ある場合に順序が不定になるため
        counters = sorted(counters, key=lambda counter: f'{counter.get_latest_datetime()}{counter.name}')
        counters.reverse()

        counter_line = ''
        for counter in counters:
            margin = ' '
            is_first_loop = counter_line==''
            if is_first_loop:
                margin = ''
            countername_display_text = f'[{counter.name}]'
            counter_line = f'{counter_line}{margin}{countername_display_text}'

        blankline = ''
        lines = [
            counter_line,
            directive_lines,
            blankline,
        ]
        return lines

    @staticmethod
    def commenter2counter(commenter, data_source):
        countername, comment = commenter

        is_count_added = False
        is_count_added_from_mark = countername.find(COUNT_MARK)!=-1
        if is_count_added_from_mark:
            countername = countername.replace(COUNT_MARK, '')
        is_count_added_from_comment = len(comment)>0
        is_count_added = is_count_added_from_mark or is_count_added_from_comment

        # 入れておいたダミーだったらもちろん消す
        if comment==NO_COMMENT_BODY:
            comment = ''

        corrected_countername = get_corrected_filename(countername)
        data_source.set_pathbody(corrected_countername)
        if not data_source.exists():
            default_counterfile_is_empty = ['']
            data_source.write_lines(default_counterfile_is_empty)

        lines = data_source.read_as_lines()
        root_hline = HierarchicalLine.parse(lines)
        counter = Counter.parse(root_hline)
        counter.name = corrected_countername

        if is_count_added:
            counter.add_count(comment)

        is_no_count = len(counter.count_elements_by_lines)==0
        if is_no_count:
            counter.add_count()

        return counter

    @staticmethod
    def line2pairs_of_countername_and_comment(line):
        MODE_IN_BRACHET = 0
        MODE_OUT_BRACHET = 1
        MODE_IN_COMMENT = 2
        mode = MODE_OUT_BRACHET
        is_fresh_off_out = False

        pairs_of_countername_and_comment = []
        start_of_name = -1
        start_of_comment = -1

        counter_name = ''
        comment = ''
        for i in range(len(line)):
            c = line[i]
    
            if is_fresh_off_out:
                is_fresh_off_out = False
                if c=='/':
                    mode = MODE_IN_COMMENT
                    start_of_comment = i+1
                    continue
            if mode == MODE_IN_COMMENT:
                is_last_of_comment = c in [' ']
                is_end = i == len(line)-1
                if not is_last_of_comment and not is_end:
                    continue
                if is_last_of_comment:
                    comment = line[start_of_comment:i]
                if is_end:
                    comment = line[start_of_comment:i+1]
                mode = MODE_OUT_BRACHET
                INDEX_OF_COMMENT = 1
                # `/` のみ指定された場合、仕様上コメントとして検出できないのでダミーを入れておく。
                if len(comment)==0:
                    comment = NO_COMMENT_BODY
                pairs_of_countername_and_comment[-1][INDEX_OF_COMMENT] = comment
                continue

            if mode == MODE_OUT_BRACHET and c=='[':
                mode = MODE_IN_BRACHET
                start_of_name = i+1
                continue

            if mode == MODE_OUT_BRACHET and c==']':
                continue

            if mode == MODE_IN_BRACHET and c=='[':
                continue

            if mode == MODE_IN_BRACHET and c==']':
                counter_name = line[start_of_name:i]
                COMMENT_IS_UNDEFINED_NOW = ''
                pair = [counter_name, COMMENT_IS_UNDEFINED_NOW]
                pairs_of_countername_and_comment.append(pair)
                mode = MODE_OUT_BRACHET
                is_fresh_off_out = True
                continue

        return pairs_of_countername_and_comment

def line2tags(line):
    countamark, directive, tags_by_str = line.split(' ', 2)
    tags = tags_by_str.split(' ')
    return tags

class Counter:
    @staticmethod
    def parse(root_hline):
        is_found, _ = get_directive_hline(root_hline, DIRECTIVE_COUNTER)
        if not is_found:
            directive_line = f'{COUNTA_MARK} {DIRECTIVE_COUNTER[0]}'
            directive_hline = HierarchicalLine(directive_line, indent_depth=0)
            root_hline.append(directive_hline)
        return Counter(root_hline)

    def __init__(self, root_hline_with_directive):
        self._root_hline = root_hline_with_directive
        self._name = ''

        self._directive_hline = None
        self._tags = []

        self._parse_hline()

    def _parse_hline(self):
        root_hline = self._root_hline

        is_found, directive_hline = get_directive_hline(root_hline, DIRECTIVE_COUNTER)
        assert(is_found)
        self._directive_hline = directive_hline

        is_found, tag_hline = get_directive_hline(root_hline, DIRECTIVE_TAG)
        if is_found:
            self._tags = line2tags(tag_hline.line)

    def add_count(self, comment=''):
        count_element = CountElement(comment)
        hline = HierarchicalLine(line=count_element.to_string(), indent_depth=1)
        # 古いカウントが上にあっても仕方ないので、最新が上に来るようにする
        #self._directive_hline.append(hline)
        self._directive_hline.prepend(hline)

    def to_lines(self):
        return HierarchicalLine.to_lines(self._root_hline)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, countername):
        self._name = countername

    @property
    def count_elements_by_lines(self):
        lines = HierarchicalLine.to_lines(self._directive_hline)
        START_OF_COUNTELEMENT = 1
        lines = lines[START_OF_COUNTELEMENT:]
        return lines

    @property
    def count_elements_by_object(self):
        lines = self.count_elements_by_lines
        countelements = []
        for line in lines:
            countelement = CountElement.parse(line)
            countelements.append(countelement)
        return countelements

    @property
    def count(self):
        return len(self.count_elements_by_object)

    def _countelements_sorted_by_datetime(self):
        count_elements = self.count_elements_by_object
        sorted_count_elements = sorted(count_elements, key=lambda elm:elm.datetime)
        return sorted_count_elements

    def get_oldest_datetime(self):
        sorted_count_elements = self._countelements_sorted_by_datetime()
        if len(sorted_count_elements)==0:
            return ''
        return sorted_count_elements[0].datetime

    def get_latest_datetime(self):
        sorted_count_elements = self._countelements_sorted_by_datetime()
        if len(sorted_count_elements)==0:
            return ''
        sorted_count_elements.reverse()
        return sorted_count_elements[0].datetime

class CountElement:
    def __init__(self, comment='',  datetime=''):
        self._comment = comment

        self._datetime = datetime
        if not datetime:
            self._datetime = today_datetimestr()

    def to_string(self):
        is_no_comment = self._comment==''
        if is_no_comment:
            return f'{self._datetime}'
        return f'{self._datetime} {self._comment}'

    @property
    def comment(self):
        return self._comment

    @property
    def datetime(self):
        return self._datetime

    @staticmethod
    def parse(line):
        line_without_indent = line.lstrip(' ')

        l = len(line_without_indent)
        elm_l = len(line_without_indent.split(' '))
        DATETIME_ELEMENT_COUNT = 3
        if l<LENGTH_OF_DATETIMESTR_FORMAT:
            raise RuntimeError('parse failed. No datetime field.')
        if elm_l<DATETIME_ELEMENT_COUNT:
            raise RuntimeError('parse failed. Maybe invalid format as a datetime.')

        is_no_comment = elm_l==DATETIME_ELEMENT_COUNT
        if is_no_comment:
            comment = ''
            datetime = line_without_indent
        else:
            datestr, dow, timestr, comment = line_without_indent.split(' ', DATETIME_ELEMENT_COUNT)
            datetime = f'{datestr} {dow} {timestr}'

        if not is_valid_datetimestr(datetime):
            raise RuntimeError(f'parse failed. invalid date field. Must be "yyyy/mm/dd dow hh:mm:ss", but actual "{line_without_indent}"')

        return CountElement(comment=comment, datetime=datetime)

class ConditionalCounter(Counter):
    def __init__(self):
        super().__init__()

    def is_match(self):
        raise NotImplementedError()

class RoutineCounter(ConditionalCounter):
    def __init__(self):
        super().__init__()
        self._routine_specifier = ''
        self._latest_stack = LatestStack()

    def is_match(self):
        return False

class EventCounter(ConditionalCounter):
    def __init__(self):
        super().__init__()
        self._target_day = ''

    def is_match(self):
        return False

class Report:
    def __init__(self, data_source, workspace):
        self._data_source = data_source
        self._workspace = workspace

        self._daily_counters_per_day = {}

    def daily_to_lines(self):
        lines = []
        indent1 = ' '

        daykeys = self._daily_counters_per_day.keys()
        daykeys.sort()
        for k in daykeys:
            counternames = self._daily_counters_per_day[k]
            datestr_with_dow = k

            lines.append(f'{datestr_with_dow}')

            count = len(counternames)
            graph = '*'*count
            lines.append(f'{indent1}{count} {graph}')

            line = ''
            for countername in counternames:
                line = f'{line}[{countername}] '
            line = f'{indent1}{line}'
            lines.append(line)
        return lines

    def update(self):
        self._update_daily()
    
    def _update_daily(self):
        # {
        #   "2022/12/29": ["counter1", "counter2"],
        #  ...
        # }
        d = {}

        counters = self._workspace.counters
        for counter in counters:
            count_elements = counter.count_elements_by_object
            for count_element in count_elements:
                datetimestr = count_element.datetime
                datestr, dow, timestr = datetimestr.split(' ')
                k = f'{datestr} {dow}'
                not_found_yet = not k in d
                if not_found_yet:
                    d[k] = []
                d[k].append(counter.name)

        self._daily_counters_per_day = d

def debugprint_lines(file_source, savee_list):
    for savee in savee_list:
        pathbody, lines = savee
        file_source.set_pathbody(pathbody)

        print(f'=== [{pathbody}] ===')
        print(f'abs:"{file_source.fullpath}"')
        print('---')
        for line in lines:
            print(line)

def save_lines_to_file(file_source, savee_list):
    for savee in savee_list:
        pathbody, lines = savee
        file_source.set_pathbody(pathbody)
        file_source.write_lines(lines)

def main(args):
    target_workspace_filename = args.input_workspace_filename
    base_directory = args.directory

    target_workspace_fullpath = os.path.join(base_directory, target_workspace_filename)
    if not os.path.exists(target_workspace_fullpath):
        raise RuntimeError(f'Not Found "{target_workspace_fullpath}".')
    lines = file2list(target_workspace_fullpath)

    file_source = FileSource(path_prefix=base_directory, path_suffix='.scb')
    root_hline = HierarchicalLine.parse(lines=lines)
    workspace = Workspace(data_source=file_source)

    workspace.parse(root_hline=root_hline)

    savee_list = [] # (pathbody, lines)
    for counter in workspace.counters:
        pathbody = counter.name
        lines = counter.to_lines()
        savee = [pathbody, lines]
        savee_list.append(savee)
    # 拡張子は file_source が suffix としてつけちゃうのでここでは外しとく
    workspace_basename = get_basename(args.input_workspace_filename)
    workspace_savee = [workspace_basename, workspace.to_lines()]
    savee_list.append(workspace_savee)

    if args.dryrun:
        debugprint_lines(file_source, savee_list)
        sys.exit(0)

    save_lines_to_file(file_source, savee_list)
    sys.exit(0)

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
