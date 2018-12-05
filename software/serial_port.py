"""
-------------------------------------------------------------------------------- 
 Author: Mirko Palla.
 Date: December 22, 2008.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.
 
 Purpose: This program contains the complete code for class Serial_port,
 containing a set of serial port device communication subroutines in Python.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file. 
------------------------------------------------------------------------------- 
"""

import sys
import time
import serial

class Serial_port:

	def __init__(self, config, logger=None):
		"Initialize serial port object with default parameters."

		if logger is not None:			# if defined, place logger into Biochem
			self.logging = logger

		self.ser = serial.Serial(port = config.get("communication","serial_port"),
					 bytesize = serial.EIGHTBITS,
					 parity = serial.PARITY_NONE,
					 stopbits = serial.STOPBITS_ONE,
					 timeout = float(config.get("communication","timeout")))

		self.logging.info("-\t--> Serial port object constructed")

#--------------------------------------------------------------------------------------#
#				SERIAL FUNCTIONS  				       #
#--------------------------------------------------------------------------------------#
#
# Serial command interface protocols in Linux for handling G.007 device regulation. 
# Only one port can be read from, written to at a time. That is, ser.close() must 
# be called before talking to a different piece of hardware with the ser.open() command.
#

	def set_baud(self, baudrate):
		"Sets serial port's baud rate as defined in configuration file."
		self.ser.setBaudrate(baudrate)

	def flush_input(self):
		"Flush the input buffer of the serial port."
		self.ser.flushInput()
		self.logging.info("-\t-\t--> Flushed serial port input buffer")

	def write_serial(self, data):
		"Flush input buffer, then write string data to serial port."
		self.ser.flushInput()
		self.ser.write(data)

	def parse_read_string(self, write_string, find_string, find_string_size):
		"Will read and parse string responses which return program code from the device."

		self.ser.flushInput()
		read_string = '-1'

		while read_string == '-1':
			self.write_serial(write_string)
      			read_chars = self.read_serial(find_string_size)
			read_string = str(read_chars.find(find_string))
			time.sleep(0.05)

		self.error_checking(read_chars)
		return read_chars

	def read_serial(self, num_expected):
		"""Return the number of chars in the receive buffer and compare it to expected
		character number passed as an argument."""

		total_received = 0
		read_chars = ""	
	
		while total_received < num_expected:
			iw = self.ser.inWaiting()

			if iw > num_expected:
				iw = num_expected
			read_chars = read_chars + self.ser.read(iw)
			total_received += iw
			time.sleep(0.05)

		return read_chars

	def error_checking(self, serial_response):
		"Parses syringe pump response and triggers error message based on malfunction type."

		if not (serial_response[2] == "@" or serial_response[2] == "`"): 
			
			error_type = {"a" : "Initialization", "b" : "Invalid command",
				      "c" : "Invalid operand", "d" : "Invalid command sequence",
				      "f" : "EEPROM failure", "g" : "Device not initialized",
				      "i" : "Plunger overload", "j" : "Valve overload",
				      "k" : "Plunger move not allowed", "o" : "Command overflow"}
 
			key = serial_response[2].lower()
			print "\n--> %s error with code %s!\n--> Exiting the system...\n" % (error_type[key], ord(key))
			sys.exit()

	def __del__(self):
		"Destructs serial port object - it closes any open session."
		self.ser.close()

