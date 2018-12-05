"""
--------------------------------------------------------------------------------
 Author: Mirko Palla.
 Date: August 25, 2009.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.
 
 Purpose: This program contains the complete code for the iterative primer wal-
 king algorithm based on cycle-iteration-number in Python.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file. 
------------------------------------------------------------------------------- 
"""

import sys
import time
import commands
import ConfigParser

from logger import Logger
from biochem import Biochem

print '\nINFO\t *\t--> START PRIMER WALKING MAIN - walking_main.py\n'

t0 = time.time()  # get current time

config = ConfigParser.ConfigParser()
config.readfp(open('config.txt'))
cycle_iter = eval(config.get("cycle_constants","cycle_iter"))

logger = Logger(config)  # initialize logger object
biochem = Biochem(logger)  # initialize biochemistry object

if biochem.speech_option == 1:
	commands.getstatusoutput('mplayer -ao pulse ../../../speech/welcome.wav')
	commands.getstatusoutput('mplayer -ao pulse ../../../speech/start.wav')

logger.info("*\t--> Started primer walking")

while (biochem.cycle < cycle_iter):
	biochem.cycle +=1

	if biochem.speech_option == 1:
		commands.getstatusoutput('mplayer -ao pulse ../../../speech/cycle_' + str(biochem.cycle) + '.wav')
	biochem.run()

biochem.finish()

delta = (time.time() - t0) / 60  # calculate elapsed time for primer walking cycles
logger.warn("*\t--> Finished primer walking - duration: %0.2f minutes" % delta)

if biochem.speech_option == 1:
	commands.getstatusoutput('mplayer -ao pulse ../../../speech/end.wav')

print 'INFO\t *\t--> END PRIMER WALKING MAIN - walking_main.py\n'
