#! /usr/bin/env python3
""" start_monitoring.py: Monitors an EC2 instance using Cloudwatch. """

from helper_tools import *
import boto3
import sys
from datetime import datetime, timedelta
from time import sleep

START_TIME = datetime.now() - timedelta(minutes=62)
END_TIME = datetime.now() - timedelta(minutes=61)

def main():
	""" The main entry point of the program """

	# Creates the boto3 cloudwatch resource needed for monitoring
	try:
		cloudwatch_resource = boto3.resource('cloudwatch')
	except Exception as e:
		user_error_message = "There was an error while setting up the cloudwatch resource."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()

	# Checks that an instance ID was provided as an argument when executing this script
	try:
		instance_id = sys.argv[1]
	except IndexError as e:
		print(e)
		user_error_message = "Error: An instance ID must be provided when executing this script."
		exit_program()
	except Exception as e:
		print(e)
		user_error_message = "There was an error with the instance ID provided."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()

	# Displays monitoring details every 60 seconds to the console
	try:
		print("Starting monitoring, CTRL+C will exit.")
		while True:
			START_TIME = datetime.now() - timedelta(minutes=62)
			END_TIME = datetime.now() - timedelta(minutes=61)
			monitor_check(cloudwatch_resource, instance_id)
			count_down(60, "Time until refresh")
	except KeyboardInterrupt as e:
		print("\n")
		exit()
		

def monitor_check(cloudwatch_resource, instance_id):
	""" Gathers metrics of an EC2 instance and prints them out to the console """
	cpu_util = get_metric(cloudwatch_resource, instance_id, 'CPUUtilization')
	disk_read_ops = get_metric(cloudwatch_resource, instance_id, 'DiskReadOps')
	disk_write_ops = get_metric(cloudwatch_resource, instance_id, 'DiskWriteOps')
	network_in = get_metric(cloudwatch_resource, instance_id, 'NetworkIn')
	network_out = get_metric(cloudwatch_resource, instance_id, 'NetworkOut')

	print("\nAverages for " + instance_id + " at " + (datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S") + ":")
	print("\tCpu utilisation: " + str(cpu_util) + "%")
	print("\tDisk read operations: " + str(disk_read_ops))
	print("\tDisk write operations: " + str(disk_write_ops))
	print("\tIncoming traffic amount: " + str(network_in) + " bytes")
	print("\tOutgoing traffic amount: " + str(network_out) + " bytes")
	print()


def get_metric(cloudwatch_resource, instance_id, metric_name):
	""" Gets the datapoints for a particular metric of an EC2 instance """
	metric_iterator = cloudwatch_resource.metrics.filter(Namespace ='AWS/EC2',
														 MetricName=metric_name,
														 Dimensions=[{'Name': 'InstanceId','Value': instance_id}])
	for metric in metric_iterator:
		response = metric.get_statistics(StartTime=START_TIME, # 2 minutes ago
										 EndTime=END_TIME, # 1 minute ago
										 Period=60,
										 Statistics=['Average'])
		if (len(response['Datapoints']) != 0):
			return response['Datapoints'][0]['Average']
		#print(response)

def count_down(seconds, message):
	""" Counts down from a certain number of seconds, printing out the time left with a message once per second """
	while (seconds >= 0):
		sleep(1)
		print("\r" + message + ": " + str(seconds), end=" ")
		seconds -= 1
	print()
	return
		
if __name__ == "__main__":
	main()