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
#  along with this program.  If not, see <http:#www.gnu.org/licenses/>.

import sys
sys.dont_write_bytecode = True

import signal
import curses
import http.client
import json
import os
import _thread
import optparse
<<<<<<< HEAD
import queue
import urllib.request
=======

>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
from sys import stdout
from subprocess import Popen, PIPE, DEVNULL
from time import sleep
from colorama import init, Fore
<<<<<<< HEAD
from os import getenv
=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2

class JamendoRadioPlayer:
	def __init__(self):
		self.model = Model()
		self.player = Player(self.model)
		self.jamendo = Jamendo()
		self.view = None

	def init(self, radio):
		self.model.setRadios(self.jamendo.getRadios())
<<<<<<< HEAD

		if radio:
			# Interfaz colorama (se envía una radio)

			# Capturar CTRL-c para terminar la aplicación
			signal.signal(signal.SIGINT, self.__signalHandler)

			# Inicializar la vista
			self.model.view = ColoramaView(self)

			# Dibujado inicial de la vista
			self.model.view.render(self.model)

=======

		if radio:
			# Interfaz colorama (se envía una radio)

			# Capturar CTRL-c para terminar la aplicación
			signal.signal(signal.SIGINT, self.__signalHandler)

			# Inicializar la vista
			self.model.view = ColoramaView(self)

			# Dibujado inicial de la vista
			self.model.view.render(self.model)
			
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
			# Buscar la radio
			x = None
			for i, r in enumerate(self.model.radios):
				if int(radio) == r['id']:
					x = self.jamendo.getRadio(self.model.getRadioName1(r))
					break

			# Reproducir la radio
			self.player.play(x)
		else:
			# Interfaz curses
			curses.wrapper(self.curses)
<<<<<<< HEAD

	def curses(self, stdscr):
		# Inicializar la vista
		self.model.view = CursesView(self, stdscr)

		# Dibujado inicial de la vista
		self.model.view.render(self.model)

		# Loop de aplicación
		self.model.view.loop()

	def echo(self):
		radios = self.jamendo.getRadios()

=======

	def curses(self, stdscr):
		# Inicializar la vista
		self.model.view = CursesView(self, stdscr)

		# Dibujado inicial de la vista
		self.model.view.render(self.model)

		# Loop de aplicación
		self.model.view.loop()

	def echo(self):
		radios = self.jamendo.getRadios()

>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
		print("{0:5}  {1}".format("RADIO", "NAME"))
		for r in radios:
			print("{0:5}. {1}".format(r["id"], r["dispname"]))

	def quit(self):
<<<<<<< HEAD
=======
		self.view.quit()
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
		exit()

	def __signalHandler(self, signal, frame):
		self.quit()

# Clase para comunicarse con la API de Jamendo
class Jamendo:
	def __init__(self):
		self.client_id = '47c19839' # Don't change value

	def getRadios(self):
		radios = self.__getData("radios/?client_id=%s&format=json&limit=all" % self.client_id)
		return radios['results']

	def getRadio(self, name):
		radio = self.__getData("radios/stream?client_id=%s&format=json&name=%s" % (self.client_id, name))
		return radio['results'][0]

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

# Clase para reproducir
class Player:
	def __init__(self, model):
		self.model = model
		self.model.setVolume(100)
<<<<<<< HEAD
		self.volume = 100
=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
		self.model.setPlaying(False)
		self.pipe = Popen(["mpg123","-R"], stdin=PIPE, stdout=DEVNULL, stderr=DEVNULL)

	def play(self, radio):
		if not radio:
			return
		self.model.setRadio(radio)
		self.model.setPlaying(True)
		self.pipe.stdin.write(bytes('LOAD %s\n' % self.model.getRadioStream(), 'UTF-8'))

	def stop(self):
		self.model.setPlaying(False)
		self.pipe.stdin.write(bytes('STOP\n', 'UTF-8'))

	def pause(self):
		self.model.setPlaying(False)
		self.pipe.stdin.write(bytes('PAUSE\n', 'UTF-8'))

	def playPause(self):
		self.model.setPlaying(not self.isPlaying())
		self.pause()

	def isPlaying(self):
		return self.model.playing

	def volumeUp(self):
		self.volume += 5
		self.setVolume(self.volume)

	def volumeDown(self):
		self.volume -= 5
		self.setVolume(self.volume)

	def setVolume(self, volume):
		if volume < 0 or volume > 100:
			return
		self.model.setVolume(volume)
		self.pipe.stdin.write(bytes('VOLUME %i\n' % self.model.volume, 'UTF-8'))

