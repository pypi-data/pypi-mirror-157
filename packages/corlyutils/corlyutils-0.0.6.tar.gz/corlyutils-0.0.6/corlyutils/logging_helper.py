import json
import logging

import os
import sys

import time

PROJECT_PATH = os.sep.join([os.getcwd(), 'logs'])


# 最终文件路径 {log_dir}/logs/filename
def config_my_log(filename=None, log_dir=PROJECT_PATH):
    handlers = []
    if filename:
        print("log_dir", log_dir)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        curr_date = time.strftime("%Y-%m-%d")
        logfile = filename + '.' + curr_date + '.log'
        logfile_path = os.sep.join([log_dir, logfile])

        fh = logging.FileHandler(logfile_path, encoding="UTF-8")
        fh.setLevel(logging.INFO)
        handlers.append(fh)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    handlers.append(sh)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-5.5s [%(filename)s:%(lineno)d] %(message)s',
        handlers=handlers
    )


def sleep_countdown(seconds, step=1):
    for remaining in range(seconds, 0, -1 * step):
        sys.stdout.write("\r")
        sys.stdout.write("{:2d} seconds remaining..".format(remaining))
        sys.stdout.flush()
        time.sleep(step)
