import subprocess
import shlex
from os.path import relpath
from github import Github
from github.GithubException import UnknownObjectException
from mtlibs import process_helper
import os
import sys
import time
from pathlib import Path
import base64
import logging
import json
from urllib.parse import urlparse
import requests

logger = logging.getLogger(__name__)

# 源码入口脚本文件名。（按顺序搜索）
DEFAULT_ENTRY_SCRIPTS = "main entry deploy"
GHTOKEN = os.environ.get('GHTOKEN')


def gitclone(owner, repo, token, dest_dir):
    """克隆一个github仓库"""
    cmd = "git clone https://{token}@github.com/{owner}/{repo}.git {dest_dir}/{repo}".format(
        token=token,
        owner=owner,
        repo=repo,
        dest_dir=dest_dir
    )
    completed_process = subprocess.run(shlex.split(cmd))


def deploy_repo(repo_url):
    """ 
        更新源码，目前配合github hook 的功能，暂时写死
        TODO: 目前仅支持ssh的方式拉取源码。要更新到支持github token
    """
    # os.system('curl -q --insecure https://116.202.120.181/api/ip')
    # os.system('curl -q http://google.com')
    url = urlparse(repo_url)
    owner = url.path.split('/')[1]
    repo_name = url.path.split('/')[2].rstrip('.git')

    targetdir = "/deploy/" + owner + '/'+repo_name
    if os.path.exists(targetdir):
        logger.info("文件夹 %s 存在，拉取github" % targetdir)
        os.system("cd %s && git reset --hard origin/main && git pull" %
                  targetdir)
    else:
        parent_dir = Path(targetdir).parent
        Path(parent_dir).mkdir(mode=0o777, parents=True, exist_ok=True)
        logger.info("部署路径 %s" % targetdir)
        os.system("git clone {url} {targetdir}".format(
            url=repo_url,
            targetdir=targetdir
        ))
    # 运行

    is_entry_exists = False
    for entry_file in DEFAULT_ENTRY_SCRIPTS.split(' '):
        fullpath = os.path.join(targetdir, entry_file)
        logger.info("搜索入口脚本；{}".format(fullpath))
        if os.path.exists(fullpath):
            is_entry_exists = True
            logger.info("执行脚本 %s " % targetdir)
            proc = subprocess.Popen(['sh', '-c', fullpath],  cwd=targetdir)
            break
    if not is_entry_exists:
        logger.warn("仓库入库脚本文件'{}'不存在，跳过启动".format(DEFAULT_ENTRY_SCRIPTS))




class Ghrepo():
    """对一个github repo进行操作"""
    def __init__(self,url:str=None,token:str=None,owner:str=None,repo:str=None):
        if url:
            repourl = urlparse(url)
            self.token = repourl.password
            self.owner = repourl.username        
            pathitems = repourl.path.split('/')
            self.repo = pathitems[1]
            print('REPO') 
            print(f'根据网址否则ghrepo， token {self.token}, owner:{self.owner}, repo:{self.repo}')
        else:
            self.token = token
            self.owner = owner
            self.repo = repo

        self.http_headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }

     
         
        

    def repoInfo():
        """获取当前仓库的信息"""
        r = requests.get(
            f'https://api.github.com/orgs/{self.owner}/repos',
            data=payload,
            headers=self.http_headers)
        text = r.text
        print("DEBUG 当前仓库信息", json.loads(r.text))

    def _put(apiurl,payload):
        """发出put请求"""
        return requests.put(
            f'https://api.github.com/orgs/{self.owner}/repos',
            data=payload,
            headers=self.http_headers)

    def write_content(self, path, content):
        """将文件内容写入仓库"""
        payload = {
            "owner": self.owner,
            "repo": self.repo,
            "path": path,
            "message": 'commit message 1',
            "content": content
        }
        r = requests.put(f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}',
            data=content,
            headers=self.http_headers)

        print('响应：',r.text)
        return  json.dumps(r.text)



class GHRepo_old():
    """这是旧的，使用的第三方库，感觉累赘。"""
    def __init__(self, token, owner, repo):
        self.token = token
        self.owner = owner
        self.g = Github(token)
        self.repo = self.g.get_repo(
            "{owner}/{repo}".format(owner=owner, repo=repo))

    def gh_writefile(self, path, content_text):
        """在仓库对应路径写文件"""
        # repo = self.g.get_repo("{owner}/{repo}".format(owner=self.owner, repo=self.repo))
        try:
            content = self.repo.get_contents(path)
            # 更新
            self.repo.update_file(content.path, "modi",
                                  content_text, content.sha)
        except UnknownObjectException as e:
            # 文件不存在,创建
            self.repo.create_file(path, "create", content_text)

    def gh_readfile(self, path):
        """在仓库对应路径读文件"""
        repo = self.g.get_repo(
            "{owner}/{repo}".format(owner=self.owner, repo=self.repo))
        content = repo.get_contents(path)
        context_bytes = base64.b64decode(content.content)
        context_text = context_bytes.decode()
        print(context_text)

    def putFiles(self, local_dir):
        """将文件夹内的所有文件上传(更新)到仓库上"""
        dir = os.path.abspath(local_dir)
        for home, dirs, files in os.walk(dir):
            # print(home, dirs, files)
            for file in files:
                relPath = str(Path(home) / file)[len(dir) + 1:]
                # print("相对路径: %s" % relPath)
                with open(str(Path(home) / file)) as f:
                    workflow_text = f.read()
                    self.gh_writefile(relPath, workflow_text)

    def workflow_dispatch(self, name):
        """手动调度任务"""
        workflows = [x for x in self.repo.get_workflows()]
        print(workflows)
        for w in workflows:
            if w.name == name:
                print("调度工作流 {}".format(name))
                if w.create_dispatch(ref="main"):
                    print("调度成功")

    def workflows(self):
        """列出所有工作流"""
        workflows = [x for x in self.repo.get_workflows()]
        return workflows
