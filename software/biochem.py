"""
--------------------------------------------------------------------------------
 Author: Mirko Palla.
 Date: August 25, 2008.

 For: Walking biochemistry automation [fluidics software] at the Ju Lab - 
 Chemical Engineering Department, Columbia University.
 
 Purpose: This program contains the complete code for module Biochem,
 containing re-occurring biochecmistry subroutines in Python.

 This software may be used, modified, and distributed freely, but this
 header may not be modified and must appear at the top of this file. 
------------------------------------------------------------------------------- 
"""

import os
import sys 
import time 
import xlrd
import commands

import ConfigParser  # Import configuration file parser class.
from logger import Logger  # Import logger class.

from serial_port import Serial_port  # Import serial port class.
from syringe_pump import Syringe_pump  # Import syringe_pump class. 

class Biochem:

	def __init__(self, logger):
		"Initialize biochemistry object with default parameters"

		self.state = 'biochemistry object'
		self.cycle = 0  # initialize cycle number to zero

		self.config = ConfigParser.ConfigParser()  # create configuration file parser object
		self.config.read('config.txt')  # fill it in with configuration parameters from file

		self.logging = logger  # initialize logger object
		self.ser = Serial_port(self.config, self.logging)  # place serial port into Biochem
		self.syringe_pump = Syringe_pump(self.config, self.ser, self.logging)  # create syringe pump

		self.get_config_parameters()  # retrieve all configuatrion parameters from file
		self.log_config_parameters()  # register current configuration parameter list

		self.logging.info("%i\t--> Biochemistry object is constructed: [%s]" % (self.cycle, self.state))
		#commands.getstatusoutput('mplayer -ao pulse ../../../speech/biochem_object.wav')

#--------------------------------------------------------------------------------------# 
# 			      PARAMETER PARSING FUNCTIONS 			       # 
#--------------------------------------------------------------------------------------#

#------------------------------- Get_config_parameters ---------------------------------

	def get_config_parameters(self):
		"""Retieves all biochemistry and device related configuration parameters from the confi-
		guration file using the ConfigParser facility. It assigns each parameter to a field of 
		the biochemistry object, thus it can access it any time during a run."""

		self.logging.info("%i\t--> Retrieve configuration parameters from file: [%s]" % (self.cycle, self.state))

		#----------------------- Device communication --------------------------

		self.log_option = int(self.config.get("communication","log_option"))
		self.speech_option = int(self.config.get("communication","speech_option"))

		#----------------------- Tubing configuration --------------------------

		self.channel_volume = int(self.config.get("tube_constants","channel_volume"))
		self.flowcell_volume = int(self.config.get("tube_constants","flowcell_volume"))
		self.dead_volume = int(self.config.get("tube_constants","dead_volume"))

		self.excel_file = self.config.get("tube_constants","excel_file")
		self.get_excel_volumes()  # create volume dictionaries from Excel file

		#---------------------- Syringe configuration --------------------------

		self.full_stroke = int(self.config.get("syringe_constants","full_stroke"))
		self.clean_stroke = int(self.config.get("syringe_constants","clean_stroke"))
		self.clean_speed = int(self.config.get("syringe_constants","clean_speed"))
		self.reagent_speed = int(self.config.get("syringe_constants","reagent_speed"))
		self.load_speed = int(self.config.get("syringe_constants","load_speed"))
		self.empty_speed = int(self.config.get("syringe_constants","empty_speed"))
		self.final_push_speed = int(self.config.get("syringe_constants","final_push_speed"))

		#------------------------ Biochem parameters ---------------------------

		self.air_gap = int(self.config.get("biochem_parameters","air_gap"))
		self.time_limit = int(self.config.get("biochem_parameters","time_limit"))
		self.slow_push_volume = int(self.config.get("biochem_parameters","slow_push_volume"))
		self.preparation_time = int(self.config.get("biochem_parameters","preparation_time"))

		#-------------------- Incorporation parameters -------------------------

		self.incorporation_volume = int(self.config.get("incorporation_parameters","incorporation_volume"))

		self.i_nucleotide_volume = int(self.config.get("incorporation_parameters","i_nucleotide_volume"))
		self.i_buffer_volume = int(self.config.get("incorporation_parameters","i_buffer_volume"))
		self.i_Mn_volume = int(self.config.get("incorporation_parameters","i_Mn_volume"))
		self.i_9N_volume = int(self.config.get("incorporation_parameters","i_9N_volume"))

		self.incorporation_time = int(self.config.get("incorporation_parameters","incorporation_time"))
		self.incorporation_temp = int(self.config.get("incorporation_parameters","incorporation_temp"))

		#---------------------- Capping-1 parameters ---------------------------

		self.capping1_volume = int(self.config.get("capping1_parameters","capping1_volume"))

		self.c1_nucleotide_volume = int(self.config.get("capping1_parameters","c1_nucleotide_volume"))
		self.c1_buffer_volume = int(self.config.get("capping1_parameters","c1_buffer_volume"))
		self.c1_Mn_volume = int(self.config.get("capping1_parameters","c1_Mn_volume"))
		self.c1_9N_volume = int(self.config.get("capping1_parameters","c1_9N_volume"))

		self.capping1_time = int(self.config.get("capping1_parameters","capping1_time"))
		self.capping1_temp = int(self.config.get("capping1_parameters","capping1_temp"))

		#---------------------- Capping-2 parameters ---------------------------

		self.capping2_volume = int(self.config.get("capping2_parameters","capping2_volume"))

		self.c2_nucleotide_volume = int(self.config.get("capping2_parameters","c2_nucleotide_volume"))
		self.c2_buffer_volume = int(self.config.get("capping2_parameters","c2_buffer_volume"))
		self.c2_Mn_volume = int(self.config.get("capping2_parameters","c2_Mn_volume"))
		self.c2_9N_volume = int(self.config.get("capping2_parameters","c2_9N_volume"))

		self.capping2_time = int(self.config.get("capping2_parameters","capping2_time"))
		self.capping2_temp = int(self.config.get("capping2_parameters","capping2_temp"))

		#----------------------- Cleavage parameters --------------------------

		self.cleavage_volume = int(self.config.get("cleavage_parameters","cleavage_volume"))

		self.cleavage_time = int(self.config.get("cleavage_parameters","cleavage_time"))
		self.cleavage_iter = int(self.config.get("cleavage_parameters","cleavage_iter"))

		#----------------------- Path lenghts / volumes ------------------------

		self.reagent1_to_syringe_port1 = self.e_volumes['Reagent 1']['Syringe Pump 1']
		self.reagent2_to_syringe_port2 = self.e_volumes['Reagent 2']['Syringe Pump 2']
		self.reagent3_to_syringe_port3 = self.e_volumes['Reagent 3']['Syringe Pump 3'] 
		self.reagent4_to_syringe_port4 = self.e_volumes['Reagent 4']['Syringe Pump 4']
		self.reagent5_to_syringe_port5 = self.e_volumes['Reagent 5']['Syringe Pump 5'] 
		self.reagent6_to_syringe_port6 = self.e_volumes['Reagent 6']['Syringe Pump 6']
		self.reagent7_to_syringe_port7 = self.e_volumes['Reagent 7']['Syringe Pump 7']

		self.syringe_port9_to_FC_inlet = self.e_volumes['Syringe Pump 9']['Flow Cell Inlet'] + self.channel_volume
		self.FC_outlet_to_waste = self.e_volumes['Flow Cell Outlet']['Waste Bottle'] + self.channel_volume

