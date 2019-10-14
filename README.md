# devops-create-webserver
Assignment 1 for DevOps, creates a AWS EC2 instance with a simple web server running on it.

This script creates an Amazon EC2 instance on the execution of run_newwebserver.py on a Linux machine. An Apache web server is automatically installed and run on the instance. While the instance runs, an S3 bucket is created and an image is downloaded automatically from the internet using curl and is displayed on the index page.

Extra arguments may be given while executing the program to configure the type of instance, security group, tags, and more.
