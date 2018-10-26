#!/usr/bin/env python3

## Importing the required libraries to be used.

import boto3
import time
import subprocess

## Global variable to access EC2 functions provided by Boto3;

ec2 = boto3.resource('ec2')

###########################

def create_new_webserver_instance(security_group_id, key_name):
    '''
        Creates and configures a AWS EC2 t2.micro instance with a pre-configured nginx
        web server.

        Requires a single Security Group Id from the user's AWS account and a SSH private
        pem key located in the same directory as this file as arguments to be used by
        the instance.
    '''
    print('Creating a new web server instance using the ' + key_name + ' key and ' + security_group_id + ' security group..')

    try:
        new_instance = ec2.create_instances(
            ImageId = 'ami-0c21ae4a3bd190229',
            MinCount = 1,
            MaxCount = 1,
            InstanceType = 't2.micro',

            ## Security group the instance will abide to (must be in your AWS account);
            SecurityGroupIds = [security_group_id],

            ## Name of private key to be used to launch the instance (should be in the same directory as this file);
            KeyName = key_name,

            ## Start-up instructions to install nginx
            UserData =  '''#!/bin/bash
                        yum update -y
                        yum install python3 -y
                        amazon-linux-extras install nginx1.12 -y'''
        )

        print('New instance created (ID: ' + new_instance[0].id + ').')

        return new_instance

    except Exception as error:
        print('An error occured while trying to create a new instance: ' + error)

def copy_file_to_instance(instance, key_name, file_name = 'check_webserver.py'):
    '''
        Copies the given file to the specified instance.

        Note that the file is copied to the ~ (home) directory of the instance.
    '''
    print('Copying file ' + file_name + ' to instance..')

    try:
        ## Causes an error if file doesn't exist.
        fileExists = open(file_name)

        print('scp -i ' + key_name + '.pem ' + file_name + 'ec2-user@' + instance[0].public_ip_address)

        ## Using the linux secure copy (scp) command to copy the file.
        subprocess.run([
            'scp',
            '-i',
            key_name + '.pem',
            file_name,
            'ec2-user@' + instance[0].public_ip_address + ':~',
        ])

        print('File ' + file_name + ' copied to instance.')

    except Exception as error:
        print('An error occured while copying file to the instance: ' + error)

def execute_file_in_instance(instance, key_name, file_name  = 'check_webserver.py'):
    '''
        Runs the given file located in the specified instance remotely
        using ssh.

        Note that this function assumes the file already exists in the
        home directory of the instance, so no checking is applied.
    '''
    print('Executing the file ' + file_name + ' in the instance remotely..')

    try:
        ## Making the file executable.
        subprocess.run([
            'ssh',
            '-i',
            key_name + '.pem',
            'ec2-user@' + instance[0].public_ip_address,
            'chmod',
            '400',
            file_name
        ])

        print('File ' + file_name + ' is now executable.')

        ## Running the file if it's a python file.
        if '.py' in file_name:
            print('The given file is a python file and will now be run..')

            subprocess.run([
                'ssh',
                '-i',
                key_name + '.pem',
                'ec2-user@' + instance[0].public_ip_address,
                'python3',
                file_name
            ])

            print('File ' + file_name + ' was executed.')

        else:
            print('File ' + file_name + ' was not executed.')

    except Exception as error:
        print('An error occured while executing the web server monitoring script remotely: ' + error)


###########################

def main():
    '''
        Main function to start-up the program.

        1) Creates a new instance.
        2) Copies web server monitoring script to instance.
        3) Run web server check and executes nginx appropriately.
    '''
    print('This python module will create a AWS EC2 web server instance and execute a web server monitoring script.')

    security_group_id = input('Please provide the id of a security group located in your AWS account that this new instance will use: ')
    key_name = input('Please provide the private .pem key file that this instance will use  (in this directory) (Omit the file extension): ')
    instance = create_new_webserver_instance(security_group_id, key_name)

    print('Sleeping the program for 60 seconds to let the instance to be configured..')
    time.sleep(60)
    instance[0].reload()
    print('60 seconds passed.')

    '''
        Note that the user is not prompted to input the monitoring script
        file as it comes with the assignment folder.
        
        Otherwise:
            web_server_file_name = input('Please provide the name of the web server monitoring script file  (in this directory): ')
            copy_file_to_instance(instance, key_name, web_server_file_name)
            execute_file_in_instance(instance, key_name, web_server_file_name)
    '''
    copy_file_to_instance(instance, key_name)

    ## Workaround to attempt to fix bug 1) specified in README.md
    time.sleep(10)

    execute_file_in_instance(instance, key_name)

    print('To connect to the EC2 web server instance, please use the following command in another terminal (in this directory): ')
    print('ssh -i ' + key_name + '.pem ec2-user@' + instance[0].public_ip_address)

    input('Press any key to terminate the instance.')
    instance[0].terminate()

if __name__ == '__main__':
  main()  