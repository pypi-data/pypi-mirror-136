# How to use?
```python
from Task import TaskManager
import time

with TaskManager("Job1") as tm1:
    with TaskManager("Job2") as tm2:
	    time.sleep(1.0)
	
	time.sleep(1.0)


TaskManager.summary()
```
