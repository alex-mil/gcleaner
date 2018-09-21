import sys

if sys.version_info[0] < 3:
    sys.stderr.write("Python version must be 3.x.x\n")
    sys.exit(-1)

from os import path, curdir, walk
from subprocess import Popen, PIPE, TimeoutExpired


class GCleaner(object):
    def __init__(self):
        self.cur_dir = path.abspath(curdir)
        self.git_fetch_cmd = 'git fetch --prune origin'.split()
        self.git_branch_cmd = 'git branch --remote'.split()
        self.git_push_delete_cmd = 'git push origin --delete'.split()
        self.seconds = 5

    def clean(self, start_path=None):
        start_path = self.cur_dir if not start_path else start_path

        for root, dirs, _ in walk(start_path):
            for name in dirs:
                if name == '.git':
                    self._fetch_with_prune(root)
                    branches = self._get_remote_branches(root)
                    if branches:
                        self._push_with_delete(
                            root, list(filter(None, branches)))
                    else:
                        msg = """Failed:
                        Folder: {}
                        Cannot get a list of remote branches
                        """.format(root)
                        print(msg)
                    break

    def _fetch_with_prune(self, path):
        proc = Popen(self.git_fetch_cmd, cwd=path, stdout=PIPE)
        try:
            (stdout, stderr) = proc.communicate(timeout=self.seconds)
            proc.wait()
            if stderr:
                msg = """Failed:
                Output: {}
                Error: {}
                """.format(stdout.decode('utf-8'), stderr.decode('utf-8'))
                print(msg)
        except TimeoutExpired:
            proc.kill()
            proc.communicate()

    def _get_remote_branches(self, path):
        proc = Popen(self.git_branch_cmd, cwd=path, stdout=PIPE)
        try:
            (stdout, stderr) = proc.communicate(timeout=self.seconds)
            if stderr:
                msg = """Failed:
                Output: {}
                Error: {}
                """.format(stdout.decode('utf-8'), stderr.decode('utf-8'))
                print(msg)
            else:
                return stdout.decode('utf-8').split('\n')
        except TimeoutExpired:
            proc.kill()
            proc.communicate()

    def _push_with_delete(self, path, branches):
        for branch in branches:
            branch = branch.strip(' *').split('/')[-1]
            if not 'production' in branch and not 'master' in branch:
                cmd = self.git_push_delete_cmd + [branch]
                proc = Popen(cmd, cwd=path, stdout=PIPE)
                try:
                    (stdout, stderr) = proc.communicate(timeout=self.seconds)
                    proc.wait()
                    if stderr:
                        msg = """Failed:
                        Output: {}
                        Error: {}
                        """.format(stdout.decode('utf-8'), stderr.decode('utf-8'))
                        print(msg)
                    else:
                        print(stdout.decode('utf-8'))
                except TimeoutExpired:
                    proc.kill()
                    proc.communicate()


def main():
    f_path = input(
        'Where to start scaning? (current directory by default) --> ')
    c = GCleaner()
    c.clean(None if not f_path else f_path)
    print('The script has finished.')


if __name__ == '__main__':
    main()
