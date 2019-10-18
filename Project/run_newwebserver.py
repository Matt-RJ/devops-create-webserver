#! /usr/bin/env python3
""" run_newwebserver.py: Creates an AWS S3 bucket and EC2 instance with apache running on it. """

import os
import sys
import boto3

import helper_tools
import ec2_tools
from s3_tools import *

__author__ = "Mantas Rajackas"
__version__ = "1.0"

def parse_sysargs():
	""" Parses the arguments provided when running this script. Arguments not specified use the default option. """
	
	# The order that arguments are taken in when executing this script.
	config_order = ["image_id", "instance_type", "key_name", "security_group_name",
				    "tag_key", "tag_value", "bucket_name", "location_constraint"]
    
    # Default settings for EC2 instances, used if arguments don't overwrite them.
	config = {
		"image_id": "ami-0ce71448843cb18a1",
		"instance_type": "t2.micro",
		"key_name": "DevOps-Assignment01-Key",
		"security_group_name": "allow-ssh-http",
		"tag_key": "DevOps",
		"tag_value": "Assignment01",
		"bucket_name": "20079912-assignment1",
		"location_constraint": "eu-west-1"
	}

	for i in range(1, len(sys.argv)):
		config[config_order[i-1]] = sys.argv[i]

	print("\nAn instance will be created with the following attributes:")
	print(config)
	print()
	return config


# This runs when the EC2 instance has been created to install and run an apache web server
USER_DATA = open('user_data.txt', 'r').read()

def main():
	""" Main entry point of the program """
	config = parse_sysargs()

	# Creates an EC2 resource for creating instances
	try:
		ec2_resource = boto3.resource('ec2')
	except Exception as e:
		print(e)
		user_error_message = "There was an issue with setting up the EC2 resource."
		print(user_error_message)
		helper_tools.create_log(user_error_message, e)
		exit_program()

	# Creates an S3 resource for creating buckets
	try:
		s3_resource = boto3.resource('s3')
	except Exception as e:
		print(e)
		user_error_message = "There was an issue with setting up the S3 resource."
		print(user_error_message)
		helper_tools.create_log(user_error_message, e)
		exit_program()

	# Creates the Key Pair
	ec2_tools.create_key_pair(ec2_resource, config["key_name"])

	# Creates an EC2 instance
	instance = ec2_tools.create_ec2_instance(ec2_resource, config["image_id"], config["key_name"],
											 config["security_group_name"], config["instance_type"],
											 USER_DATA, config["tag_key"], config["tag_value"])

	instance_public_ip = instance.public_ip_address

	# Creates an S3 bucket if it doesn't exist already
	if (not bucket_exists(s3_resource, config["bucket_name"])):
		create_s3_bucket(s3_resource, config["bucket_name"], config["location_constraint"])
	else:
		print("The S3 bucket with the name '" + config["bucket_name"] + "' already exists, continuing...\n")

	# Creates a directory for images
	helper_tools.create_directory("images")

	# Downloads an image using curl
	get_image("http://devops.witdemo.net/image.jpg", "images/image.png")

	# Uploads the image to an S3 bucket
	upload_to_bucket(s3_resource, config["bucket_name"], "images/image.png")

	# These will run on the instance when SSHing in
	commands = """
		echo '<html>' > index.html
		echo 'Private IP address: ' >> index.html
		curl http://169.254.169.254/latest/meta-data/local-ipv4 >> index.html
		echo '<br>Here is the image, downloaded automatically with curl:<br> ' >> index.html
		echo '<img src="https://s3-eu-west-1.amazonaws.com/%s/images/image.png">' >> index.html
		echo '</html>' >> index.html
		sudo mkdir -p /var/www/html
		sudo chmod 755 /var/www/html
		sudo mv index.html /var/www/html/index.html
	""" % (config["bucket_name"])

	ec2_tools.ssh_into_ec2_instance(config["key_name"], instance_public_ip, commands)

	ec2_tools.show_all_instances(ec2_resource)

	print("The instance has been successfully created and configured.")

	exit_program()

if __name__ == "__main__":
	main()