#------------------------------- Log_config_parameters ---------------------------------

	def log_config_parameters(self):
		"""Logs all biochemistry and device related configuration parameters contained in 
		the ConfigParser object using Logger facility."""


 		if self.log_option == 0:

			self.logging.info("""\n
*********************************************************************   
*                                                                   *      
*             ***  THIS IS THE WALKAMETER LOG-FILE  ***             *
*                                                                   *
*                Current biochemistery parameter set:	            *
*                                                                   *
*********************************************************************\n""")

          		for section in self.config.sections():
             			self.logging.info("[" + section + "]\n")

             			for (key, value) in self.config.items(section):
                 			if key == "__name__":
                     				continue
                 			self.logging.info("%s = %s" % (key, value))
             			self.logging.info("\n")

 		elif self.log_option == 1:

			if os.access(self.config.get("communication","cfg_dir"), os.F_OK) is False:
				os.mkdir(self.config.get("communication","cfg_dir"))

			os.chdir(self.config.get("communication","cfg_dir"))

			from datetime import datetime
			t = datetime.now()
			time = t.strftime('%m-%d-%y %H:%M:%S')
			
			cfg_log = open("parameter_" + time + ".log", 'a')  # open up log-file to be written
			cfg_log.write("""
*********************************************************************   
*                                                                   *      
*             ***  THIS IS THE WALKAMETER LOG-FILE  ***             *
*                                                                   *
*                Current biochemistery parameter set:	            *
*                                                                   *
*********************************************************************\n\n""")

          		for section in self.config.sections():
             			cfg_log.write("[" + section + "]\n\n")

             			for (key, value) in self.config.items(section):
                 			if key == "__name__":
                     				continue
                 			cfg_log.write("%s = %s\n" % (key, value))
             			cfg_log.write("\n")
			cfg_log.close()  # close log-file

 		else:
			print '--> Error: not correct input!\n--> Usage in log-file: [communications] > log_option > 0|1\n'
			sys.exit()

#---------------------------- Gap volume calculation -----------------------------------

	def gap_volume(self, reagent_volume):
		"Determines the positioning gap needed to center the reagent volume in the flowcell."

		return int((reagent_volume - self.flowcell_volume) / 2)

#------------------------------- Get_excel_volumes -------------------------------------

	def get_excel_volumes(self):
		"""Extracts path length and tube cross-sectional area information from standard Excel file
		containing all external volume calculations in the fluidics sub-system. It automatically 
		calculates total path volumes in both cases, creating a dictionary object holding volume 
		data specified by the following format:
	
			volumes[point_B][point_A] = 'total path volume from point A to point B in the system'

		This function creates a dictionary object as one of the fields of the 'Biochem' object con-
		taining external volume calculations.

		If changes occur in either path length or cross-sectional area data, the numbers must be
		updated accordingly, but the file format and data tabulation cannot be changed."""

		self.logging.info("%i\t--> Retrieve Excel volumes from file: [%s]" % (self.cycle, self.state))

		book = xlrd.open_workbook(self.excel_file)  # read in Excel file into 'xlrd' object
		sh = book.sheet_by_index(0)  # create handle for first Excel sheet

		#----------------------------------------------------------------------------------#
		# 				EXTERNAL VOLUMES 				   #
		#----------------------------------------------------------------------------------#

		e_volumes = {} # create dictionary for external tubing volumes

		for row in range(2, 11):
 
			from_row = sh.cell_value(rowx=row, colx=0)
			to_row = sh.cell_value(rowx=row, colx=1)

			# Tubing run length

			tubing_run = sh.cell_value(rowx=row, colx=2)
			cross_sectional_area = sh.cell_value(rowx=row, colx=4)

			total_volume = tubing_run * cross_sectional_area  # tubing path volume

			#------------------------- Volume dictionary creation-------------------------
 
			if not e_volumes.has_key(from_row):
				e_volumes[from_row] = {}

			e_volumes[from_row][to_row] = int(round(total_volume))

		self.e_volumes = e_volumes

