import imaplib
import json
import re


class Client:
    def __init__(self, imap_server):
        self.dirs = {'': dict()}
        self.origin = {'': ''}
        with open('config.json') as f:
            self.config = json.loads(f.read())
        self.servers = [imaplib.IMAP4_SSL(imap_server) for _ in range(self.config['serverConut'])]
        for each in self.servers:
            _, login_msg = each.login(self.config['user'], self.config['passwd'])
            print("server%d: %s" % (self.servers.index(each) + 1, ''.join([x.decode() for x in login_msg])))

    def updateDirectory(self):
        directory = [x.decode() for x in self.servers[0].list()[1][6:]]
        directory = [x[x.find('/') + 4:-1] for x in directory]
        for i in directory:
            folder = self.dirs['']
            for j in i.split('/'):
                if j[0] == '&':
                    break  # 跳过用户自己在网页上建立的文件夹
                if folder.get(j) is None:
                    folder[j] = dict()
                    self.origin[j] = i
                folder = folder[j]

    def ls(self, directory: str, list_file=True):
        self.updateDirectory()
        folder = self.dirs['']
        for i in directory.split('/'):
            if not i:
                continue  # folder被初始化为根目录，此处跳过
            try:
                folder = folder[i]
            except KeyError:
                # Directory not exist!
                return {}
        ret = {x + '/' for x in folder.keys()}  # 先加入文件夹
        if not list_file:  # 仅列出文件夹
            return ret
        if directory != '':
            # 根目录下不可能有文件(邮件)
            server = self.servers[0]
            server.select(self.origin[directory.split('/')[-1]])
            typ, data = server.search(None, 'ALL')
            for num in data[0].split():
                typ, data = server.fetch(num, 'BODY[HEADER]')
                data = data[0][1].decode()
                ret.add(re.compile('''\\[mailDisk](.*)<[0-9]*/[0-9]*>''').findall(data)[0])
        return ret