# Clase que contiene los datos que se mostrarán en el la vista.
# Cuando se produzca algun cambio en alguno de ellos la vista será notificada
# para que se rederice de nuevo con la información cambiada (Patrón MVC).
class Model:
	def __init__(self):
		self.radios = None
		self.radio = None
		self.playing = None
		self.volume = None

		self.view = None

	# Notificar a la vista de cambios
	def __notify(self):
		if self.view:
			self.view.render(self)

	def setRadios(self, radios):
		self.radios = radios
		self.__notify()

	def setRadio(self, radio):
		self.radio = radio
		self.__notify()

	def setPlaying(self, playing):
		self.playing = playing
		self.__notify()

	def setVolume(self, volume):
		self.volume = volume
		self.__notify()
<<<<<<< HEAD

	# TODO:
	# Estos métodos que acceden a las propiedades devueltas por la API de
=======
	
	# TODO:
	# Estos métodos que acceden a las propiedades devueltas por la API de 
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
	# Jamendo probablemente estarían mejor en una clase de utilidades. ¿?
	def getRadioName1(self, radio):
		if not radio:
			return
		return radio['name']

	def getRadioName0(self):
		return self.getRadioName1(self.radio)

	def getRadioDisplayName1(self, radio):
		if not radio:
			return
		return radio['dispname']

	def getRadioDisplayName0(self):
		return self.getRadioDisplayName1(self.radio)

	def getRadioStream(self):
		if not self.radio:
			return
		return self.radio['stream']

	def getRadioPlayingNowArtistName(self):
		if not self.radio:
			return ''
		return self.radio['playingnow']['artist_name']

	def getRadioPlayingNowTrackName(self):
		if not self.radio:
			return ''
		return self.radio['playingnow']['track_name']

<<<<<<< HEAD
	def getTrackID(self):
		if not self.radio:
			return ''
		return self.radio['playingnow']['track_id']

=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
# Vista colorama
class ColoramaView:
	def __init__(self, jrp):
		self.jrp = jrp

	def render(self, model):
		print(model.getRadioDisplayName0())
		print(model.getRadioPlayingNowArtistName())
		print(model.getRadioPlayingNowTrackName())

# Vista curses
class CursesView:
	def __init__(self, jrp, stdscr):
		self.jrp = jrp
		self.r = 0
<<<<<<< HEAD
		# Esto inicia la función encargado de gestinoar una cola de datos
		self.queue = queue.Queue()
=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2

		# Inicializar la interfaz
		self.stdscr = stdscr
		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)
		curses.doupdate()
		self.stdscr.keypad(1)
		self.stdscr.nodelay(1)
		curses.start_color()
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
		curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.resize_term(24, 80)
		stdout.write("\x1b]2;Jamendo Radio Player\x07")

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

		# Stattus bar
		self.statusbar = self.win.derwin(2, 78, 21, 1)
		self.statusbar.bkgd(' ', curses.color_pair(2))

<<<<<<< HEAD
		# Actual download
		self.downloadwin = self.statusbar.derwin(1, 78, 1, 0)

=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
		# Volume info
		self.volumewin = self.statusbar.derwin(1, 19, 0, 58)
		self.volumewin.addnstr(0, 0, 'Volume: ##########', 19)

		self.win.overwrite(self.stdscr)

<<<<<<< HEAD
		_thread.start_new_thread(self.__downloadFile, ())