#--------------------------------------------------------------------------------------# 
# 				   BASIC SYRINGE FUNCTIONS     			       # 
#--------------------------------------------------------------------------------------#

#---------------------------- Reagent transfer through syringe -------------------------

	def move_reagent(self, fill_volume, from_speed, from_port, to_speed, to_port):
		"""Moves a given volume of reagent [1] into syringe at speed [2] through specified valve
		position [3], then transfers syringe content through valve position [4] into an other
		location in the fluidic system. All parameters are integers respectively."""

		if fill_volume <= self.full_stroke:

			self.syringe_pump.set_speed(from_speed)  # draw into syringe
			self.syringe_pump.set_valve_position(from_port)
			self.syringe_pump.set_absolute_volume(fill_volume)

			self.syringe_pump.set_speed(to_speed)  # transfer fluid through 'to_port'
			self.syringe_pump.set_valve_position(to_port)
			self.syringe_pump.set_absolute_volume(0)

		else:
			iteration = int(fill_volume / self.full_stroke)
			remainder = int(fill_volume - (iteration * self.full_stroke))

			for i in range(0, iteration):

				self.syringe_pump.set_speed(from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(self.full_stroke)

				self.syringe_pump.set_speed(to_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)
	                
			if remainder != 0:
 
				self.syringe_pump.set_speed(from_speed)  # draw remainder into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(remainder)

				self.syringe_pump.set_speed(to_speed)  # transfer remainder fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)

#------------------------- Slow reagent transfer through syringe -------------------------

	def move_reagent_slow(self, fill_volume, from_speed, from_port, to_speed, to_port):
		"""Moves a given volume of reagent [1] into syringe at speed [2] through specified valve
		position [3], then transfers syringe content through valve position [4] into an other
		location in the fluidic system. The last 100 ul reagent is drawn into the flowcell with 
		slower speed to avoid air bubble build up in the chambers. All parameters are integers 
		respectively."""

		if fill_volume <= self.full_stroke:

			if fill_volume <= self.slow_push_volume:  # if flowcell-fill volume less than last slow-fill volume

				# Slow push in to aviod air gaps

				self.syringe_pump.set_speed(self.from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(fill_volume)

				self.syringe_pump.set_speed(self.final_push_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)
			else:
				first_push_volume = fill_volume - self.slow_push_volume  #  calculate first push volume

				self.syringe_pump.set_speed(from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(first_push_volume)

				self.syringe_pump.set_speed(to_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)

				# Slow push in to aviod air gaps

				self.syringe_pump.set_speed(from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(self.slow_push_volume)

				self.syringe_pump.set_speed(self.final_push_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)	
		else:
			first_push_volume = fill_volume - self.slow_push_volume  #  calculate first push volume

			iteration = int(first_push_volume / self.full_stroke)
			remainder = int(first_push_volume - (iteration * self.full_stroke))

			for i in range(0, iteration):

				self.syringe_pump.set_speed(from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(self.full_stroke)

				self.syringe_pump.set_speed(to_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)

			if remainder != 0:
	                
				self.syringe_pump.set_speed(from_speed)  # draw remainder into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(remainder)

				self.syringe_pump.set_speed(to_speed)  # transfer remainder fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)

				# Slow push in to aviod air gaps

				self.syringe_pump.set_speed(from_speed)  # draw into syringe
				self.syringe_pump.set_valve_position(from_port)
				self.syringe_pump.set_absolute_volume(self.slow_push_volume)

				self.syringe_pump.set_speed(self.final_push_speed)  # transfer fluid through 'to_port'
				self.syringe_pump.set_valve_position(to_port)
				self.syringe_pump.set_absolute_volume(0)

#----------------------------- Air gap drawing to syringe ------------------------------

	def draw_air_to_syringe(self):
		"Draws a specific volume of air gap to syringe port-9."

		self.logging.info("%i\t--> START: Draw air gap to syringe port-9: [%s]" % (self.cycle, self.state))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_air.wav')

		self.logging.info("%i\t--> Push %i ul air gap just passed syringe port-9" % (self.cycle, self.air_gap))
		self.move_reagent(self.air_gap, self.load_speed, 8, self.reagent_speed, 9)  # push air gap just passed syringe port-9
		self.logging.info("%i\t--> END: Drawn air gap to syringe port-9: [%s]" % (self.cycle, self.state))

#------------------------------- Draw reagent into flowcell ----------------------------

	def push_into_flowcell(self, reagent_number, centering_volume):
		"Pushes reagent into flowcell assuming reagent is already in inlet tube with air gap behind."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/flowcell_filling.wav')

		push_volume = (self.syringe_port9_to_FC_inlet + self.dead_volume) - (centering_volume + self.air_gap)  # calculate volume required to push reagent into flowcell

		self.logging.info("%i\t--> START: Push reagent into flowcell with %i ul follow up fluid: [%s]" % (self.cycle, push_volume, self.state))
		self.move_reagent(push_volume, self.clean_speed, reagent_number, self.reagent_speed, 9)  # draw follow up fluid into syringe then push reagent into flowcell with it
		self.logging.info("%i\t--> END: Push reagent into flowcell with %i ul follow up fluid: [%s]" % (self.cycle, push_volume, self.state))

#---------------------------- Reagent-to-syringe path filling --------------------------

	def fill_reagent_path(self, reagent_number, syringe_speed=None):
		"Fills reagent-to-syringe path with pre-loaded fluid and dumps tube content to syringe waste."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/fill_reagent_path_' + str(reagent_number) + '.wav')

		self.logging.info("%i\t--> START: Fill reagent-to-syringe path %i: [%s]" % (self.cycle, reagent_number, self.state))

		if syringe_speed is None:
			syringe_speed = self.reagent_speed  # if no argument given, use reagent speed

		key_1 = 'Reagent ' + str(reagent_number)
		key_2 = 'Syringe Pump ' + str(reagent_number) 
		total_volume = self.e_volumes[key_1][key_2] + self.dead_volume

		self.logging.info("%i\t--> Draw %i ul fluid up to syringe port %i and eject tube content to syringe waste" % (self.cycle, total_volume, reagent_number))
		self.move_reagent(total_volume, syringe_speed, reagent_number, self.clean_speed, 7)  # draw fluid up to syringe port i and eject tube content to syringe waste
		self.logging.info("%i\t--> END: Filled reagent-to-syringe path %i: [%s]" % (self.cycle, reagent_number, self.state))

#------------------------------ Push reagent back to chamber ---------------------------

	def push_reagent_back(self, reagent_number, syringe_speed=None):
		"Pushes reagent back into cooled reagent chamber with air from reagent-to-syringe path."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/push_reagent_back_' + str(reagent_number) + '.wav')

		self.logging.info("%i\t--> START: Push reagent %i back to chamber: [%s]" % (self.cycle, reagent_number, self.state))

		if syringe_speed is None:
			syringe_speed = self.load_speed  # if no argument given, use reagent speed

		key_1 = 'Reagent ' + str(reagent_number)
		key_2 = 'Syringe Pump ' + str(reagent_number) 
		total_volume = self.e_volumes[key_1][key_2] + self.dead_volume

		self.logging.info("%i\t--> Push %i ul fluid back to reagent chamber %i with air" % (self.cycle, total_volume, reagent_number))
		self.move_reagent(total_volume + 10, self.load_speed, 8, syringe_speed, reagent_number)  # push fluid back to reagent chamber i with air

		self.logging.info("%i\t--> END: Push reagent %i back to chamber: [%s]" % (self.cycle, reagent_number, self.state))

#-------------------------------- Collect sample into tube -----------------------------

	def collect_sample(self):
		"Collects DNA sample into tube assuming air gap behind."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/collect_sample.wav')

		push_volume = self.FC_outlet_to_waste + self.incorporation_volume + 25  # calculate volume required to push reagent into tube

		self.logging.info("%i\t--> START: Collect DNA sample into tube with %i ul follow up air: [%s]" % (self.cycle, push_volume, self.state))
		self.move_reagent(push_volume, self.clean_speed, 8, self.reagent_speed, 9)  # draw air into syringe then push reagent into tube with it
		self.logging.info("%i\t--> END: Collect DNA sample into tube with %i ul follow up air: [%s]" % (self.cycle, push_volume, self.state))

#------------------------- Incubate and count elapsed time ----------------------------

	def incubate_reagent(self, time_m):
		"""Incubates reagent for given amount of time and dynamically counts elapsed time 
		in seconds to update user about incubation state."""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/incubation_start.wav')

		self.logging.info("%i\t--> START: Incubate reagent for %i min: [%s]" % (self.cycle, time_m, self.state))
		incubation_time = time_m * 60  # incubation time in seconds

		for tc in range(0, incubation_time):

			time.sleep(1)
			sys.stdout.write('TIME\t -\t--> Elapsed time: ' + str(tc) + ' of ' + str(incubation_time) + ' seconds\r')
			sys.stdout.flush()

		print '\n'

		self.logging.info("%i\t--> END: Incubated reagent: [%s]" % (self.cycle, self.state))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/incubation_end.wav')

#--------------------------------------------------------------------------------------# 
# 			       ELEMENTARY CLEANING ROUTINES    			       # 
#--------------------------------------------------------------------------------------#

#---------------------------- Reagent-to-syringe path cleaning --------------------------

	def clean_reagent_path(self, reagent_number, iteration):
		"Cleans reagent-to-syringe path with pre-loaded fluid and dumps tube content to syringe waste n-times."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/clean_reagent_path.wav')

		self.logging.info("%i\t--> START: Clean reagent-to-syringe path %i: [%s]" % (self.cycle, reagent_number, self.state))

		for n in range(0, iteration):
			self.fill_reagent_path(reagent_number, self.clean_speed)  # clean reagent-to-syringe path n-times

		self.logging.info("%i\t--> END: Cleaned reagent-to-syringe path %i: [%s]" % (self.cycle, reagent_number, self.state))

#-------------------------------- Syringe pump cleaning --------------------------------

	def clean_syringe_pump(self, iteration):
		"Fills syringe pump with reagent 'Wash 1' and dumps content to syringe waste n-times."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/clean_syringe.wav')

		self.logging.info("%i\t--> START: Clean syringe pump: [%s]" % (self.cycle, self.state))
		self.logging.info("%i\t--> Draw %i ul reagent 'Wash 1' up into syringe pump and eject content to syringe waste" % (self.cycle, self.clean_stroke))

		for n in range(0, iteration):
			self.move_reagent(self.clean_stroke, self.clean_speed, 5, self.clean_speed, 7)  # draw reagent 'Wash 1' into syringe pump and eject tube content to syringe waste

		self.logging.info("%i\t--> END: Cleaned syringe pump: [%s]" % (self.cycle, self.state))

#---------------------------------- Flowcell cleaning ----------------------------------

	def clean_flowcell(self, reagent_number, iteration):
		"Cleans flowcell with reagent (Wash 1/2) and dumps previous tube content to flowcell waste n-times."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/clean_flowcell.wav')

    		if reagent_number == 5:
			reagent_name = "'Wash 1'"
		elif reagent_number == 6:
			reagent_name = "'Wash 2'"
		else:
			reagent_name = "reagent"

		self.logging.info("%i\t--> START: Clean flowcell: [%s]" % (self.cycle, self.state))
		self.logging.info("%i\t--> Draw %i ul %s up to flush flowcell %i time(s)" % (self.cycle, self.clean_stroke, reagent_name, iteration))

		for n in range(0, iteration):
			self.move_reagent(self.clean_stroke, self.clean_speed, reagent_number, self.empty_speed, 9)  # draw reagent (Wash 1/2) up to flush flowcell once, and eject tube content to flowcell waste

		self.logging.info("%i\t--> END: Cleaned flowcell: [%s]" % (self.cycle, self.state))

#-------------------------- Complete flowcell/syringe pump cleaning --------------------

	def clean_flowcell_and_syringe(self, iteration):
		"""Cleans flowcell and syringe pump completely with 'Wash 1', making sure that there is no left
		over reagent leading to or in the syringe pump after a biochemistry step. This function also
		flushes the flowcell, thus incorporates the 'clean_flowcell' procedure inherently."""

		self.logging.info("%i\t--> START: Clean flowcell and syringe pump" % (self.cycle))

		self.clean_flowcell(5, iteration)   # first cleans flowcell with 'Wash 1' n-times
		self.clean_syringe_pump(iteration)  # finally cleans syringe pump with 'Wash 1' n-times as well

		self.logging.info("%i\t--> END: Cleaned flowcell and syringe pump" % (self.cycle))

#------------------------------ Fluidic sub-system cleaning ----------------------------

	def clean_fluidics_system(self, iteration):
		"""Cleans all fluid lines, flowcell and syringe pump with 'Wash 1'. Assumes
		that all reagent chambers are filled with 'Wash 1'."""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/clean_system.wav')

		self.logging.info("%i\t--> START: Clean fluidics system: [%s]" % (self.cycle, self.state))

		for n in range(0, 6):
			self.clean_reagent_path(n+1, iteration)  # clean all reagent paths with 'Wash 1' i-times

		self.clean_flowcell_and_syringe(iteration)       # clean flowcell and syringe pump completely with 'Wash 1' i-times
		self.logging.info("%i\t--> END: Cleaned fluidics system: [%s]" % (self.cycle, self.state))

#------------------------------- Trapped bubble clearing -------------------------------

	def clear_bubbles(self, iteration):
		"Clears bubbles trapped in flowcell with high flow rate 'Wash 1' n-times."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/clear_bubbles.wav')

		self.logging.info("%i\t--> START: Clear bubbles: [%s]" % (self.cycle, self.state))

		self.logging.info("%i\t--> Clear bubbles with high flow rate %i ul 'Wash 1'" % (self.cycle, self.full_stroke))

		for n in range(0, iteration):
			self.move_reagent(self.full_stroke, 15, 5, 0, 9)  # draw 1000 ul 'Wash 1' into syringe pump and clear bubbles with it trapped in flowcell

		self.logging.info("%i\t--> END: Cleared bubbles: [%s]" % (self.cycle, self.state))

#--------------------------------------------------------------------------------------# 
# 				    PRIMING FUNCTIONS     			       # 
#--------------------------------------------------------------------------------------#

#--------------------------------- Prime reagent paths ---------------------------------

	def prime_reagent_paths(self):
		"""Primes reagent paths, such that reagents - not containing enzyme - end 
		up in syringe port start positions."""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/prime_reagent_paths.wav')

		self.logging.info("%i\t--> START: Prime reagent-to-syringe paths: [%s]" % (self.cycle, self.state))

		for n in [1, 5, 6]:
			self.fill_reagent_path(n, self.clean_speed)  # prime reagent-to-syringe path

		self.logging.info("%i\t--> END: Primed reagent-to-syringe paths: [%s]" % (self.cycle, self.state))

#--------------------------------- Priming syringe pump --------------------------------

	def prime_syringe_pump(self):
		"Primes syringe pump with 'Wash 1' as initialization step."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/prime_syringe.wav')

		self.logging.info("%i\t--> START: Prime syringe pump: [%s]" % (self.cycle, self.state))
		self.clean_syringe_pump(1)  # clean syringe pump with 'Wash 1' once
		self.logging.info("%i\t--> END: Primed syringe pump: [%s]" % (self.cycle, self.state))

#----------------------------------- Priming flowcell ----------------------------------

	def prime_flowcell(self):
		"Primes flowcell with 'Wash 1' as initialization step."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/prime_flowcell.wav')

		self.logging.info("%i\t--> START: Prime flowcell: [%s]" % (self.cycle, self.state))
		self.clean_flowcell(5, 1)  # clean flowcell with 'Wash 1' once
		self.logging.info("%i\t--> END: Primed flowcell: [%s]" % (self.cycle, self.state))

#------------------------------ Fluidic sub-system priming -----------------------------

	def prime_fluidics_system(self):
		"""Primes TCEP, SPSC and Thermo Pol-II buffer fluid lines with reagents;
		flowcell and syringe pump with 'Wash 1'. Assumes that reagent chambers are 
		filled with appropriate reagents."""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../speech/priming_system.wav')

		self.logging.info("%i\t--> START: Prime fluidics system: [%s]" % (self.cycle, self.state))

		self.prime_reagent_paths()  # prime reagent paths (not containing enzyme) with reagents
		self.prime_flowcell()       # prime flowcell with 'Wash 1'
		self.prime_syringe_pump()   # prime syringe pump with 'Wash 1'

		self.logging.info("%i\t--> END: Primed fluidics system: [%s]" % (self.cycle, self.state))

#--------------------------------------------------------------------------------------# 
# 				INITIALIZATION FUNCTIONS 			       # 
#--------------------------------------------------------------------------------------#

#-------------------------- Syringe pump initialization -------------------------------

	def syringe_pump_init(self):
		"Initializes syringe pump by moving it to zero position and setting speed to 20."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/initialize_syringe.wav')

		self.logging.info("%i\t--> START: Initialize syringe pump: [%s]" % (self.cycle, self.state))
		self.syringe_pump.initialize_syringe()  # initialize syringe pump
		self.logging.info("%i\t--> END: Initialized syringe pump with default operation settings: [%s]" % (self.cycle, self.state))

#--------------------------- Biochemistry initialization -------------------------------

	def init(self):
		"Initialize biochemistry sub-system."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/initialize_system_start.wav')

		t0 = time.time()  # get current time
		self.state = 'initialization' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		self.syringe_pump_init()  # initialize syringe pump
		self.prime_fluidics_system()  # draw reagents up to start positions, flush flowcell and clean syringe pump with 'Wash 1' as initialization step

		delta = (time.time() - t0) / 60	 # calculate elapsed time for incorporation
		self.logging.warn("%i\t--> Finished system initialization - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/initialize_system_end.wav')

#---------------------------- Biochemistry finalization --------------------------------

	def finish(self):
		"Finalize biochemistry sub-system."

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/finalize_system_start.wav')

		t0 = time.time()  # get current time
		self.state = 'finalization' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		self.push_reagent_back(1)  # push cleavage solution back into reagent chamber 
		self.push_reagent_back(5)  # push 'Wash 1' back into reagent chamber 
		self.push_reagent_back(6)  # push 'Wash 2' back into reagent chamber 

		delta = (time.time() - t0) / 60	 # calculate elapsed time for incorporation
		self.logging.warn("%i\t--> Finished system finalization - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/finalize_system_end.wav')

#--------------------------------------------------------------------------------------# 
# 				 BIOCHEMISTRY FUNCTIONS 			       # 
#--------------------------------------------------------------------------------------#

#---------------------------------- Pre_washing sub. -----------------------------------

	def pre_washing(self):
		"""Runs pre-washing protocol for SBS sequencing. Does the following:

		- clean flowcell with 'Wash 1' 2-times [SPSC, a soap]
		- clean flowcell with 'Wash 2' 2-times [Thermo Pol-II buffer (1X cc.), prepares DNA]
		- incubate 'Wash 2' in FC at 55C for 2 minutes

		Reagent requirements:

		- port-5 : 400 ul 'Wash 1'
		- port-6 : 400 ul 'Wash 2'"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/pre_washing_start.wav')

		t0 = time.time()  # get current time
		self.state = 'pre_washing' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		self.clean_flowcell(5, 2)   # clean flowcell with 'Wash 1' 2-times
		self.clean_flowcell(6, 2)   # clean flowcell with 'Wash 2' 2-times
		self.incubate_reagent(self.preparation_time)  # incubate reagent for 2 min

		delta = (time.time() - t0) / 60	 # calculate elapsed time for incorporation
		self.logging.warn("%i\t--> Finished pre-washing protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/pre_washing_end.wav')

#--------------------------------- Incorporation sub. ----------------------------------

	def incorporation(self):
		"""Runs incorporation protocol for SBS sequencing. Does the following:

		- incorporate modified nucleotide using 9N enzyme as catalyst
		- incubate reaction mix at 55C for 20 minutes
		- clean flowcell with 'Wash 2' 2-times

		Reagent requirements:

		- port-2 : 30 ul incorporation mix (dNTP, N3-dNTP, buffer, Mn, 9N)
		- port-6 : 400 ul 'Wash 2'"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/incorporation_start.wav')

		t0 = time.time()  # get current time
		self.state = 'incorporation' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))
		self.fill_reagent_path(2, self.load_speed)  # prime reagent-to-syringe path 2 with incorporation mix
		self.draw_air_to_syringe()  # draw air to syringe port-9

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_incorporation_mix.wav')

		self.logging.info("%i\t--> Draw %i ul incorporation mix into system from syringe port-2" % (self.cycle, self.incorporation_volume))
		self.move_reagent(self.incorporation_volume, self.load_speed, 2, self.reagent_speed, 9) # draw incorporation mix into system from syringe port-2
		self.push_reagent_back(2)  # push incorporation mix back into reagent chamber 

		cv = self.gap_volume(self.incorporation_volume) # calculate centering volume required
		self.draw_air_to_syringe()  # draw air to syringe port-9
		self.push_into_flowcell(6, cv)  # push incorporation mix into flowcell followed by "Wash 2"
		self.incubate_reagent(self.incorporation_time)  # incubate reagent for 15 min
		self.clean_flowcell(6, 2)  # clean flowcell with 'Wash 2' 2-times

		delta = (time.time() - t0) / 60	 # calculate elapsed time for incorporation
		self.logging.warn("%i\t--> Finished incorporation protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/incorporation_end.wav')

#-----------------------------  Test_incorporation sub. --------------------------------

	def test_incorporation(self):
		"""Runs test incorporation protocol for SBS sequencing. Does the following:

		- incorporate modified nucleotide using 9N enzyme as catalyst
		- incubate reaction mix at 60C for 20 minutes

		Reagent requirements:

		- port-2 : 30 ul incorporation mix (dNTP, N3-dNTP, buffer, Mn, 9N)"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/test_incorporation_start.wav')

		t0 = time.time()  # get current time
		self.state = 'test_incorporation' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))
		self.fill_reagent_path(2, self.load_speed)  # prime reagent-to-syringe path 2 with incorporation mix
		self.draw_air_to_syringe()  # draw air to syringe port-9

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_incorporation_mix.wav')

		self.logging.info("%i\t--> Draw %i ul incorporation mix into system from syringe port-2" % (self.cycle, self.incorporation_volume))
		self.move_reagent(self.incorporation_volume, self.load_speed, 2, self.reagent_speed, 9) # draw incorporation mix into system from syringe port-2
		self.push_reagent_back(2)  # push incorporation mix back into reagent chamber 

		cv = self.gap_volume(self.incorporation_volume) # calculate centering volume required
		self.draw_air_to_syringe()  # draw air to syringe port-9
		self.push_into_flowcell(5, cv)  # push incorporation mix into flowcell followed by "Wash 1"
		self.incubate_reagent(self.incorporation_time)  # incubate reagent for 20 min

		delta = (time.time() - t0) / 60	 # calculate elapsed time for incorporation
		self.logging.warn("%i\t--> Finished incorporation test protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/test_incorporation_end.wav')

#----------------------------------  Capping-1 sub. ------------------------------------

	def capping_1(self):
		"""Runs capping-1 protocol to reduce the amount of unextended priming 
		strands and thus negate any lagging fluorescent signal for SBS sequencing. 
		Does the following:

		- synchronize incorporation with N3-dNTPs in relatively high concentration using 9N enzyme as catalyst
		- incubate reaction mix at 55C for 25 minutes
		- clean flowcell with 'Wash 2' 2-times

		Reagent requirements:

		- port-3 : 30 ul capping-1 reaction mix (N3-dNTP, buffer, Mn, 9N)
		- port-6 : 400 ul 'Wash 2'"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/capping_1_start.wav')

		t0 = time.time()  # get current time
		self.state = 'capping-1' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))
		self.fill_reagent_path(3, self.load_speed)  # prime reagent-to-syringe path 3 with capping-1 mix
		self.draw_air_to_syringe()  # draw air to syringe port-9

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_capping1_mix.wav')

		self.logging.info("%i\t--> Draw %i ul capping-1 mix into system from syringe port-3" % (self.cycle, self.capping1_volume))
		self.move_reagent(self.capping1_volume, self.load_speed, 3, self.reagent_speed, 9) # draw capping-1 mix into system from syringe port-3
		self.push_reagent_back(3)  # push capping-1 mix back into reagent chamber 

		cv = self.gap_volume(self.capping1_volume) # calculate centering volume required
		self.draw_air_to_syringe()  # draw air to syringe port-9
		self.push_into_flowcell(6, cv)  # push capping-1 mix into flowcell followed by "Wash 2"
		self.incubate_reagent(self.capping1_time)  # incubate reagent for 25 min
		self.clean_flowcell(6, 2)  # clean flowcell with 'Wash 2' 2-times

		delta = (time.time() - t0) / 60	 # calculate elapsed time for capping-1
		self.logging.warn("%i\t--> Finished capping-1 protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/capping_1_end.wav')

#----------------------------------  Capping-2 sub. ------------------------------------

	def capping_2(self):
		"""Runs capping-2 protocol to permanently terminate any ill-terminated 
		priming strands and thus eliminates them from subsequent polymerase 
		reaction cycles. Does the following:

		- permanently terminate incorporation with ddNTPs using 9N enzyme as catalyst
		- incubate reaction mix at 55C for 5 minutes
		- clean flowcell and syringe with 'Wash 1' 2-times

		Reagent requirements:

		- port-4 : 30 ul capping-2 reaction mix (ddNTP, buffer, Mn, 9N)
		- port-5 : 800 ul 'Wash 1'"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/capping_2_start.wav')

		t0 = time.time()  # get current time
		self.state = 'capping-2' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))
		self.fill_reagent_path(4, self.load_speed)  # prime reagent-to-syringe path 4 with capping-2 mix
		self.draw_air_to_syringe()  # draw air to syringe port-9

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_capping2_mix.wav')

		self.logging.info("%i\t--> Draw %i ul capping-2 mix into system from syringe port-4" % (self.cycle, self.capping1_volume))
		self.move_reagent(self.capping1_volume, self.load_speed, 4, self.reagent_speed, 9) # draw capping-2 mix into system from syringe port-4
		self.push_reagent_back(4)  # push capping-2 mix back into reagent chamber 

		cv = self.gap_volume(self.capping2_volume) # calculate centering volume required
		self.draw_air_to_syringe()  # draw air to syringe port-9
		self.push_into_flowcell(5, cv)  # push capping-2 mix into flowcell followed by "Wash 1"
		self.incubate_reagent(self.capping2_time)  # incubate reagent for 5 min
		self.clean_flowcell_and_syringe(2)  # clean flowcell and syringe with 'Wash 1' 2-times

		delta = (time.time() - t0) / 60	 # calculate elapsed time for capping-2
		self.logging.warn("%i\t--> Finished capping-2 protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/capping_2_end.wav')

#----------------------------------- Cleavage sub. -------------------------------------

	def cleavage(self):
		"""Runs cleavage protocol to remove both ddNTPs and 3'-OH capping groups with
		TCEP solution, which prepares the DNA chain for the next nucleotide incorporation 
		event. Does the following:

		- cleave ddNTPs and 3'-OH capping groups with TCEP breaking disulfide bonds
		- incubate reaction mix at 55C for 15 minutes
		- clean flowcell and syringe with 'Wash 1' 4-times

		Reagent requirements:

		- port-1 : 100 = 2*50 ul TCEP solution
		- port-5 : 800 = 4*200 ul 'Wash 1'"""

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/cleavage_start.wav')

		t0 = time.time()  # get current time
		self.state = 'cleavage' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		for n in range(0, self.cleavage_iter):  # recall cleavage iteration number configuration parameter

			if self.speech_option == 1:
				commands.getstatusoutput('mplayer -ao pulse ../../../speech/cleavage_iteration_' + str(n+1) + '.wav')

			self.logging.info("%i\t--> Cleavage iteration: %i" % (self.cycle, n+1))
			self.draw_air_to_syringe()  # draw air to syringe port-9

			if self.speech_option == 1:
				commands.getstatusoutput('mplayer -ao pulse ../../../speech/draw_cleavage_solution.wav')

			self.logging.info("%i\t--> Draw %i ul TCEP solution into system from syringe port-1" % (self.cycle, self.cleavage_volume))
			self.move_reagent(self.cleavage_volume, self.load_speed, 1, self.reagent_speed, 9) # draw TCEP solution into system from syringe port-1
			cv = self.gap_volume(self.cleavage_volume) # calculate centering volume required

			self.draw_air_to_syringe()  # draw air to syringe port-9
			self.push_into_flowcell(5, cv)  # push TCEP solution into flowcell followed by "Wash 1"
			self.incubate_reagent(self.cleavage_time)  # incubate reagent for 15 min

		self.clean_flowcell(5, 4)  # clean flowcell with 'Wash 1' 4-times

		delta = (time.time() - t0) / 60  # calculate elapsed time for cleavage
		self.logging.warn("%i\t--> Finished cleavage protocol - duration: %0.2f minutes\n" % (self.cycle, delta))

		if self.speech_option == 1:
			commands.getstatusoutput('mplayer -ao pulse ../../../speech/cleavage_end.wav')

#--------------------------------------------------------------------------------------# 
# 				 WALKING ALGORTIHMS 				       # 
#--------------------------------------------------------------------------------------#

#------------------------------- Primer_walking sub. -----------------------------------

	def primer_walking(self):
		"""Performs a cycle of primer walking biochemistry consisting of:

		- incorporation using SBS protocol
		- capping-1 to ensure synchronized query base termination points
		- capping-2 to eliminate all ill-terminated priming strands
		- cleavage to prepare DNA for next incorporation event using TCEP

		Reagent requirements:

		- port-1 : 100 ul TCEP solution
		- port-2 : 30 ul incorporation mix (dNTP, N3-dNTP, buffer, Mn, 9N)
		- port-3 : 30 ul capping-1 reaction mix (N3-dNTP, buffer, Mn, 9N)
		- port-4 : 30 ul capping-2 reaction mix (ddNTP, buffer, Mn, 9N)
		- port-5 : 3200 ul 'Wash 1'
		- port-6 : 1200 ul 'Wash 2'"""

		t0 = time.time()  # get current time
		self.state = 'primer_walking' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))
		
		self.pre_washing()  # perform primer walking biochemistry
		self.incorporation()  
		self.capping_1()
		self.capping_2()
		self.cleavage()

		delta = (time.time() - t0) / 60  # calculate elapsed time for primer walking
		self.logging.warn("%i\t--> Finished primer walking cycle - duration: %0.2f minutes" % (self.cycle, delta))

#--------------------------------- Test_walking sub. -----------------------------------

	def test_walking(self):
		"""Performs a cycle of primer walking biochemistry testing consisting of:

		- incorporation using cheap SBS protocol
		- collection of sample into tube

		Reagent requirements:

		- port-2 : 30 ul incorporation mix (dNTP, N3-dNTP, buffer, Mn, 9N)"""

		t0 = time.time()  # get current time
		self.state = 'test_walking' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		self.fill_reagent_path(2)  # perform primer walking biochemistry testing
		self.test_incorporation()
		self.collect_sample()

		delta = (time.time() - t0) / 60  # calculate elapsed time for primer walking
		self.logging.warn("%i\t--> Finished primer walking testing - duration: %0.2f minutes" % (self.cycle, delta))

#------------------------------ Fluor_incorporation sub. -------------------------------

	def fluor_incorporation(self):
		"""Performs a cycle of primer walking biochemistry testing consisting of:

		- pre-washing for SBS sequencing
		- incorporate fluorescently labeled modified nucleotides 
		- clean flowcell and syringe thoroughly with SPSC 

		Reagent requirements:

		- port-2 : 30 ul incorporation mix (N3-dNTP, N3-dNTP-N3-dyes, buffer, Mn, 9N)"""

		t0 = time.time()  # get current time
		self.state = 'fluor_incorporation' # update function state of biochemistry object

		self.logging.info("%i\t--> In %s subroutine" % (self.cycle, self.state))

		self.pre_washing()  # perform primer walking biochemistry testing
		self.test_incorporation()
		self.clean_flowcell_and_syringe(2)  

		delta = (time.time() - t0) / 60  # calculate elapsed time for primer walking
		self.logging.warn("%i\t--> Finished fluor incorporation testing - duration: %0.2f minutes" % (self.cycle, delta))

#------------------------------------- Run sub. ----------------------------------------

	def run(self):
		"""Runs primer walking cycle(s) based on the desired iteration number
		already contained in biochemistry object as configuration parameter."""

		time.sleep(1)
		self.state = 'running'  # update function state of biochemistry object

		#----------------------- Flowcell preparation ----------------------------------

		print "\n--> Cycle: %i\n" % self.cycle 

		if self.cycle == 1:
			self.init()  # initialize biochemistry sub-system only once at the beginning (iteration 1)
			self.primer_walking()  # perform primer walking on query base 
		else:
			self.primer_walking()  # perform primer walking on query base 

