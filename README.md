# Boto3 Amazon Web Server Experiments (Developer Operations Assignment 1)
The following Python modules operates

1) The creation and launch of an AWS EC2 instance with a pre-configured nginx web server.

2) The creation of a AWS S3 bucket and an automatic upload example of a given picture to the bucket and to the EC2 instance's web server landing page.

## Required data to run the Python modules:

- *sg-securitygroupid* An id of a security group from your AWS account that allows inbound SSH/HTTP/HTTPS traffic.

- *KeyPair.pem* A private .pem key pair file from your AWS account. Should be located in this directory.

- *ImageFile.jpg* A image file to be used to add onto a S3 bucket and onto the EC2 web server instance. Should be located in this directory.

## Running the Python modules:
This assumes that the user has Python installed.

1) *python3 run_newwebserver.py*

2) *python3 create_s3bucket.py*

## Looking at the output:
Once the python modules has been run, the image file added onto the EC2 web server instance can be viewed at

- ec2-[public-ip-address-of-created-instance].eu-west-1.compute.amazonaws.com

## Detected bugs:

1) Occasionally after copying the web server script to the EC2 instance in run_newwebserver.py, the script is unable to be run remotely as an error is given where the python3 command is not found inside the instance.
My assumption for the cause of this bug is that the the instance sometimes tries to run the script before it is made executable from the previous command.

2) Rarely after the script is run remotely via python3, the nginx web server landing page does not start up.