=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
	# Método que renderiza el modelo en la interfaz
	def render(self, model):
		for i, radio in enumerate(model.radios):
			if i == self.r:
				self.win.addstr(i + 4, 2, model.getRadioDisplayName1(radio), curses.color_pair(2))
			else:
				self.win.addstr(i + 4, 2, model.getRadioDisplayName1(radio), curses.A_NORMAL)
		self.win.refresh()

		self.wintags.addstr(0, 0, model.getRadioPlayingNowArtistName())
		self.wintags.addstr(2, 0, model.getRadioPlayingNowTrackName())
		self.wintags.refresh()

		v = "#" * int(model.volume / 10)
		self.volumewin.addnstr(0, 0, 'Volume: %s' % v, 19)
		self.volumewin.refresh()

	def menu(self):
		n = len(self.jrp.model.radios) - 1
		i = self.r
		key = self.stdscr.getch()
		while key != ord('\n'):
<<<<<<< HEAD
			sleep(0.05)
=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
			# It was a pain in the ass trying to get the arrows working.
			# Since the curses.KEY_* did not work, I used the raw return value.
			if key == 258:
				i += 1
			elif key == 259:
				i -= 1

			if i < 0:
				i = 0
			if i > n:
				i = n

			self.r = i
			self.render(self.jrp.model)

			key = self.stdscr.getch()

		name = self.jrp.model.radios[self.r]['name']
		return self.jrp.jamendo.getRadio(name)

	def loop(self):
		try:
			while True:
<<<<<<< HEAD
				sleep(0.05)
=======
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
				k = self.stdscr.getch()
				if k == ord('c'):
					radio = self.menu()
					self.jrp.player.play(radio)
				elif k == ord('q'):
					self.jrp.quit()
				elif k == ord('x'):
					self.jrp.player.stop()
				elif k == ord('z'):
					self.jrp.player.playPause()
				elif k == ord('a'):
					self.jrp.player.volumeDown()
				elif k == ord('s'):
					self.jrp.player.volumeUp()
<<<<<<< HEAD
				elif k == ord('d'):
					self.Download()
		except KeyboardInterrupt:
			self.jrp.quit()

	def Download(self):
		name = self.jrp.model.radios[self.r]['name']
		track_id = self.jrp.jamendo.getRadio(name)['playingnow']['track_id']
		artist_name = self.jrp.jamendo.getRadio(name)['playingnow']['artist_name']
		track_name = self.jrp.jamendo.getRadio(name)['playingnow']['track_name']

		# The following line is for use in 3.0 version of the Jamendo API (Beta)
		#url = 'http://api.jamendo.com/v3.0/tracks/file?client_id=%s&audioformat=ogg&id=%s' % (self.jamendo.client_id, self.track_id)
		url = 'http://storage-new.newjamendo.com/download/track/%s/mp32' % track_id
		self.queue.put([url, artist_name, track_name])
		name = self.jrp.model.radios[self.r]['name']
		pass

	def __downloadFile(self):
		while True:
			sleep(0.05)
			data = self.queue.get()
			self.downloadwin.addnstr(0, 0, 'Downloading: %s - %s' % (data[1], data[2]), 70)
			self.downloadwin.refresh()
			urllib.request.urlretrieve(data[0], '%s/%s - %s.mp3' % (getenv('HOME'), data[1], data[2]))
			self.downloadwin.clear()
			self.downloadwin.refresh()

=======
		except KeyboardInterrupt:
			self.jrp.quit()

>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
	def quit(self):
		self.killThreads = True
		curses.endwin()
		_thread.exit()

if __name__ == '__main__':
	parser = optparse.OptionParser(usage = 'usage: JamendoRadioPlayer.py [options]')
	parser.add_option('-e', '--echo', action='store_true', help='List Jamendo radios')
	parser.add_option('-r', '--radio', action='store', help='Play a Jamendo radio')
	(options, args) = parser.parse_args()

	if options.echo:
		JamendoRadioPlayer().echo()
	elif options.radio:
		JamendoRadioPlayer().init(options.radio)
		while True:
			input()
<<<<<<< HEAD
	else:
=======
	else:		
>>>>>>> 6f26cd022eded8f66b341879e5fa028cf3b04bc2
		JamendoRadioPlayer().init(None)
