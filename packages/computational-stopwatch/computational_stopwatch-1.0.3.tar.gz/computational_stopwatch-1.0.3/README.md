# Computational Stopwatch

Simple stopwatch to easily print the elapsed time of a set of operations. It's a minimalistic library, but it is very useful in many real cases.

## Usage
The easiest way to use this tool is in conjunction with the **with** python statement:
```python
>> from computational_stopwatch import Stopwatch
>>
>> with Stopwatch():
>>  time.sleep(3) # <- simulates a computation 
Elapsed time 0:00:03.003106
```
Anything within the scope of the **with** statement will count against the elapsed time. An optional task name to be printed along the elapsed time (e.g. for better identification in a log) can be set in the constructor. This name will be prepended to the printed message. This is useful to track the elapsed time of several tasks ran in sequence.
```python
>> with Stopwatch("My short task"):
>>  time.sleep(3) # <- simulates a computation 
My short task complete. Elapsed time 0:00:03.003106
```
Alternatively to the use with the **with** statment, the class can be directly instantiated and the print function explicitly called.
```python
>> sw = Stopwatch()
>> time.sleep(3)
>> sw.print_elapsed_time()
Elapsed time 0:00:03.003280
```
or simply
```python
>> sw = Stopwatch()
>> time.sleep(3)
>> print(sw)
0:00:03.003269
```
The start time can be reset with the **reset_time** function and the **get_elapsed_time** method returns the unformatted elapsed time, which is useful for numerical comparisons.

Different **verbosity** levels can be set in the constructor, with 2 as the default level, with 1 only the time is printed when the object is deleted, and with 0 nothing is printed. This is convenient to directly assess the elapsed time in seconds without any rogue prints on deletion:
```python
>> sw = Stopwatch(verbosity=0)
>> time.sleep(3)
>> t = sw.get_elapsed_time()
>> print(t)
3.0032315254211426
```
By default, everything is printed on the standard output. Further or alternative streams can be set in the constructor. For instance, the folowing snipped: 
```python
>> log_file = open('/tmp/my_log_file.txt','w')
>> with Stopwatch("My logged task", streams=[sys.stdout, log_file]):
>>  time.sleep(3) # <- simulates a computation 
My logged task complete. Elapsed time 0:00:03.002731
```
prints the message both on the standard output as well as in the log file for future perusal.