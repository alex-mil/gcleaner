import sys

if sys.version_info[0] > 2:
    sys.stderr.write("Python version must be 2.x.x\n")
    sys.exit(-1)

from os import path, curdir, walk
from subprocess import Popen, PIPE
from threading import Timer


class GCleaner(object):
    def __init__(self):
        self.cur_dir = path.abspath(curdir)
        self.git_fetch_cmd = 'git fetch --prune origin'.split()
        self.git_branch_cmd = 'git branch --remote'.split()
        self.git_push_delete_cmd = 'git push origin --delete'.split()
        self.seconds = 5
        self.kill = lambda process: process.terminate()

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
        fetch = Popen(self.git_fetch_cmd, cwd=path, stdout=PIPE, stderr=PIPE)
        _timer = Timer(self.seconds, self.kill, [fetch])

        try:
            _timer.start()
            fetch.wait()
            (_, _) = fetch.communicate()
            if fetch.returncode:
                print("Failed! Return code = {}".format(fetch.returncode))
        finally:
            _timer.cancel()

    def _get_remote_branches(self, path):
        git_branch = Popen(self.git_branch_cmd, cwd=path,
                           stdout=PIPE, stderr=PIPE)
        _timer = Timer(self.seconds, self.kill, [git_branch])

        try:
            _timer.start()
            (stdout, _) = git_branch.communicate()
            if git_branch.returncode:
                print("Failed! Return code = {}".format(git_branch.returncode))
            else:
                return stdout.decode('utf-8').split('\n')
        finally:
            _timer.cancel()

    def _push_with_delete(self, path, branches):
        for branch in branches:
            branch = branch.strip(' *').split('/')[-1]
            if not 'production' in branch and not 'master' in branch:
                cmd = self.git_push_delete_cmd + [branch]
                git_push = Popen(cmd, cwd=path, stdout=PIPE, stderr=PIPE)
                _timer = Timer(self.seconds, self.kill, [git_push])
                try:
                    _timer.start()
                    git_push.wait()
                    (_, _) = git_push.communicate()
                    if git_push.returncode:
                        print("Failed! Return code = {}".format(
                            git_push.returncode))
                    else:
                        print "Executing: {}".format(' '.join(map(str, cmd)))
                finally:
                    _timer.cancel()


def main():
    f_path = raw_input(
        'Where to start scaning? (current directory by default) --> ')
    gc = GCleaner()
    gc.clean(None if not f_path else f_path)
    print('The script has finished.')


if __name__ == '__main__':
    main()
