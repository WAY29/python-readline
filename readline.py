from itertools import chain
from sys import exc_info, stdout
from traceback import print_exception
from typing import List, Tuple, Union

from colorama import Back, Fore, init

TUPLE_OR_LIST = Union[List, Tuple]
init(autoreset=True)


class Colored(object):
    #  前景色:红色  背景色:默认
    def red(self, s):
        return Fore.RED + s + Fore.RESET

    #  前景色:绿色  背景色:默认
    def green(self, s):
        return Fore.GREEN + s + Fore.RESET

    #  前景色:黄色  背景色:默认
    def yellow(self, s):
        return Fore.YELLOW + s + Fore.RESET

    #  前景色:蓝色  背景色:默认
    def blue(self, s):
        return Fore.BLUE + s + Fore.RESET

    #  前景色:洋红色  背景色:默认
    def magenta(self, s):
        return Fore.MAGENTA + s + Fore.RESET

    #  前景色:青色  背景色:默认
    def cyan(self, s):
        return Fore.CYAN + s + Fore.RESET

    #  前景色:白色  背景色:默认
    def white(self, s):
        return Fore.WHITE + s + Fore.RESET

    #  前景色:黑色  背景色:默认
    def black(self, s):
        return Fore.BLACK

    #  前景色:白色  背景色:绿色
    def white_green(self, s):
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET


color = Colored()


def get_min_string(wordlist):
    return "".join(chain.from_iterable(filter(lambda a: len(a) == 1, [set([chr(y[x]) for y in wordlist]) for x in range(len(min(wordlist, key=len)))])))


try:
    # POSIX system: Create and return a getch that manipulates the tty
    import termios
    import sys
    import tty

    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    #  Read arrow keys correctly
    def getchar():
        firstChar = getch()
        if firstChar == '\x1b':
            secChar = getch()
            if (secChar == "["):
                ThrChar = getch()
                if (ThrChar.isdigit()):
                    return {"2~": "Ins", "3~": "Del", "5~": "PgUp", "6~": "PgDn"}[ThrChar + getch()]
                else:
                    return {"A": "up", "B": "down", "C": "right", "D": "left", "H": "Home", "F": "End"}[ThrChar]
        else:
            return firstChar.encode()

except ImportError:
    # Non-POSIX: Return msvcrt's (Windows') getch
    from msvcrt import getch

    # Read arrow keys correctly
    def getchar():
        firstChar = getch()
        if firstChar == b'\xe0':
            return {b"H": "up", b"P": "down", b"M": "right", b"K": "left", b"G": "Home", b"O": "End", b"R": "Ins", b"S": "Del", b"I": "PgUp", b"Q": "PgDn"}[getch()]
        else:
            return firstChar


