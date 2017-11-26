import sys
import os

if sys.platform == "linux" or sys.platform == "darwin" \
or sys.platform == "linux2":
	try:
		import curses
	except:
		print("Warning: curses module not found.")
		exit()

class claw:
	def __init__(self, directory=None, ext=None):
		if directory == None:
			self.directory = str(os.getcwd())+"/"
			print(self.directory)
		rows, cols = os.popen('stty size','r').read().split()
		self.rows=int(rows) 
		self.cols=int(cols)
		self.origin = os.getcwd()
		self.hmarg = 3
		self.vmarg = 3
		self.inmarg= 3
		self.outer_x = self.cols - 2*self.hmarg
		self.outer_y = self.rows - 2*self.vmarg
		self.pad_x = self.outer_x - 4
		self.pad_y = self.outer_y - 4
		self.ext=ext
		self.window  = 0
		self.lchoice = 0
		self.rchoice = 0
		self.listfiles = []
		self.chosen = []
		self.ch = ''
		self.directory_populate()
		self.curses_init()
		self.outerbox = curses.newwin(self.rows - 2*self.vmarg, \
						  self.cols - 2*self.hmarg, \
						  self.vmarg,self.hmarg)
		try:
			self.directorypad = curses.newpad(len(self.listfiles),self.cols - 2*self.inmarg)
		except:
			self.directorypad = curses.newpad(1,self.cols - 2*self.inmarg)
		self.fpad= curses.newpad(len(self.listfiles),self.cols - 2*self.inmarg)
		self.okpad= curses.newpad(1,6)
		self.draw_frames()
		self.draw_ok()
		self.draw_directorypad()
		self.draw_fpad()
		self.mainloop()
			
	def curses_init(self):
		self.screen = curses.initscr()
		curses.noecho()
		curses.curs_set(0)
		curses.start_color()
		curses.use_default_colors()
		self.screen.keypad(1)

		curses.init_pair(1,0,7)
		curses.init_pair(2,15,7)

	def directory_populate(self):
		for root, dirs, files in os.walk(os.getcwd()):
			if self.ext == None:		
				for name in files:
					if name[0] != ".":	
						self.listfiles.append(name)
				break
			if self.ext != None:
				for name in files:
					if name.endswith(str(self.ext)):
						self.listfiles.append(name)
				break
		
	def set_ext(self):
		self.screen.addstr(1,1,"Extension Filter: ")
		self.screen.refresh()
		curses.echo()
		self.ext = self.screen.getstr()
		self.ext = self.ext.decode()
		if self.ext == "" or self.ext == "none":
			self.ext = None
		curses.noecho()
		del self.listfiles; self.listfiles = []
		del self.lchoice; self.lchoice = 0
		self.directory_populate()
		self.screen.clear()
		self.draw_frames()
		self.directorypad.clear()
		self.draw_directorypad()
		self.draw_fpad() 
		self.draw_ok()
	
	def fpad_expansion(self,fy):
		self.fpad= curses.newpad(len(self.listfiles)+fy,self.cols - 2*self.inmarg)

	def directory_change(self):
		while(True):
			self.screen.move(1,1)
			self.screen.clrtoeol()
			self.screen.addstr(1,1,"Change Directory: ")
			self.screen.refresh()
			curses.echo()
			new_dir = self.screen.getstr()
			curses.noecho()
			new_dir = new_dir.decode()
			try:
				os.chdir(new_dir)
				break
			except:
				self.screen.move(1,1)
				self.screen.clrtoeol()
				self.screen.addstr(1,1,"Directory Not Found. Press ENTER.")
				errch=None
				while errch != 10:
					errch = self.screen.getch()	
		self.directory = new_dir
		del self.listfiles 
		self.listfiles = []
		del self.lchoice; self.lchoice = 0
		self.directory_populate()
		self.screen.clear()
		self.draw_frames()
		fy,fx = self.fpad.getmaxyx()
		if fy < len(self.listfiles):
			self.fpad_expansion(fy)
		try:
			self.directorypad = curses.newpad(len(self.listfiles),self.cols - 2*self.inmarg)
		except:
			self.directorypad = curses.newpad(1,self.cols - 2*self.inmarg)
		self.directorypad.clear()
		self.draw_directorypad()
		self.draw_fpad()
		self.draw_ok()
				
	def draw_frames(self):
		#These are all cosmetic operations. Hence the verbosity.
		self.screen.addstr(self.rows-2,1,"Current Directory: ")
		self.screen.addnstr(self.rows-2,20,str(os.getcwd()),self.cols-22)		

		self.outerbox.addstr(self.outer_y-2,int((self.outer_x-len("[ FILES ]"))/5),\
							"[ FILES ]")	
		self.outerbox.addstr(self.outer_y-2,4*int((self.outer_x-len("[ BUILD ]"))/5),\
							"[ BUILD ]")	
			
		self.outerbox.bkgd(curses.color_pair(1))
		self.outerbox.move(1,self.inmarg)
		self.outerbox.hline(curses.ACS_HLINE, int(self.outer_x/2) - 8)
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.move(1,int(self.outer_x/2) - 5)
		self.outerbox.vline(curses.ACS_VLINE, self.outer_y - 4)
		self.outerbox.move(self.outer_y-4,self.inmarg)
		self.outerbox.hline(curses.ACS_HLINE, int(self.outer_x/2) - 8)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(1,self.inmarg)
		self.outerbox.vline(curses.ACS_VLINE, self.outer_y - 4)
			
		self.outerbox.move(1,self.inmarg)
		self.outerbox.addch(curses.ACS_ULCORNER)
		self.outerbox.move(1,int(self.outer_x/2) -5)
		self.outerbox.addch(curses.ACS_URCORNER)
		self.outerbox.move(self.outer_y-4,int(self.outer_x/2) - 5)
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.addch(curses.ACS_LRCORNER)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(self.outer_y-4,self.inmarg)
		self.outerbox.addch(curses.ACS_LLCORNER)
		
		self.outerbox.move(1,self.inmarg+int(self.outer_x/2))
		self.outerbox.hline(curses.ACS_HLINE, int(self.outer_x/2) - 7)
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.move(1,self.outer_x - 5)
		self.outerbox.vline(curses.ACS_VLINE, self.outer_y - 4)
		self.outerbox.move(self.outer_y-4,self.inmarg+int(self.outer_x/2))
		self.outerbox.hline(curses.ACS_HLINE, int(self.outer_x/2) - 7)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(1,self.inmarg+int(self.outer_x/2))
		self.outerbox.vline(curses.ACS_VLINE, self.outer_y - 4)
					
		self.outerbox.move(1,self.inmarg+int(self.outer_x/2))
		self.outerbox.addch(curses.ACS_ULCORNER)
		self.outerbox.move(1,self.outer_x-5)
		self.outerbox.addch(curses.ACS_URCORNER)
		self.outerbox.move(self.outer_y-4,self.outer_x-5)
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.addch(curses.ACS_LRCORNER)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(self.outer_y-4,self.inmarg+int(self.outer_x/2))
		self.outerbox.addch(curses.ACS_LLCORNER)
				
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.move(self.outer_y-self.hmarg,int(self.outer_x/2)-2*self.hmarg)
		self.outerbox.hline(curses.ACS_HLINE,10)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(self.outer_y-self.hmarg,int(self.outer_x/2)+self.hmarg+1)
		self.outerbox.vline(curses.ACS_VLINE,2)
		self.outerbox.move(self.outer_y-1,int(self.outer_x/2)-2*self.hmarg)
		self.outerbox.hline(curses.ACS_HLINE,10)
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.move(self.outer_y-self.hmarg,int(self.outer_x/2)-2*self.hmarg)
		self.outerbox.vline(curses.ACS_VLINE,2)
				
		self.outerbox.attron(curses.color_pair(2))
		self.outerbox.move(self.outer_y-self.hmarg,int(self.outer_x/2)-2*self.inmarg)
		self.outerbox.addch(curses.ACS_ULCORNER)
		self.outerbox.move(self.outer_y-self.hmarg,int(self.outer_x/2)+self.inmarg+1)
		self.outerbox.addch(curses.ACS_URCORNER)
		self.outerbox.move(self.outer_y-1,int(self.outer_x/2)-2*self.inmarg)
		self.outerbox.addch(curses.ACS_LLCORNER)
		self.outerbox.attron(curses.color_pair(1))
		self.outerbox.move(self.outer_y-1,int(self.outer_x/2)+self.inmarg+1)
		self.outerbox.addch(curses.ACS_LRCORNER)
			
		self.screen.noutrefresh()	
		self.outerbox.noutrefresh()
		curses.doupdate()	
	
	def draw_directorypad(self):
		self.directorypad.bkgd(curses.color_pair(1))
		for i in range(len(self.listfiles)):
			if(i == self.lchoice and self.window == 0):
				self.directorypad.attron(curses.A_REVERSE)
				self.directorypad.addstr(i,0,self.listfiles[i])
				self.directorypad.attroff(curses.A_REVERSE)
			else:
				self.directorypad.addstr(i,0,self.listfiles[i])
		self.screen.noutrefresh()
		if self.lchoice > (self.outer_y - 3*self.vmarg):
			depth = self.lchoice - (self.outer_y - 3*self.vmarg)
			self.directorypad.noutrefresh(depth,0,self.vmarg*2,self.hmarg*3, \
								int(self.rows)-3*self.hmarg, \
								int(self.cols/2)-2*self.hmarg-1)
		else:
			self.directorypad.noutrefresh(0,0,self.vmarg*2,self.hmarg*3, \
								int(self.rows)-3*self.hmarg, \
								int(self.cols/2)-2*self.hmarg-1)
		curses.doupdate()

	def draw_fpad(self):
		self.fpad.clear()
		self.fpad.bkgd(curses.color_pair(1))
		for i in range(len(self.chosen)):
			if(i == self.rchoice and self.window == 1):
				self.fpad.attron(curses.A_REVERSE)	
				self.fpad.addstr(i,0,self.chosen[i])
				self.fpad.attroff(curses.A_REVERSE)
			else:
				self.fpad.addstr(i,0,self.chosen[i])
		self.screen.noutrefresh()
		if self.rchoice > (self.outer_y - 3*self.vmarg):
			depth = self.rchoice - (self.outer_y - 3*self.vmarg)
			self.fpad.noutrefresh(depth,0,self.vmarg*2,self.hmarg*3+int(self.outer_x/2), \
								int(self.rows)-3*self.hmarg, \
								self.cols-3*self.hmarg-1)
		else:
			self.fpad.noutrefresh(0,0,self.vmarg*2,self.hmarg*3+int(self.outer_x/2), \
							int(self.rows)-3*self.hmarg, \
							self.cols-3*self.hmarg-1)
	
		curses.doupdate()

	def draw_ok(self):
		self.okpad.bkgd(curses.color_pair(1))
		if self.window == 2:
			self.okpad.attron(curses.A_REVERSE)
			self.okpad.addstr(0,0," Ok ")
			self.okpad.attroff(curses.A_REVERSE)
		else:	
			self.okpad.addstr(0,0," Ok ")
		self.screen.noutrefresh()
		self.okpad.noutrefresh(0,0,self.rows-5,int(self.outer_x/2), \
								   self.rows-4,int(self.outer_x/2)+4)
		curses.doupdate()
	
	def __call__(self):
		return self.chosen
	
	def mainloop(self):
		while(self.ch != ord('q')):
			self.ch = self.screen.getch()
			if self.ch == ord('s'):
				self.set_ext()
			if self.ch == ord('c'):
				self.directory_change()
			if self.ch == ord('\t'):
				self.window = (self.window+1)%3
				if self.window == 1 and len(self.chosen)==0:
					self.window = (self.window+1)%3
				self.draw_directorypad()
				self.draw_fpad()
				self.draw_ok()
			if self.window == 0:
				if self.ch == curses.KEY_UP and self.lchoice == 0:
					self.lchoice = len(self.listfiles)-1 
					self.draw_directorypad()
					continue
				if self.ch == curses.KEY_DOWN and self.lchoice == len(self.listfiles)-1:
					self.lchoice = 0
					self.draw_directorypad()
					continue
				if self.ch == curses.KEY_UP:
					self.lchoice -= 1
					self.draw_directorypad()
					continue
				if self.ch == curses.KEY_DOWN:
					self.lchoice += 1
					self.draw_directorypad()
					continue
				if self.ch == 10: #KEY_ENTER
					if len(self.listfiles) == 0:
						curses.doupdate()
						continue
					if self.listfiles[self.lchoice] not in self.chosen:
						self.chosen.append(self.listfiles[self.lchoice])
						self.draw_fpad()
			if self.window == 1:
				if self.ch == curses.KEY_UP and self.rchoice == 0:
					self.rchoice = len(self.chosen)-1 
					self.draw_fpad()
					continue
				if self.ch == curses.KEY_DOWN and self.rchoice == len(self.chosen)-1:
					self.rchoice = 0
					self.draw_fpad()
					continue
				if self.ch == curses.KEY_UP:
					self.rchoice -= 1
					self.draw_fpad()
					continue
				if self.ch == curses.KEY_DOWN:
					self.rchoice += 1
					self.draw_fpad()
					continue
				if self.ch == ord('d'): #curses.KEY_BACKSPACE:
					if len(self.chosen) == 0:
						curses.doupdate()
						continue
					self.chosen.remove(self.chosen[self.rchoice])
					if self.rchoice == 0:
						self.rchoice == 0
					else:
						self.rchoice -= 1
					self.draw_fpad()
					if len(self.chosen) ==0:
						self.window=0
						self.draw_directorypad()
						continue	
			if self.window == 2:
				if self.ch == 10:
					break
			curses.doupdate()
		curses.endwin()
		os.chdir(self.origin)

#def fileclaw():
#	c = claw()
#	chosen = c.listfiles
#	del c
#	return chosen
