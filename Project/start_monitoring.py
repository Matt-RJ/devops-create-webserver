#! /usr/bin/env python3
""" start_monitoring.py: Monitors an EC2 or S3 instance using Cloudwatch. """

from helper_tools import *
import boto3
import sys
from datetime import datetime, timedelta

def main():

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

	start_monitoring(cloudwatch_resource, instance_id)

def start_monitoring(cloudwatch_resource, instance_id):
	metric_iterator = cloudwatch_resource.metrics.filter(Namespace ='AWS/EC2',
														 MetricName='CPUUtilization',
														 Dimensions=[{'Name': 'InstanceId','Value': instance_id}])
	for metric in metric_iterator:
		response = metric.get_statistics(StartTime=datetime.now() - timedelta(minutes=65),
										 EndTime=datetime.now() - timedelta(minutes=60),
										 Period=300,
										 Statistics=['Average'])
		if (len(response['Datapoints']) != 0):
			print("Average CPU utilisation: ", response['Datapoints'][0]['Average'])
		print(response)
		
if __name__ == "__main__":
	main()