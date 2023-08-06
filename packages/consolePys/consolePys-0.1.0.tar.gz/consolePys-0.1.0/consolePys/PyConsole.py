from ColorCraft import activeColor
from ColorCraft.Print import print
import sys
import time
import platform
import os
locate_python = sys.exec_prefix

class Console(object):
	timers = {}
	def info(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="log")
	def log(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="logb")
	def logc(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="logc")
	def warn(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="warning")
	def error(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="fail")
	def fail(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="fail")
	def header(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="header")
	def normal(*objs,start="",sep=" ",end="\n",file=sys.stdout,flush=False,bg=None):
		return print(*objs,start=start,sep=sep,end=end,file=file,flush=flush,bg=bg,color="normal")
	def clear():
		command = 'cls' if platform.system().lower() == 'windows' else 'clear'
		return os.system(command)
	def time(timer):
		if isinstance(timer,str):
			Console.timers[timer] = time.time()
		else:
			raise ValueError(f"timer must be str {timer}")
		return time.time()-Console.timers[timer]
	def timeLog(timer):
		if isinstance(timer,str):
			if timer in Console.timers: return time.time()-Console.timers[timer]
			else:
				Console.warn(f"Timer '{timer}' does not exist")
				return 0
		else:
			raise ValueError(f"timer must be str {timer}")
		return time.time()-Console.timers[timer]
	def timeEnd(timer):
		if isinstance(timer,str):
			if timer in Console.timers:
				finalyTime = time.time()-Console.timers[timer]
				del Console.timers[timer]
			else:
				Console.warn(f"Timer '{timer}' does not exist")
				return 0
		else:
			raise ValueError(f"timer must be str {timer}")
		return finalyTime
