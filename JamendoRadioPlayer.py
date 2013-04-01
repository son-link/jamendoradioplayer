#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  A player for Jamendo radios for use on GNU/Linux terminal
#
#  Copyright 2013 Alfonso Saavedra "Son Link" <sonlink@dhcppc4>
#  Copyright 2013 picodotdev <picodotdev@gmail.com>
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
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

class JamendoRadioPlayer:
	def __init__(self):
		# Global variables
		self.player = Player()
		self.jamendo = Jamendo()

		self.track = 0

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
		controls.addstr(0, 2, 'z: Play/Pause, x: Stop, c: Change radio, d: Download actual track', 1)
		controls.addstr(1, 2, 'a: Volume down, s: Volume up, q: Exit', 1)
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
		self.play(radio)

		try:
			while True:
				k = stdscr.getch()
				if k == ord('c'):
					radio = self.radiosMenu()
					self.play(radio)
				elif k == ord('q'):
					self.quit()
				elif k == ord('x'):
					self.stop()
				elif k == ord('z'):
					self.playPause()
				elif k == ord('a'):
					self.volumeDown()
				elif k == ord('s'):
					self.volumeUp()

		except KeyboardInterrupt:
			self.quit()

	def radiosMenu(self):
		"""List radios"""
		self.statusbar.addnstr(1, 1, 'Geting radios list', 78)
		self.statusbar.clear()
		self.statusbar.refresh()

		radios = self.jamendo.getRadios()
		if radios['headers']['code'] == 0:
			totalradios = len(radios['results'])
			pos = 0
			x = None
			h = curses.color_pair(2)
			while x != ord('\n'):
				self.win.addstr(2, 2, "Radios", curses.A_BOLD)
				for index in range(totalradios):
					if pos == index:
						self.win.addstr(index + 4, 2, radios['results'][index]['dispname'], h)
					else:
						self.win.addstr(index + 4, 2, radios['results'][index]['dispname'], n)
				self.win.refresh()
				x = stdscr.getch()
				# It was a pain in the ass trying to get the arrows working.
				if x == 258:
					if pos < totalradios - 1:
						pos += 1
					else:
						pos = 0
				# Since the curses.KEY_* did not work, I used the raw return value.
				elif x == 259:
					if pos > 0:
						pos += -1
					else:
						pos = totalradios - 1
				#elif x != ord('\n'):
					#curses.flash()
					# show_error() is my custom function for displaying a message:
					# show_error(str:message, int:line#, int:seconds_to_display)
					#show_error('Invalid Key',11,1)

			return int(pos)

	def play(self, radio):
		"""Start playing"""
		self.radio = radio
		radio = self.jamendo.getRadio(self.radio)

		if (len(radio['results']) == 0):
			return

		stream = radio['results'][0]['stream']

		self.player.play(stream)

		_thread.start_new_thread(self.__getTrackTags, ())

	def stop(self):
		self.player.stop()

	def playPause(self):
		self.player.playPause()

	def volumeUp(self):
		self.player.volumeUp()
		self.__updateVolume()

	def volumeDown(self):
		self.player.volumeDown()
		self.__updateVolume()

	def __updateVolume(self):
		v = "#" * int(self.player.volume / 10)
		self.volumewin.addnstr(0, 0, 'Volume: %s' % v, 19)
		self.volumewin.refresh()

	def quit(self):
		"""Exit"""
		self.killThreads = True
		curses.endwin()
		_thread.exit()
		exit()

	def __getTrackTags(self):
		"""Get tags from actual track"""
		while True:
			radio = self.jamendo.getRadio(self.radio)
			self.wintags.clear()
			self.wintags.addstr(0, 0, radio['results'][0]['playingnow']['artist_name'])
			self.wintags.addstr(2, 0, radio['results'][0]['playingnow']['track_name'])
			self.wintags.refresh()
			ml = int(radio['results'][0]['callmeback'])
			sleep(ml / 1000.0)

class Jamendo:
	def __init__(self): 
		self.client_id = '47c19839' # Don't change value
		self.radios = None

	def getRadios(self):
		if not self.radios:
			self.radios = self.__getData("radios/?client_id=%s&format=json&limit=all" % self.client_id)
		return self.radios

	def getRadio(self, radio):
		return self.__getData("radios/stream?client_id=%s&format=json&id=%i" % (self.client_id, radio))

	def __getData(self, get):
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

class Player:
	def __init__(self): 
		self.volume = 100
		self.stream = None
		self.playing = False
		self.pipe = Popen(["mpg123","-R"], stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

	def play(self, stream):
		if not stream:
			return
		self.stream = stream
		self.playing = True
		self.pipe.stdin.write(bytes('LOAD %s\n' % self.stream, 'UTF-8'))

	def stop(self):
		self.Playing = False
		self.pipe.stdin.write(bytes('STOP\n', 'UTF-8'))

	def pause(self):
		self.playing = False
		self.pipe.stdin.write(bytes('PAUSE\n', 'UTF-8'))

	def playPause(self):
		self.pause()

	def isPlaying(self):
		return self.playing

	def volumeUp(self):
		self.setVolume(self.volume + 5)

	def volumeDown(self):
		self.setVolume(self.volume - 5)

	def setVolume(self, volume):
		if volume < 0 or volume > 100:
			return
		self.volume = volume
		self.pipe.stdin.write(bytes('VOLUME %i\n' % self.volume, 'UTF-8'))

if __name__ == '__main__':
	JamendoRadioPlayer()
