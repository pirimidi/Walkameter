#!/usr/local/bin/python

"""
-------------------------------------------------------------------------------- 
 Author: Mirko Palla.
 Date: January 2, 2009.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.

 Purpose: given function command, this utility program performs any fluidics 
 method contained in biochemistry module.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file.
------------------------------------------------------------------------------- 
"""

import sys
import time

#----------------------------- Input argument handling ---------------------------------

if len(sys.argv) == 1:
	print """\n
     **********************************************************************         
     *              Welcome to the syringe pump utility program           *
     *         Usage: python fluidics_utils.py flowcell-number method     *
     **********************************************************************

     |  Methods defined here:
     |  
     |  __init__(self, config, serial_port, logger=None)
     |      Initialize Cavro XCalibur syringe pump object with default parameters.
     |  
     |  initialize_syringe(self)
     |      Initializes syringe pump with default operation settings.
     |  
     |  set_absolute_volume(self, absolute_volume)
     |      Sets syringe pump absolute volume (an integer) in ragne of 0-1000, where 0 is
     |      the syringe initial position and the maximum filling volume is the stroke of 
     |      the syringe (1000 ul).
     |  
     |  set_speed(self, speed)
     |      Sets syringe pump move speed (an integer) in range of 0-40, where the 
     |      maximum speed is 0 equivalent to 1.25 strokes/second = 1250 ul/s.
     |  
     |  set_valve_position(self, valve_position)
     |      Sets to given syringe pump valve position, an integer.
     |  
     |  syringe_command(self, command)
     |      Sends syringe pump command and checks device response integrity.\n\n"""

	sys.exit()

elif len(sys.argv) < 2:
	print '\n--> Error: not correct input!\n--> Usage: python syringe_utils.py [method-name]\n'
	sys.exit()

else:
	import ConfigParser						# Import configuration parser class.
	from logger import Logger					# Import logger class.
	from serial_port import Serial_port				# Import serial port class.
	from syringe_pump import Syringe_pump				# Import syringe pump class.

	#--------------------- "Walking" syringe pump initialization ------------------------

	config = ConfigParser.ConfigParser()
	config.readfp(open('config.txt'))

	t0 = time.time()                # get current time
	print '\n'
	logger = Logger(config)         # initialize logger object

	serial_port = Serial_port(config, logger)			# Initialize serial port object.
	syringe_pump = Syringe_pump(config, serial_port, logger)	# Initialize syringe pump object.

	#---------------------------------------------------------------------------------------
	#			     SYRINGE PUMP FUNCTIONS
	#---------------------------------------------------------------------------------------

	logger.info('***\t--> Started %s method execution - syringe_utils.py' % sys.argv[1])

	method = (sys.argv[1])  # assign name of requested method

	if method == 'initialize_syringe':
		syringe_pump.initialize_syringe()

	elif method == 'set_absolute_volume':
		print "INFO\t ***\t--> Please, enter desired plunger position [integer]: ",
		position = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing new-line character
		syringe_pump.set_absolute_volume(position)

	elif method == 'set_speed':
		print "INFO\t ***\t--> Please, enter desired plunger speed [integer]: ",
		speed = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing new-line character
		syringe_pump.set_speed(speed)

	elif method == 'set_valve_position':
		print "INFO\t ***\t--> Please, enter desired valve position [integer]: ",
		position = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing new-line character
		syringe_pump.set_valve_position(position)

	elif method == 'syringe_command':
		print "INFO\t ***\t--> Please, enter a valid syringe pump command [string]: ",
		command = sys.stdin.readline().strip()  # use stdin explicitly and remove trailing new-line character
		syringe_pump.syringe_command(command)
	else:
		print 'WARNING\t ***\t--> Error: not correct method input!\n\n--> Double check method name (1st argument)\n'
		sys.exit(1)

	#-------------------------- Duration of syringe pump method test ------------------------------

	delta = (time.time() - t0)  # Calculate elapsed time for syringe pump method execution.
	logger.warn('***\t--> Finished %s method execution - duration: %0.2f seconds\n' % (method, delta))

