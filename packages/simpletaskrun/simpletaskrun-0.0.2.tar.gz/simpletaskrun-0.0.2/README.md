A simple interface of excuting python functions or shell commands parallelly

```python
from simpletaskrun import Runner
import os

def task(cmd):
	#do the task in a single thread
	os.system(cmd)
	
threadpool_size = 10 # max task num in the same time
runner = Runner(threadpool_size)
for i in range(100):
	cmd = 'echo %s' % i
	runner.add(task, [cmd])

runner.clear()
```