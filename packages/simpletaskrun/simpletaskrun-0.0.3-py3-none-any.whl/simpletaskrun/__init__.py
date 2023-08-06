from concurrent.futures import ThreadPoolExecutor
import time
from multiprocessing import cpu_count
from termcolor import colored

class Runner:
  def __init__(self, max_num=1):

    if max_num > cpu_count():
      print(colored('%d threadpool, %d cpu cores\n' % (max_num, cpu_count()), 'yellow'))
    else:
      print(colored('%d threadpool, %d cpu cores\n' % (max_num, cpu_count()), 'yellow'))
    self.max_num = max_num
    self.keeper = []
    self.executor = ThreadPoolExecutor(max_num)

  def add(self, command, command_args):
    if len(self.keeper) < self.max_num:
      if command != '':
        print(colored('Add new task with args: %s\n' % ' '.join(command_args), 'green'))
        task1 = self.executor.submit(lambda p: command(*p), command_args)
        self.keeper.append(task1)
    else:
      while True:
        time.sleep(0.1)
        for task in self.keeper:
          if task.done() == True:
            self.keeper.remove(task)
        if (len(self.keeper) < self.max_num):
          break
      self.add(command, command_args)

  def clear(self):
    while True:
      if (len(self.keeper) == 0):
        print(colored('All tasks finished!', 'green'))
        break
      for task in self.keeper:
        if task.done() == True:
          self.keeper.remove(task)
      time.sleep(0.1)

  def __del__(self):
    while True:
      if len(self.keeper) == 0:
        break
      for command, task in list(self.keeper.items()):
        if task.done() == True:
          self.keeper.remove(task)
      time.sleep(0.1)