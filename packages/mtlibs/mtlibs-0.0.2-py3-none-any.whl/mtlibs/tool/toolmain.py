#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
import argparse
import time
import asyncio
import getpass
import hmac
import threading
import json
import pwd
import importlib

def hello(args):
    print(" hello in tool main")

def main(argv):
    """
        tool 主模块入口
        当前被调用的方式是通过CLI主程序。
    """
    print(term.format("[TOOL 子模块]] ====", term.Color.GREEN), flush=True)
    parser = argparse.ArgumentParser(description="CLI TOOL")
    # sub help
    subparsers = parser.add_subparsers(help='子命令')
    parser_hello = subparsers.add_parser('help', help='a help')
    parser_hello.set_defaults(func=hello)


if __name__ == '__main__':
    main(sys.argv)