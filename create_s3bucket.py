#!/usr/bin/env python3

## Importing the required libraries to be used.

import boto3
import sys
import time
import subprocess

## Global variables;

ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

###########################

def create_new_bucket(bucket_name):
    '''
        Creates a new AWS S3 bucket.

        The name of the bucket should be given as an argument as it is required
        to be unique globally.
    '''
    print('Creating a new bucket with name ' + bucket_name + '..')

    try:
        new_bucket = s3.create_bucket(
            Bucket = bucket_name,

            ## Making sure the bucket is sent to the eu-west-1 zone.
            CreateBucketConfiguration = {'LocationConstraint': 'eu-west-1'},

            ## Making the bucket readable by anyone (so it can be published onto a EC2 instance later).
            ACL = 'public-read'
        )

        print('New bucket created (Name: ' + new_bucket.name + ').')

        return new_bucket

    except Exception as error:
        print('An error was found while trying to create a new bucket: ' + error)

def copy_image_to_bucket(bucket_name, image_name):
    '''
        Copies a given image file to a bucket.
    '''
    print('Copying image file ' + image_name + ' to bucket..')

    try:
        pushed_image = s3.Object(bucket_name, image_name).put(
            Body = open(image_name, 'rb'),

            ## Making the image readable by anyone.
            ACL = 'public-read'
        )

        print('Image ' + image_name + ' added to bucket.')

    except Exception as error:
        print('An error was found while trying to push the file to the bucket: ' + error)

def copy_image_to_instance_web_server(bucket_name, image_name, instance_key_name, instance_public_ip_address):
    '''
        Copies the given image from the bucket to an instance's web server landing
        page.

        The instance's ssh key and public ip address will be used to connect to
        the instance.

        Note that the instance is assumed to be running and a HTML file is created
        firstly to be used to later replace the default web server landing page.
    '''
    print('Creating copy of the image file ' + image_name + ' into a HTML file..')

    try:
        '''
            Running the command using a single string argument so echo is only
            used to create a file after the shell looks at the other arguments.
        ''' 
        subprocess.run(
            ['echo "<html><img src="https://s3-eu-west-1.amazonaws.com/' + bucket_name + '/' + image_name + '"></html>" > image.html'],
            shell = True
        )

        print('HTML file containing copy of image created. Now adding image html file to the instance ' + instance_public_ip_address + '..')

        subprocess.run([
            'scp',
            '-i',
            instance_key_name + '.pem',
            'image.html',
            'ec2-user@' + instance_public_ip_address + ':~'
        ])

        print('Image html file copied to instance. Now replacing the default web server landing page with the image html file..')

        ## Moving the pushed file to replace the default nginx html file.
        subprocess.run([
            'ssh',
            '-i',
            instance_key_name + '.pem',
            'ec2-user@' + instance_public_ip_address,
            'sudo',
            'mv',
            'image.html',
            '/usr/share/nginx/html/index.html'
        ])

        print('Image copied to instance web sever landing page.')

    except Exception as error:
        print('An error was found while trying to copy the image to the instance: ' + error)

def delete_bucket_objects(bucket):
    '''
        Deletes all existing objects inside a given bucket using a simple
        for loop.
    '''
    print('Deleting all objects from bucket..')

    for key in bucket.objects.all():
        
        try:
            key.delete()

        except Exception as error:
            print('An error was found while trying to delete an object from the bucket: ' + error)

    print('Bucket objects deleted.')

###########################

def main():
    '''
        Main function to start-up the program.

        1) Creates a new bucket.
        2) Copies image to the new bucket.
        3) Copies image to an EC2 instance.
    '''
    print('This python module will create a AWS S3 publicly readable bucket and copy an image to the bucket and to a running EC2 instance web server landing page.')

    bucket_name = input('Please provide the name of the bucket you wish to create (Must be unique): ')
    create_new_bucket(bucket_name)

    time.sleep(10)

    image_name = input('Please provide the file name of the image you wish to put onto the bucket (in this directory): ')
    copy_image_to_bucket(bucket_name, image_name)

    print('Now prompting running EC2 web server instance details..;')
    key_name = input('Please provide the private .pem key file that the instance uses (in this directory) (Omit the file extension): ')
    public_ip_address = input('Please provide the public ip address of the instance that you wish to use: ')
    copy_image_to_instance_web_server(bucket_name, image_name, key_name, public_ip_address)

    input('Press any key to delete this bucket.')
    bucket = s3.Bucket(bucket_name)
    delete_bucket_objects(bucket)

if __name__ == '__main__':
  main()
