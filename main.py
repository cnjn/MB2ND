import os
import utils
import threading
import rich.console
from prompt_toolkit import prompt
from prompt_toolkit.document import Document
from prompt_toolkit.history import FileHistory
from prompt_toolkit.validation import Validator
from prompt_toolkit.completion import WordCompleter

commands = ['ls', 'cd', 'mkdir', 'download', 'upload', 'rm', 'quit']
currentDir = ''
console = rich.console.Console()
client = utils.Client('imap.exmail.qq.com')


class myThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.recv = recv

    def run(self):
        print("开始线程：" + self.name)
        print("退出线程：" + self.name)


class UpdateWord(Validator):
    def __init__(self, completer: WordCompleter):
        super().__init__()
        self.completer = completer

    def validate(self, document: Document) -> None:
        # 更新自动补全的字典
        text = document.text.split()
        if not text:  # text为空跳过
            return
        if text[0] == 'download':
            if len(text) == 1:
                self.completer.words = ['test1', 'test2']
            else:
                self.completer.words = ['test3', 'test4']
        elif text[0] == 'cd':
            if len(text) == 1:
                self.completer.words = [x[:-1] for x in client.ls(currentDir, False)]
        else:
            self.completer.words = commands


while 1:
    completer = WordCompleter(commands)
    user_input = prompt('mailDisk %s > ' % currentDir,
                        history=FileHistory('history.txt'),
                        completer=completer,
                        validator=UpdateWord(completer),
                        complete_while_typing=False)
    comm = user_input.split()[0]
    if comm == 'ls':
        files = client.ls(currentDir)
        console.print(files if files else '')
    elif comm == 'quit':
        exit()
    elif comm == 'cd':
        try:
            folder = user_input.split()[1]
        except IndexError:
            currentDir = ''
            continue
        if folder == '..':
            currentDir = currentDir[:currentDir.rfind('/')]
        elif folder not in completer.words:
            print('Directory not exist!')
        else:
            currentDir += '/'+folder
    elif comm == 'upload':
        pass


# 登陆
# a = client.servers[0].create('/ok/ip2')
# pass

# M = recv
# M.select("files")
# # a = M.fetch('12', 'BODY[TEXT]')
#
# a = myThread('1', '9', '9', M)
# b = myThread('2', '11', '11', M)
# # a.start()
# b.start()
# # a.join()
# b.join()
#
# typ, data = M.search(None, 'ALL')
# # for num in data[0].split():
# #     typ, data = M.fetch(num, '(RFC822)')
# #     print('Message %s\n%s\n' % (num, data[0][1].decode()))
# M.close()
# M.logout()
