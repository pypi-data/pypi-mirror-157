A simple interface of excuting python functions or shell commands parallelly

```python
import os
from simpletaskrun import Runner

def task(cmd):
  #execute shell command and python code
  os.system(cmd)
  print('%s has been echoed' % cmd.split(' ')[-1])
	
# 10 is the max task num in same time
runner = Runner(10)
for i in range(100):
  cmd = 'echo %s' % i
  runner.add(task, [cmd])

runner.clear()
```