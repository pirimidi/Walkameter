#!/usr/local/bin/python

"""
-------------------------------------------------------------------------------- 
 Author: Mirko Palla.
 Date: November 25, 2008.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.

 Purpose: this program checks proper installation of the fluidics system for
 walking biochemistry, i.e., on the 9-port syringe pump it switches from port 
 position 1 to 10 in a step-wise manner and also performs a full-stroke syringe 
 movement twice.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file.
------------------------------------------------------------------------------- 
"""

import sys
import time
import ConfigParser						# Import configuration file parser class.

from logger import Logger					# Import logger class.
from serial_port import Serial_port				# Import serial port class.
from syringe_pump import Syringe_pump				# Import syringe pump class.

#--------------------------- Configuration input handling ------------------------------

if len(sys.argv) < 2:
	print '\n--> Error: not correct input!\n--> Usage: python device_test.py [configuration-file-name]\n'
	sys.exit()

config = ConfigParser.ConfigParser()				# Create configuration file parser object.
config.read(sys.argv[1])					# Fill it in with configuration parameters from file.
logger = Logger(config)						# Initialize logger object.	

#---------------------------- Device(s) initialization ---------------------------------
	
t0 = time.time()							# Get current time.
print '\n'
logger.info('***\t*\t--> Installation testing started - device_test.py')  # Installation test start.

serial_port = Serial_port(config, logger)				# Initialize serial port object.
syringe_pump = Syringe_pump(config, serial_port, logger)		# Initialize syringe pump object.

#---------------------------------------------------------------------------------------
#				SYRINGE PUMP CONTROL
#---------------------------------------------------------------------------------------

# Switch ports on the 9-port syringe pump similarly to protocol described above. 

syringe_pump.initialize_syringe()					# Initialize syringe pump.

for i in range(1, 10):							# Switch all rotary valves from port position 1 to 10 in a step-wise manner.
	syringe_pump.set_valve_position(i)		 		# Set valve to port 'i'.		
	syringe_pump.set_speed(i+5)					# Set syringe speed to pull speed (moderately fast).
	syringe_pump.set_absolute_volume(1000) 				# Draw 1000 ul of fluid into syringe.
	syringe_pump.set_valve_position(9)		 		# Set valve to port 'i'.		
	syringe_pump.set_speed(0)					# Set syringe speed to eject speed (fastest possible on 0-40 scale).
	syringe_pump.set_absolute_volume(0)				# Empty syringe contents.

#-------------------------- Duration of device test ------------------------------

delta = (time.time() - t0) / 60				# Calculate elapsed time for walking protocol.
logger.warn("***\t*\t--> Finished device test protocol - duration: %0.2f minutes\n" % delta)

