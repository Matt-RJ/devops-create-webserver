#file -- s3_tools.py --

from helper_tools import *

def create_s3_bucket(s3_resource, bucket_name, location_constraint):
	""" Creates a new S3 bucket """
	print("\nCreating a S3 bucket with the name '" + bucket_name + "'...")
	try:
		s3_resource.create_bucket(
			Bucket=bucket_name,
			CreateBucketConfiguration={'LocationConstraint': location_constraint}
		)
		print("The S3 bucket was created successfully.")
	except Exception as e:
		print(e)
		user_error_message = "There was an error with creating an S3 bucket."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()

def bucket_exists(s3_resource, bucket_name):
	""" Checks if an S3 bucket already exists by name """
	return s3_resource.Bucket(bucket_name) in s3_resource.buckets.all()

def upload_to_bucket(s3_resource, bucket_name, file):
	""" Uploads a file to an S3 bucket with public access permissions """
	try:
		print("\nUploading " + file + " to the S3 bucket...")
		s3_resource.Object(bucket_name, file).put(
			Body=open(file, 'rb'),
			ACL='public-read' # Gives public access permissions to the file
		)
		print("The file has been uploaded successfully.\n")
	except Exception as e:
		print(e)
		user_error_message = "There was an error with uploading to the S3 bucket."
		print(user_error_message)
		create_log(user_error_message, e)
		exit_program()