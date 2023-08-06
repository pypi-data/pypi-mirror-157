# mplite

![Build status](https://github.com/root-11/mplite/actions/workflows/python-package.yml/badge.svg)
[![codecov](https://codecov.io/gh/root-11/mplite/branch/main/graph/badge.svg?token=QRBR8W5AB3)](https://codecov.io/gh/root-11/mplite)
[![Downloads](https://pepy.tech/badge/mplite)](https://pepy.tech/project/mplite)
[![Downloads](https://pepy.tech/badge/mplite/month)](https://pepy.tech/project/mplite/month)

A light weight wrapper for pythons multiprocessing module that makes multiprocessing easy.

In case anyone is looking for a very easy way to use multiprocessing with args and kwargs, here is a neat wrapper as [mplite](https://pypi.org/project/mplite/):

The [test](https://github.com/root-11/mplite/blob/main/tests/test_basics.py) is also the showcase:

*1. get the imports*

```
from mplite import TaskManager, Task
import time
```

*2. Create the function that each cpu should work on individually.*

```
def f(*args, **kwargs):
    time.sleep(args[0])
    return args[0]/kwargs['hello']
```

*3. create the main function you'd like to run everything from:*

```
def main():
    args = list(range(10)) * 5
    start = time.time()
    
    with TaskManager() as tm:
        # add the first tasks
        tasks = [Task(f, *(arg/10,), **{'hello': arg}) for arg in args]

        print("an example of a tasks is available as string:\n\t", str(tasks[0]), '\n\t', repr(tasks[0]))

        results = tm.execute(tasks)   # this will contain results and tracebacks!
        
        end = time.time()
        print(f"did nothing for {end-start} seconds, producing {len(results)} results")
        print(f"hereof {len([result for result in results if isinstance(result, str) ])} had errors.")
        print(f"the rest where results: {[i for i in results if not isinstance(i,str)]}")
        
        # add more tasks to the SAME pool of workers:
        tasks = [Task(broken, *(i,)) for i in range(3)]
        results = tm.execute(tasks)
        print("More expected errors:")
        for result in results:
            print("expected -->", result)  

if __name__ == "__main__":
    main()
```

*Expected outputs*

```
an example of a tasks is available as string:
	 Task(f=f, *(0.0,), **{'hello': 0}) 
	 Task(f=f, *(0.0,), **{'hello': 0})

  0%|          | 0/50 [00:00<?, ?tasks/s]
  2%|▏         | 1/50 [00:00<00:07,  6.96tasks/s]
  4%|▍         | 2/50 [00:00<00:06,  7.75tasks/s]
  6%|▌         | 3/50 [00:00<00:05,  8.15tasks/s]
 14%|█▍        | 7/50 [00:00<00:03, 14.16tasks/s]
 18%|█▊        | 9/50 [00:00<00:02, 14.36tasks/s]
 24%|██▍       | 12/50 [00:00<00:02, 14.13tasks/s]
 32%|███▏      | 16/50 [00:01<00:01, 17.34tasks/s]
 38%|███▊      | 19/50 [00:01<00:01, 18.03tasks/s]
 42%|████▏     | 21/50 [00:01<00:01, 16.66tasks/s]
 46%|████▌     | 23/50 [00:01<00:01, 15.06tasks/s]
 52%|█████▏    | 26/50 [00:01<00:01, 17.60tasks/s]
 56%|█████▌    | 28/50 [00:01<00:01, 16.86tasks/s]
 62%|██████▏   | 31/50 [00:02<00:01, 16.72tasks/s]
 66%|██████▌   | 33/50 [00:02<00:00, 17.37tasks/s]
 70%|███████   | 35/50 [00:02<00:00, 17.72tasks/s]
 74%|███████▍  | 37/50 [00:02<00:00, 17.52tasks/s]
 80%|████████  | 40/50 [00:02<00:00, 19.88tasks/s]
 86%|████████▌ | 43/50 [00:02<00:00, 15.19tasks/s]
 90%|█████████ | 45/50 [00:02<00:00, 13.69tasks/s]
 94%|█████████▍| 47/50 [00:03<00:00, 14.46tasks/s]
 98%|█████████▊| 49/50 [00:03<00:00, 10.98tasks/s]
100%|██████████| 50/50 [00:03<00:00, 14.40tasks/s]

did nothing for 3.601374387741089 seconds, producing 50 results
hereof 5 had errors.
the rest where results: [0.1, 0.1, 0.0999..., 0.1, 0.1, 0.1, 0.1, 0.0999..., 0.0999..., 0.0999..., 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0999..., 0.0999..., 0.0999..., 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0999..., 0.0999..., 0.0999..., 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0999..., 0.0999..., 0.0999..., 0.1, 0.1, 0.1, 0.1, 0.0999..., 0.0999..., 0.1, 0.1]

  0%|          | 0/3 [00:00<?, ?tasks/s]
100%|██████████| 3/3 [00:00<00:00, 80.66tasks/s]

More expected errors:

expected --> Traceback (most recent call last):
  File "d:\github\mplite\mplite\__init__.py", line 97, in execute
    return self.f(*self.args,**self.kwargs)
  File "d:\github\mplite\tests\test_basics.py", line 36, in broken
    raise NotImplementedError("this task must fail!")
NotImplementedError: this task must fail!

expected --> Traceback (most recent call last):
  File "d:\github\mplite\mplite\__init__.py", line 97, in execute
    return self.f(*self.args,**self.kwargs)
  File "d:\github\mplite\tests\test_basics.py", line 36, in broken
    raise NotImplementedError("this task must fail!")
NotImplementedError: this task must fail!

expected --> Traceback (most recent call last):
  File "d:\github\mplite\mplite\__init__.py", line 97, in execute
    return self.f(*self.args,**self.kwargs)
  File "d:\github\mplite\tests\test_basics.py", line 36, in broken
    raise NotImplementedError("this task must fail!")
NotImplementedError: this task must fail!

```

Note that tasks **can't crash**! In case of exceptions during
task execution, the traceback is captured and the compute
core continues to execute the next task.

### How to test worker functions

Also, if you want to check that the inputs to the task
are formed correctly, you can do the check from the interpreter,
by calling `.execute()` on the task:

```
>>> t = Task(f, *(1,2,3), **{"this":42})
>>> t.execute()
```

### How to handle incremental tasks

From version 1.1.0 it is possible to add tasks incrementally.

Let's say I'd like to solve the pyramid task where I add up all numbers

```
1+2  3+4  5+6  7+8  9+10
 =    =    =    =    = 
 3 +  7    11 + 15   19
   =         =       =
   10        26  +  19
   =             =
   10      +     45
           = 
          55
```

This requires that I:

a. create a queue with 1,2,3,...,10
b. add tasks for the numbers to be added pairwise
c. receive the result
d. when I have a pair of numbers submit them AGAIN.

Here is an example of what the code can look like:
```

def test_incremental_workload():
    with TaskManager() as tm:       
        # 1. create initial workload
        checksum = 55
        for a in range(1,10,2):
            t = Task(adder, a, a+1)
            print(t)
            tm.submit(t)
    
        # 2. create incremental workload
        a,b = None,None
        while True:
            result = tm.take()
            if result is None:
                if tm.open_tasks == 0:
                    break
                else:
                    continue
            
            if a is None:
                a = result
            else:
                b = result
            
            if a and b:
                t = Task(adder, a,b)
                print(t)
                tm.submit(t)
                a,b = None,None

        print(a,b,flush=True)
        assert a == checksum or b == checksum,(a,b,checksum)


```

Output:
```
Task(f=adder, *(1, 2), **{})
Task(f=adder, *(3, 4), **{})
Task(f=adder, *(5, 6), **{})
Task(f=adder, *(7, 8), **{})
Task(f=adder, *(9, 10), **{})
Task(f=adder, *(3, 7), **{})
Task(f=adder, *(11, 15), **{})
Task(f=adder, *(19, 10), **{})
Task(f=adder, *(26, 29), **{})
55 None

```