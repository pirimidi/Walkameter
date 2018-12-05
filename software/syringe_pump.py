"""
-------------------------------------------------------------------------------- 
 Author: Mirko Palla.
 Date: August 5, 2008.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.
 
 Purpose: This program contains the complete code for class Syringe_pump, 
 containing Cavro XCalibur syringe pump communication subroutines in Python.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file. 
------------------------------------------------------------------------------- 
"""

import time 

class Syringe_pump:

	def __init__(self, config, serial_port, logger=None):
		"Initialize Cavro XCalibur syringe pump object with default parameters."

		#--------------------------------- Serial configuration ---------------------------

		self._baud_rate = int(config.get("communication","syringe_pump_baud"))
		self._read_length = int(config.get("communication","read_length"))
		self._sleep_time = float(config.get("communication","sleep_time"))

		if logger is not None:
			self.logging = logger

		self.serport = serial_port				
		self.state = 'syringe pump initialized'

		self.logging.info("-\t--> Syringe pump object constructed")

#--------------------------------------------------------------------------------------#
#			Cavro XCalibur syringe pump FUNCTIONS			       #
#--------------------------------------------------------------------------------------#
#
# Performs low-level functional commands (e.g. set pump flow rate, draw volume, etc). 
# Each command implemented here must know the command set of the hardware being 
# controlled, but does not need to know how to communicate with the device (how to poll 
# it, etc). Each functional command will block until execution is complete.
#

#--------------------------------------------------------------------------------------#
#				   BASIC SETTINGS   			               #
#--------------------------------------------------------------------------------------#

	def syringe_command(self, command):	
		"Sends syringe pump command and checks device response integrity."
			
		# Sleep for 0.01 s to make sure previous command executed
		time.sleep(0.01)

		# Set baud rate of syringe pump		 
		self.serport.set_baud(self._baud_rate)

		# Initialize syringe dead volume
		self.serport.write_serial('/1' + command + 'R\r')

		# Get device feedback and check for errors
		self.serport.parse_read_string('/1QR\r', '`', 4)

	def initialize_syringe(self):	
		"Initializes syringe pump with default operation settings."

		# Initialize syringe dead volume
		self.syringe_command('k5')

		# Initialize move to zero position, full dispense, full force
		self.syringe_command('Z0')

		# Initialize speed, range is 0-40, the maximum speed is 0 (1.25 strokes/second)
		self.syringe_command('S20')

		self.logging.info("-\t--> Initialized syringe pump object")

	def set_valve_position(self, valve_position):
		"Sets to given syringe pump valve position, an integer."

		self.syringe_command('I' + str(valve_position))
		self.logging.info("-\t--> Set syringe pump valve position to %i" % valve_position)

	def set_speed(self, speed):
		"""Sets syringe pump move speed (an integer) in range of 0-40, where the 
		maximum speed is 0 equivalent to 1.25 strokes/second = 1250 ul/s."""

		self.syringe_command('S' + str(speed))
		self.logging.info("-\t--> Set syringe pump speed to %i" % speed)

	def set_absolute_volume(self, absolute_volume):
		"""Sets syringe pump absolute volume (an integer) in ragne of 0-100, where 0 is
		the syringe initial position and the maximum filling volume is the stroke of 
		the syringe (100 ul)."""

		# Increments = (pump resolution * volume ul) / (syringe size ml * ul/ml)
		absolute_steps = (3000 * absolute_volume) / (1 * 100)

		self.syringe_command('A' + str(absolute_steps))	# 'P' command for relative pick-up, 'A' for absolute position 
		self.logging.info("-\t--> Set syringe pump absolute volume to %i" % absolute_volume)

