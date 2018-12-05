#!/usr/local/bin/python

"""
-------------------------------------------------------------------------------- 
 Author: Mirko Palla.
 Date: August 25, 2009.

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
     *                                                                    *      
     *            WELCOME TO THE BIOCHEMISTRY UTILITY PROGRAM             *
     *                                                                    *
     *            Usage: python biochem_utils.py [method-name]	          *
     *                                                                    *
     **********************************************************************

     |  Methods defined here:
     |  
     |  __init__(self, cycle_number, logger)
     |      Initialize biochemistry object with default parameters
     |  
     |  capping_1(self)
     |	    Runs capping-1 protocol to reduce the amount of unextended priming 
     |	    strands and thus negate any lagging fluorescent signal for SBS sequencing. 
     |
     |  capping_2(self)
     |	    Runs capping-2 protocol to permanently terminate any ill-terminated 
     |      priming strands and thus eliminates them from subsequent polymerase 
     |	    reaction cycles.
     |
     |  clean_flowcell(self, reagent_number, iteration)
     |      Cleans flowcell with dH2O and dumps previous tube content to flowcell waste n-times.
     |  
     |  clean_flowcell_and_syringe(self, iteration)
     |      Cleans flowcell and syringe pump completely with dH2O, making sure that there is no left
     |      over reagent leading to or in the syringe pump after a biochemistry step. This function also
     |      flushes the flowcell, thus incorporates the 'clean_flowcell' procedure inherently.
     |
     |  clean_fluidics_system(self, iteration)
     |      Cleans all fluid lines, flowcell and syringe pump with dH2O. Assumes
     |      that all reagent chambers are filled with dH2O.
     |  
     |  clean_reagent_path(self, reagent_number, iteration)
     |      Cleans reagent-to-syringe path with pre-loaded fluid and dumps tube content to syringe waste n-times.
     |  
     |  clean_syringe_pump(self, iteration)
     |      Fills syringe pump with dH2O and dumps content to syringe waste n-times.
     |
     | 	clear_bubbles(self, iteration)
     |      Clears bubbles trapped in flowcell with high flow rate 'Wash 1' n-times.
     |
     |	cleavage(self)
     |	     Runs cleavage protocol to remove both ddNTPs and 3'-OH capping groups with
     |       TCEP solution, which prepares the DNA chain for the next nucleotide incorporation 
     |	     event.
     |
     |  collect_sample(self)
     |	    Collects DNA sample into tube assuming air gap behind.
     |  
     |  draw_air_to_syringe(self)
     |      Draws a specific volume of air gap to syringe port-9.
     |  
     |  fill_reagent_path(self, reagent_number, syringe_speed=None)
     |      Fills reagent-to-syringe path with pre-loaded fluid and dumps tube content to syringe waste.
     |
     |  finish(self):
     |	    Finalize biochemistry sub-system.
     |
     |  fluor_incorporation(self):
     |      Performs a cycle of primer walking biochemistry testing consisting of:
     |
     |	    - pre-washing for SBS sequencing
     |      - incorporate fluorescently labeled modified nucleotides 
     |	    - clean flowcell and syringe thoroughly with SPSC 
     |
     |  incorporation(self)
     |      Runs incorporation protocol for SBS sequencing.
     |
     |  incubate_reagent(self, time_m)
     |      Incubates reagent for given amount of time and dynamically counts elapsed time 
     |      in seconds to update user about incubation state.
     |  
     |  init(self)
     |      Initialize biochemistry sub-system.
     |  
     |  move_reagent(self, fill_volume, from_speed, from_port, to_speed, to_port)
     |      Moves a given volume of reagent [1] into syringe at speed [2] through specified valve
     |      position [3], then transfers syringe content through valve position [4] into an other
     |      location in the fluidic system. All parameters are integers respectively.
     |  
     |  move_reagent_slow(self, fill_volume, from_speed, from_port, to_speed, to_port)
     |      Moves a given volume of reagent [1] into syringe at speed [2] through specified valve
     |      position [3], then transfers syringe content through valve position [4] into an other
     |      location in the fluidic system. The last 100 ul reagent is drawn into the flowcell with 
     |      slower speed to avoid air bubble build up in the chambers. All parameters are integers 
     |      respectively.
     |
     |	pre_washing(self)
     |	    Runs pre-washing protocol for SBS sequencing.
     |  
     |  prime_flowcell(self)
     |      Primes flowcell with dH2O as initialization step.
     |  
     |  prime_fluidics_system(self)
     |      Primes all fluid lines with reagents, flowcell and syringe pump with dH2O. 
     |	    Assumes that all reagent chambers are filled with appropriate reagents.
     |  
     |  prime_reagent_paths(self)
     |      Primes reagent paths, such that reagents end up in syringe port start positions.
     |  
     |  prime_syringe_pump(self)
     |      Primes syringe pump with dH2O as initialization step.
     |
     |  primer_walking(self)
     |      Performs a cycle of primer walking biochemistry consisting of:     
     |
     |      - incorporation using SBS protocol
     |      - capping-1 to ensure synchronized query base termination points
     |	    - capping-2 to eliminate all ill-terminated priming strands
     |      - cleavage to prepare DNA for next incorporation event using TCEP
     |  
     |  push_into_flowcell(self, reagent_number, centering_volume)
     |      Pushes reagent into flowcell assuming reagent is already in inlet tube with air gap behind.
     |
     | 	push_reagent_back(self, reagent_number, syringe_speed=None):
     |	    Pushes reagent back into cooled reagent chamber with air from reagent-to-syringe path.
     |
     |	run(self)
     |	    Runs primer walking cycle(s) based on the desired iteration number
     |	    already contained in biochemistry object as configuration parameter.
     |
     |  syringe_pump_init(self)
     |      Initializes syringe pump by moving it to zero position and setting speed to 20.
     |
     | 	test_incorporation(self)
     |	    Runs test incorporation protocol for SBS sequencing. Does the following:
     |
     |	    - incorporate modified nucleotide using 9N enzyme as catalyst
     |	    - incubate reaction mix at 60C for 20 minutes
     |
     |	test_walking(self)
     |	    Performs a cycle of primer walking biochemistry testing.\n\n"""

	sys.exit()

