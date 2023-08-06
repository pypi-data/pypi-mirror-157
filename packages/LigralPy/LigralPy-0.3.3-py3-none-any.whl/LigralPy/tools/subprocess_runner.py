import collections
from enum import Flag
from glob import glob
import logging
import queue
import subprocess
import sys
import threading
import time
import chardet
from typing import Callable, List

OutputLine = collections.namedtuple("OutputLine", ["type", "content"])
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

StreamCallback = Callable[[str], None]
ExitCallback = Callable[[int], None]


class InteractiveSubProcess:
    def __init__(
        self,
        args: List[str],
        cwd: str,
        on_stdout_callback: StreamCallback = None,
        on_stderr_callback: Callable[[str], None] = None,
        on_exit_callback: ExitCallback = None,
    ):
        """
        callback: 回调函数。输入值为进程ID。
        """
        self.terminated = False
        self.q: queue.Queue[OutputLine] = queue.Queue()
        self.args = args
        self.process = subprocess.Popen(
            self.args,
            cwd=cwd,
            stdin=subprocess.PIPE,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.to = threading.Thread(
            target=self.enqueue_stream, args=(self.process.stdout, self.q, 1)
        )
        self.te = threading.Thread(
            target=self.enqueue_stream, args=(self.process.stderr, self.q, 2)
        )
        self.tp = threading.Thread(target=self.console_loop)
        self.to.setDaemon(True)
        self.te.setDaemon(True)
        self.tp.setDaemon(True)
        self.te.start()
        self.to.start()
        self.tp.start()

        self.on_stderr_callback = on_stderr_callback
        self.on_stdout_callback = on_stdout_callback
        self.on_exit_callback = on_exit_callback

    def enqueue_stream(self, stream, queue, type):  # 将stderr或者stdout写入到队列q中。
        for line in iter(stream.readline, b""):
            if self.terminated:
                break
            encoding = chardet.detect(line)["encoding"]
            queue.put(OutputLine(type, line.decode(encoding)))
        stream.close()

    def console_loop(self):
        """
        封装后的内容,用来获取进程的输出。

        """
        flag_exit = 0
        while 1:
            try:
                queue_elem = self.q.get(timeout=0.3)
                if queue_elem.type == 1:
                    logger.info("Got OutMsg:" + queue_elem.content)
                    if self.on_stdout_callback is not None:
                        self.on_stdout_callback(queue_elem.content)
                else:
                    logger.info("Got ErrMsg:" + queue_elem.content)
                    if self.on_stderr_callback is not None:
                        self.on_stderr_callback(queue_elem.content)

                continue
            except queue.Empty:
                pass
            if self.process.poll() is not None:
                # 这里是为了防止读不完输出内容，所以在接收到退出信号之后，会再检测两次循环。
                flag_exit += 1
            if flag_exit >= 2:
                self.terminate(self.process.poll())
                break

    def terminate(self, exit_code: int):
        self.terminated = True
        if self.on_exit_callback is None:
            sys.stdout.write("Subprocess terminated with exit code %s\n" % exit_code)
        else:
            self.on_exit_callback(exit_code)


_currentRunner: InteractiveSubProcess = None


def setRunner(
    cmd: List[str],
    cwd: str,
    on_exit: ExitCallback = None,
    on_stdout: StreamCallback = None,
    on_stderr: StreamCallback = None,
) -> bool:
    """
    是一个单例
    如果运行成功返回True，运行失败返回False
    """
    global _currentRunner
    if _currentRunner is None or _currentRunner.terminated:
        _currentRunner = InteractiveSubProcess(cmd, cwd, on_stdout, on_stderr, on_exit)
        return True
    else:
        return False


if __name__ == "__main__":
    exit_flag = False

    def on_exit(code):
        global exit_flag
        exit_flag = True
        print("Program exited with code", code)

    setRunner(["python", "-c", "print('hello world')"], ".", on_exit=on_exit)
    while 1:
        time.sleep(1)
        if exit_flag:
            break
