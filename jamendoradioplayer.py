#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  jamendoradioplayer.py
#
#  Copyright 2013 Alfonso Saavedra "Son Link" <sonlink@dhcppc4>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import curses, http.client
import json
from sys import stdout
from time import sleep
from subprocess import Popen, PIPE, DEVNULL
import _thread

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.curs_set(0)
curses.doupdate()
stdscr.keypad(1)
stdscr.nodelay(1)
curses.start_color()
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2,curses.COLOR_WHITE, curses.COLOR_BLUE)
curses.resize_term(24, 80)
stdout.write("\x1b]2;Jamendo Radio Player\x07")

h = curses.color_pair(1)
n = curses.A_NORMAL
# DON'T EDIT THE FOLLOWIN LINE
client_id = '47c19839'

class JMP():
	def __init__(self):
		# Global variables
		self.radios = None
		self.track = 0
		self.volume = 100
		self.ifplaying = False
		self.pipe = Popen(["mpg123","-R"], stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

		# Main window
		self.win =  curses.newwin(24, 80, 0, 0)
		self.win.box()
		self.win.addstr(0,2, "Jamendo Radio Player", curses.A_STANDOUT)
		self.win.addstr(2,2, "Radios", curses.A_BOLD)
		self.win.addstr(2, 25, 'Track info', curses.A_BOLD)
		self.win.addstr(4, 25, 'Artist:', curses.A_BOLD)
		self.win.addstr(6, 25, 'Title:', curses.A_BOLD)

		controls = self.win.derwin(2, 78, 19, 1)
		controls.bkgd(' ', curses.A_REVERSE)
		controls.addstr(0, 2, 'z: Play/Pause x: Stop c: Change radio d: Download actual track', 1)
		controls.addstr(1, 2, 'a: Volume down s: Volume up q: Exit', 1)
		controls.refresh()

		# Subwindow for show the track tags
		self.wintags = self.win.derwin(4, 45, 4, 34)
		self.wintags.refresh()

		# Stattus bar
		self.statusbar = self.win.derwin(2, 78, 21, 1)
		self.statusbar.bkgd(' ', curses.color_pair(2))

		# Volume info
		self.volumewin = self.statusbar.derwin(1, 19, 0, 58)
		self.volumewin.addnstr(0, 0, 'Volume: ##########', 19)

		self.win.refresh()
		self.win.overwrite(stdscr)

		radio = self.radiosMenu()
		self.radio = self.radios['results'][radio]['id']
		self.play()

		try:
			while True:
				k = stdscr.getch()
				if k == ord('c'):
					self.radiosMenu()
				elif k == ord('q'):
					self.quit()
				elif k == ord('x'):
					self.stop()
				elif k == ord('z'):
					self.play_pause()
				elif k == ord('a'):
					self.set_volume(1)
				elif k == ord('s'):
					self.set_volume(0)

		except KeyboardInterrupt:
			self.quit()

	def getData(self, get):
		"""Get data from server"""
		try:
			conn = http.client.HTTPConnection("api.jamendo.com")
			conn.request("GET", "/v3.0/%s" % get)
			response = conn.getresponse()
			if response.status == 200:
				data = response.read().decode()
				return json.loads(data)
			else:
				return False
		except:
			return False

	def radiosMenu(self):
		"""List radios"""
		self.statusbar.addnstr(1, 1, 'Geting radios list', 78)
		self.statusbar.refresh()
		if not self.radios:
			self.radios = self.getData("radios/?client_id=%s&format=json&limit=all" % client_id)
		self.statusbar.clear()
		self.statusbar.refresh()
		if self.radios['headers']['code'] == 0:

			totalradios = len(self.radios['results'])
			pos = 0
			x = None
			h = curses.color_pair(2)
			while x != ord('\n'):
				self.win.addstr(2,2, "Radios", curses.A_BOLD)
				for index in range(totalradios):
					if pos == index:
						self.win.addstr(index+4,2, self.radios['results'][index]['dispname'],h)
					else:
						self.win.addstr(index+4,2, self.radios['results'][index]['dispname'],n)
				self.win.refresh()
				x = stdscr.getch()
				# It was a pain in the ass trying to get the arrows working.
				if x == 258:
					if pos < totalradios-1:
						pos += 1
					else:
						pos = 0
				# Since the curses.KEY_* did not work, I used the raw return value.
				elif x == 259:
					if pos > 0:
						pos += -1
					else:
						pos = totalradios-1
				#elif x != ord('\n'):
					#curses.flash()
					# show_error() is my custom function for displaying a message:
					# show_error(str:message, int:line#, int:seconds_to_display)
					#show_error('Invalid Key',11,1)

			return int(pos)

	def play(self):
		"""Start playing"""
		data = self.getData("radios/stream?client_id=%s&format=json&id=%i" % (client_id, self.radio))
		track = data['results'][0]['stream']
		self.pipe.stdin.write(bytes('L %s\n' % track, 'UTF-8'))
		_thread.start_new_thread(self.getTrackTags, (self.getData, self.radio, self.wintags))
		self.isplaying = True

	def getTrackTags(self, getData, radio, wintags):
		"""Get tags from actual track"""
		while True:
			data = getData("radios/stream?client_id=%s&format=json&id=%i"% (client_id, radio))
			wintags.clear()
			wintags.addstr(0, 0, data['results'][0]['playingnow']['artist_name'])
			wintags.addstr(2, 0, data['results'][0]['playingnow']['track_name'])
			wintags.refresh()
			ml = int(data['results'][0]['callmeback'])
			sleep(ml/1000.0)

	def stop(self):
		"""Stop playing"""
		self.pipe.stdin.write(bytes('S\n', 'UTF-8'))
		self.isplaying = False

	def play_pause(self):
		"""Change playing to paused and vice versa"""
		if self.isplaying:
			self.pipe.stdin.write(bytes('P\n', 'UTF-8'))
		else:
			self.play()

	def set_volume(self, change):
		"""Change volume"""
		if change == 1 and self.volume < 100:
			self.volume += 5
		elif change == 0 and self.volume > 0:
			self.volume -= 5

		self.pipe.stdin.write(bytes('V %i\n' % self.volume, 'UTF-8'))
		self.volumewin.clear()
		v = "#" * int(self.volume/10)
		self.volumewin.addnstr(0, 0, 'Volume: %s' % v, 19)
		self.volumewin.refresh()

	def quit(self):
		"""Exit"""
		self.killThreads = True
		curses.endwin()
		_thread.exit()
		exit()

if __name__ == '__main__':
	JMP()