class LovelyReadline:
    def __init__(self):
        self.STDIN_STREAM = b''
        self.CONTINUE_POINTER = None
        self.HISTORY = []
        self.HISTORY_POINTER = 0
        self.FROM_HISTORY = False
        self._wordlist = {}
        self._prefix_wordlist = {}
        self._exit_command = "quit"

    def init(self, wordlist: dict, prefix_wordlist: dict, exit_command: str = "quit"):
        self._wordlist = wordlist
        self._prefix_wordlist = prefix_wordlist
        self._exit_command = exit_command

    def get_wordlist(self) -> dict:
        return self._wordlist

    def get_prefix_wordlist(self) -> dict:
        return self._prefix_wordlist

    def get_history(self) -> list:
        return self.HISTORY

    def clean_history(self) -> bool:
        self.HISTORY = []
        return True

    def add_prefix_wordlist(self, key: str, value: TUPLE_OR_LIST) -> bool:
        if (isinstance(value, (list, tuple))):
            self._prefix_wordlist[key] = value
            return True
        else:
            return False

    def add_wordlist(self, key: str, value: TUPLE_OR_LIST) -> bool:
        if (isinstance(value, (list, tuple))):
            self._wordlist[key] = value
            return True
        else:
            return False

    def __call__(self, other_delimiter: bytes = b"",) -> str:
        cmd = ''
        wordlist = self._wordlist
        wordlist["prefix_wordlist"] = []
        end = False
        completion = False
        if (self.CONTINUE_POINTER is not None):
            pointer = self.CONTINUE_POINTER
        else:
            pointer = 0
        history_line = b''
        remaining = ""
        old_stream_len = 0
        old_pointer = 0
        try:
            while 1:
                if (self.CONTINUE_POINTER is not None):
                    ch, dch = b'', ''
                    self.CONTINUE_POINTER = None
                else:
                    old_stream_len = len(self.STDIN_STREAM)
                    old_pointer = pointer
                    try:
                        ch = getchar()
                    except Exception:
                        print(f"\nGetline error\n")
                        cmd = ''
                        break
                if (isinstance(ch, bytes)):
                    try:
                        dch = ch.decode()
                    except UnicodeDecodeError:
                        continue
                if (ch == "Del"):
                    ch = b"\b"
                    dch = "\b"
                if (isinstance(ch, str)):
                    read_history = False
                    if (ch == "up"):  # up
                        if (self.HISTORY_POINTER >= 0):
                            self.HISTORY_POINTER -= 1
                            read_history = True
                    elif (ch == "down"):  # down
                        if (self.HISTORY_POINTER <= len(self.HISTORY) - 1):
                            self.HISTORY_POINTER += 1
                            read_history = True
                    elif (ch == "left" and pointer > 0):  # left
                        pointer -= 1
                    elif (ch == "right"):  # right
                        if (pointer < len(self.STDIN_STREAM)):
                            pointer += 1
                        elif (history_line):
                            completion = True
                    elif (ch == "Home"):  # Home
                        pointer = 0
                    elif (ch == "End"):  # End
                        pointer = len(self.STDIN_STREAM)
                    if ((ch == "up" or ch == "down")):
                        history_len = len(self.HISTORY)
                        if (read_history):
                            if (self.HISTORY_POINTER > -1 and self.HISTORY_POINTER < history_len):
                                self.STDIN_STREAM = self.HISTORY[self.HISTORY_POINTER]
                                pointer = len(self.STDIN_STREAM)
                                self.FROM_HISTORY = True
                            elif (self.HISTORY_POINTER == -1):
                                self.STDIN_STREAM = b''
                                pointer = 0
                            elif (self.HISTORY_POINTER == history_len):
                                self.STDIN_STREAM = b''
                                pointer = 0
                elif (dch and 32 <= ord(dch) <= 127):
                    if (pointer == len(self.STDIN_STREAM)):
                        self.STDIN_STREAM += ch
                    else:
                        self.STDIN_STREAM = self.STDIN_STREAM[:pointer] + \
                            ch + self.STDIN_STREAM[pointer:]
                    if (self.FROM_HISTORY):
                        self.FROM_HISTORY = False
                    pointer += 1
                elif(ch == b'\r' or ch == b'\n'):  # enter
                    end = True
                elif(ch == b'\b' and pointer > 0):  # \b
                    if (pointer == len(self.STDIN_STREAM)):
                        self.STDIN_STREAM = self.STDIN_STREAM[:-1]
                    else:
                        self.STDIN_STREAM = self.STDIN_STREAM[:pointer-1] + \
                            self.STDIN_STREAM[pointer:]
                    pointer -= 1
                elif(ch == b'\t'):  # \t
                    completion = True
                elif(dch and ord(dch) == 4):  # ctrl+d
                    print(color.cyan(self._exit_command + "\n"), end="")
                    cmd = 'quit'
                    break
                elif(dch and ord(dch) == 3):  # ctrl+c
                    print(color.cyan('^C'))
                    stdout.flush()
                    break
                if (completion):
                    completion = False
                    if (history_line and isinstance(history_line, bytes)):
                        self.STDIN_STREAM = history_line
                        pointer = len(history_line)
                    elif (isinstance(history_line, list)):
                        cmd = ''
                        self.CONTINUE_POINTER = pointer
                        word = self.STDIN_STREAM.split(b" ")[-1]
                        if (other_delimiter):
                            word = word.split(other_delimiter)[-1]
                        print("\n" + b"  ".join(word +
                                                last_word for last_word in history_line).decode())
                        break
                stream_len = len(self.STDIN_STREAM)
                history_len = len(self.HISTORY)
                remaining_len = len(remaining)
                clean_len = old_stream_len + remaining_len
                print("\b" * old_pointer + " " * clean_len +
                      "\b" * clean_len, end="")  # 清空原本输入
                print(color.cyan(self.STDIN_STREAM.decode()), end="")  # 输出
                if (remaining):
                    remaining = ""
                if (end):  # 结束输入
                    stdout.write('\n')
                    stdout.flush()
                    cmd = self.STDIN_STREAM.decode()
                    # 加入历史命令
                    if (cmd and not self.FROM_HISTORY and (not history_len or (history_len and self.HISTORY[-1] != cmd.encode()))):
                        self.HISTORY.append(cmd.encode())
                    self.HISTORY_POINTER = len(self.HISTORY)
                    break
                if (history_line):
                    history_line = b''
                if (not self.STDIN_STREAM):
                    continue
                temp_history_lines = [line[stream_len:] for line in reversed(self.HISTORY) if (
                    line.startswith(self.STDIN_STREAM) and self.STDIN_STREAM != line)]
                # 若有历史命令，输出剩余的部分
                if (temp_history_lines and temp_history_lines[0]):
                    remaining = min(temp_history_lines, key=len)
                stream_list = self.STDIN_STREAM.split(b" ")
                command = self.STDIN_STREAM.strip().decode()
                if (command in self._prefix_wordlist):
                    prefix_wordlist = self._prefix_wordlist.get(command, [])
                    if (wordlist["prefix_wordlist"] != prefix_wordlist):
                        wordlist["prefix_wordlist"] = prefix_wordlist
                # 若有补全单词，输出剩余的部分
                word = stream_list[-1]
                if (other_delimiter):
                    word = word.split(other_delimiter)[-1]
                if (word):
                    word_len = len(word)
                    temp_word_lines = [line[word_len:].encode() for line in chain.from_iterable(
                        wordlist.values()) if (line.startswith(word.decode()) and word != line)]
                    if (temp_word_lines and temp_word_lines[0]):
                        temp_remaining = min(temp_word_lines, key=len)
                        temp_history_line = self.STDIN_STREAM + temp_remaining
                        if (not history_line or len(temp_history_line) < len(history_line)):
                            remaining = temp_remaining
                else:
                    temp_word_lines = []
                if (remaining):
                    total_lines = temp_history_lines + temp_word_lines
                    less_bytes = get_min_string(total_lines).encode()
                    stdout.write(remaining.decode() + "\b" *
                                 len(remaining))  # 输出补全提示
                    if (less_bytes):  # 允许补全公共子串
                        history_line = self.STDIN_STREAM + less_bytes
                    elif (len(temp_word_lines) > 1):  # 多个候选词,保留输入流并返回
                        cmd = ''
                        history_line = temp_word_lines
                    else:
                        history_line = self.STDIN_STREAM + remaining
                stdout.write("\b" * (stream_len - pointer))
                stdout.flush()
        except Exception:
            print(color.red('Error'))
            if 1:
                exc_type, exc_value, exc_tb = exc_info()
                print_exception(exc_type, exc_value, exc_tb)
            cmd = ''
        if (self.CONTINUE_POINTER is None):
            self.STDIN_STREAM = b''
        return cmd


if (__name__ == "__main__"):
    test_wordlist = {"command_wordlist": ["apt", "make"]}
    test_prefix_wordlist = {"apt": ["install"],
                            "make": ["build"],
                            "apt install": ["foo.txt"],
                            "make build": ["bar.txt"]}
    readline = LovelyReadline()
    readline.init(test_wordlist, test_prefix_wordlist)

    while True:
        print(":>", end="")
        cmd = readline()
        if (cmd == ""):
            continue
        else:
            print("cmd:", cmd)
