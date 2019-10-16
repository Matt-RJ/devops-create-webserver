#file -- ec2_tools.py --

from helper_tools import *
import time
import botocore
import subprocess

def create_ec2_instance(ec2_resource, image_id, key_name, security_group_name, instance_type, user_data, tag_key, tag_value):
	""" Creates a new ec2 instance and returns it """
	print("Launching an EC2 instance...")
	try:
		new_instance = ec2_resource.create_instances(
			ImageId = image_id,
			KeyName = key_name,
			SecurityGroupIds = [security_group_name],
			MinCount = 1,
			MaxCount = 1,
			InstanceType = instance_type,
			UserData = user_data,
			TagSpecifications = [
			{
				'ResourceType': 'instance',
				'Tags':
				[
					{
						'Key': tag_key,
						'Value': tag_value
					},
				]
			},
		])

		# Waits until the instance is running so that its IP may be acquired
		new_instance[0].wait_until_running()

		new_instance[0].reload()
		print ("A new instance has been launched with id: " + new_instance[0].id)
		print ("The instance's public IP is: " + new_instance[0].public_ip_address)

	except Exception as e:
		print(e)
		user_error_message = "There was an error with launching the EC2 instance."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()

	return new_instance[0]

def ssh_into_ec2_instance(key_name, instance_ip, commands):
	""" Executes commands on an instance using SSH """
	key = "key/" + key_name + ".pem"
	attempts = 5
	success = False

	print("Attempting to SSH into the instance...")
	# Tries to connect 5 times as ports might not be open straight away
	while attempts > 0:
		try:
			subprocess.run(
				[
					"ssh", "-o", "StrictHostKeyChecking=no",
					"-i", key, "ec2-user@"+instance_ip, commands
				], check=True # This line causes the subprocess to throw a Python exception if something fails
				#stdout=subprocess.DEVNULL,
				#stderr=subprocess.STDOUT
			)
			success = True
			break
		except Exception as e:
			pass
		time.sleep(1)

	if (not success):
		user_error_message = "An SSH connection could not be established."
		print(user_error_message)
		create_log(user_error_message, "")
		exit_program()
	else:
		print("Done.")

def create_key_pair(ec2_resource, key_pair_name):
	""" Creates a new key pair and saves it to key/key_pair_name.pem """
	dir_name = "key"
	create_directory(dir_name)
	
	try:
		# Attempts to create the key pair
		key_pair = ec2_resource.create_key_pair(KeyName=key_pair_name)

		# If the key pair doesn't already exist, create one.
		file = open(dir_name + "/" + key_pair_name + ".pem", "w")
		key_pair_out = str(key_pair.key_material)
		file.write(key_pair_out)
		file.close()

		# Changes the permissions of the key so that it may be used
		subprocess.run(["chmod","700","key/"+key_pair_name+".pem"])

		print("A new key pair called '" + key_pair_name + "' has been created successfully.")
	
	except botocore.exceptions.ClientError as e:
		# If the key pair already exists
		print("The key" + key_pair_name + " already exists, continuing... ")
		return
	except Exception as e:
		print(e)
		user_error_message = "There was an error with setting up the key pair."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()

def show_all_instances(ec2_resource):
	""" Prints out all of the instance IDs and states """
	print("Here are all of the instances:")
	for instance in ec2_resource.instances.all():
		print(instance.id, instance.state)