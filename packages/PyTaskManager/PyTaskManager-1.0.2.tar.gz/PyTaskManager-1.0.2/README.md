# What is PyTaskManager?
PyTaskManager(refer to TaskManager below) create blocks.

# How to use?
## Simplest example
Below example is the simplest implementation of TaskManager.
Using TaskManager using with statement, you can create a block.
In this case, first with statement is managed as Task `Job1`, and second with statement is managed as Task `Job2` as well.

TaskManager can measure the elapsed time of every task.
When you want to get summary, please call `TaskManager.summary()` function for showing the elapsed time.
```python
from Task import TaskManager
import time

with TaskManager("Job1") as tm1:
    with TaskManager("Job2") as tm2:
	    time.sleep(1.0)

	time.sleep(1.0)


TaskManager.summary()
# Output
# Task Summary
#         Task name: Job1 -> Elapsed time: 2.0084
#         Task name: Job2 -> Elapsed time: 1.0008
```

## Advanced usage
When creating block, you might think that you don't want to measure time in specified area.
You can control it in two ways.

First, you can stop measuring time like below.

```python
from PyTaskManager import TaskManager

with TaskManager("Job1") as tm1:
	with TaskManager("Job2") as tm2:
		# do something
		tm2.pause_track()	# after this, measuring time is paused unless you call restart_track function
		# do something without time measurement
		tm2.restart_track()
		# do something with time measurement
```


Second, you can stop measuring time based on the tree structure.
In the situation below, there're 3 task `Job1`, `Job2` and `Job3`. If you want to stop measuring time of `Job2` and `Job3`, you can impelement it like below.
In this situation, `Job2` and `Job3` 's time measurement will be stopped, on the other hand, `Job1`'s time measurement will be still keeping.
```python
from PyTaskManager import TaskManager

with TaskManager("Job1") as tm1:
	with TaskManager("Job2") as tm2:
		with TaskManager("Job3") as tm3:
			TaskManager.pause_track("Job2")
			# do something without measuing time of Job2 and Job3
			TaskManager.restart_track("Job2")
```
When you use `TaskManager.pause_track()`, you must call `TaskManager.restart_track()`.
If you don't call it, the result of time mesurement will be not correct.