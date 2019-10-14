#file -- helper_tools.py --

from datetime import datetime
import subprocess
import os

def create_log(user_error_message, exception_message):
	""" Saves a message to a log file under logs/Error log (Date time).txt """

	log_datetime = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
	dir_name = "logs"
	file_name = "Error log " + log_datetime + ".txt"

	create_directory(dir_name)

	# Writes log file
	file = open(dir_name + "/" + file_name, "w+")
	file.write("An error has occurred while running run_newwebserver.py:\nTime: " +
		log_datetime + "\n\n" + user_error_message + "\n" + str(exception_message))
	file.close()

	print("An error log has been saved to logs/" + file_name)

def create_directory(dir_name):
	""" Creates a directory if it doesn't already exist """

	try:
		# Create directory if it doesn't already exist
		os.mkdir(dir_name)
	except FileExistsError:
		# Do nothing if the directory already exists
		pass

def get_image(url, filename):
	""" Uses curl to get an image from a url """
	print("Getting " + filename + "from " + url + "...\n")
	subprocess.run(['curl','-o', filename,url],stdout=subprocess.DEVNULL)
	print(filename + " acquired successfully.")

def exit_program():
	""" Prompts the user to press enter and quits the program """
	input("\nPress enter to quit the program...")
	quit()