elif len(sys.argv) < 2:
	print '\n--> Error: not correct input!\n--> Usage: python biochem_utils.py [method-name]\n'
	sys.exit()

else:

	import ConfigParser					# Import configuration parser class.
	from logger import Logger				# Import logger class.
	from biochem import Biochem				# Import biochecmistry class.

	#--------------------- Walkameter fluidics sub-system initialization -------------------

	config = ConfigParser.ConfigParser()
	config.readfp(open('config.txt'))

	t0 = time.time()                # get current time
	print '\n'
	logger = Logger(config)         # initialize logger object

	biochem = Biochem(logger)  # Initialize biochemistry object: cycle-number need to be passed.

	#---------------------------------------------------------------------------------------
	#				FLUIDICS SUB-SYSTEM FUNCTIONS
	#---------------------------------------------------------------------------------------

	logger.info('*\t--> Started %s method execution - biochem_utils.py' % sys.argv[1])

	method = (sys.argv[1])  # assign name of requested method

	if method == 'capping_1':
		biochem.capping_1()

	elif method == 'capping_2':
		biochem.capping_2()

	elif method == 'clean_flowcell':
		print "INFO\t *\t--> Please, enter reagent and cleaning iteration numbers separated by single space [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.clean_flowcell(int(v[0]), int(v[1]))

	elif method == 'clean_flowcell_and_syringe':
		print "INFO\t *\t--> Please, enter the number of cleaning iterations [integer]: ",
		iteration = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing newline character
		biochem.clean_flowcell_and_syringe(iteration)

	elif method == 'clean_fluidics_system':
		print "INFO\t *\t--> Please, enter the number of cleaning iterations [integer]: ",
		iteration = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing newline character
		biochem.clean_fluidics_system(iteration)

	elif method == 'clean_reagent_path':
		print "INFO\t *\t--> Please, enter: reagent and iteration numbers separated by single space [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.clean_reagent_path(int(v[0]), int(v[1]))

	elif method == 'clean_syringe_pump':
		print "INFO\t *\t--> Please, enter the number of cleaning iterations [integer]: ",
		iteration = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing newline character
		biochem.clean_syringe_pump(iteration)

	elif method == 'clear_bubbles':
		print "INFO\t *\t--> Please, enter the number of bubble clearing iterations [integer]: ",
		iteration = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing newline character
		biochem.clear_bubbles(iteration)

	elif method == 'cleavage':
		biochem.cleavage()

	elif method == 'collect_sample':
		biochem.collect_sample()

	elif method == 'draw_air_to_syringe':
		biochem.draw_air_to_syringe()

	elif method == 'fill_reagent_path':
		print "INFO\t *\t--> Please, enter the number of reagent-to-syringe path and syringe speed [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.push_into_flowcell(int(v[0]), int(v[1]))

	elif method == 'finish':
		biochem.finish()

	elif method == 'fluor_incorporation':
		biochem.fluor_incorporation()

	elif method == 'incorporation':
		biochem.incorporation()

	elif method == 'incubate_reagent':
		print "INFO\t *\t--> Please, enter incubation time in minutes [integer]: ",
		time_m = int(sys.stdin.readline().strip())  # use stdin explicitly and remove trailing newline character
		biochem.incubate_reagent(time_m)

	elif method == 'init':
		biochem.init()

	elif method == 'move_reagent':
		print "INFO\t *\t--> Please, enter: fill_volume, from_speed, from_port, to_speed, to_port separated by single space [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.move_reagent(int(v[0]), int(v[1]), int(v[2]), int(v[3]), int(v[4]))

	elif method == 'move_reagent_slow':
		print "INFO\t *\t--> Please, enter: fill_volume, from_speed, from_port, to_speed, to_port separated by single space [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.move_reagent_slow(int(v[0]), int(v[1]), int(v[2]), int(v[3]), int(v[4]))

	elif method == 'pre_washing':
		biochem.pre_washing()

	elif method == 'prime_flowcell':
		biochem.prime_flowcell()

	elif method == 'prime_fluidics_system':
		biochem.prime_fluidics_system()

	elif method == 'prime_reagent_paths':
		biochem.prime_reagent_paths()

	elif method == 'prime_syringe_pump':
		biochem.prime_syringe_pump()

	elif method == 'primer_walking':
		biochem.primer_walking()

	elif method == 'push_into_flowcell':
		print "INFO\t *\t--> Please, enter follow up reagent number and centering volume to push into flowcell [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.push_into_flowcell(int(v[0]), int(v[1]))

	elif method == 'push_reagent_back':
		print "INFO\t *\t--> Please, enter the reagent number to push back and syringe speed [integers]: ",
		v = sys.stdin.readline().strip().split(' ')  # use stdin explicitly and remove trailing newline character
		biochem.push_reagent_back(int(v[0]), int(v[1]))

	elif method == 'run':
		biochem.run()

	elif method == 'syringe_pump_init':
		biochem.syringe_pump_init()

	elif method == 'test_incorporation':
		biochem.test_incorporation()

	elif method == 'test_walking':
		biochem.test_walking()

	else:
	 print 'WARNING\t *\t--> Error: not correct method input!\n\n--> Double check method name (1st argument)\n'
	 sys.exit(1)

	#-------------------------- Duration of biochemistry test ------------------------------

	delta = (time.time() - t0) / 60  # Calculate elapsed time for flowcell flush.
	logger.info('*\t--> Finished %s method execution - duration: %0.2f minutes\n' % (method, delta))

