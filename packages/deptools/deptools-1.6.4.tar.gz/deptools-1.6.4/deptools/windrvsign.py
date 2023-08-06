# -*- coding: utf-8 -*-
'''AlazarTech Windows Driver Signature

Usage:
  windrvsign <cab_file> <output_zip>
  windrvsign -h | --help
  windrvsign --version

Arguments:
  <cab_file>      CAB file to be sent for signing.
  <output_zip>    Path and name of the output zip folder contaning the signed drivers.

'''

import os
from datetime import date
import requests
from azure.storage.blob import BlobClient
import time
import zipfile
from distutils.dir_util import copy_tree

from docopt import docopt

def get_access_token():

  body = "grant_type=client_credentials" +\
      "&client_id="+os.getenv('AZURE_AD_APPLICATION_CLIENT_ID') +\
      "&client_secret="+os.getenv('AZURE_AD_APPLICATION_CLIENT_SECRET') +\
      "&resource=https://manage.devcenter.microsoft.com"

  req = requests.post("https://login.microsoftonline.com/"+os.getenv('AZURE_AD_APPLICATION_TENANT_ID')+"/oauth2/token", data = body)
  
  if req.status_code != 200:
    raise Exception("Unable to get access token")

  access_token = req.json()['access_token']

  return access_token

def create_new_product(access_token):
  today = date.today()
  date_time = today.strftime("%Y-%m-%d"+"T"+"%H:%M:%S")

  body = {
    "productName": "Driver signature - " + date_time,
    "testHarness": "Attestation",
    "announcementDate": date_time,
    "deviceMetadataIds": [],
    "deviceType": "internal",
    "isTestSign": 0,
    "isFlightSign": 0,  
    "marketingNames": [],
    "requestedSignatures": [
        "WINDOWS_v100_TH2_FULL",
        "WINDOWS_v100_X64_TH2_FULL",
        "WINDOWS_v100_RS1_FULL",
        "WINDOWS_v100_X64_RS1_FULL",
        "WINDOWS_v100_RS2_FULL",
        "WINDOWS_v100_X64_RS2_FULL",
        "WINDOWS_v100_RS3_FULL",
        "WINDOWS_v100_X64_RS3_FULL",
        "WINDOWS_v100_RS4_FULL",
        "WINDOWS_v100_X64_RS4_FULL",
        "WINDOWS_v100_RS5_FULL",
        "WINDOWS_v100_X64_RS5_FULL",
        "WINDOWS_v100_19H1_FULL",
        "WINDOWS_v100_X64_19H1_FULL",
        "WINDOWS_v100_X64_CO_FULL"
    ],
    "additionalAttributes": {}
  }

  req = requests.post("https://manage.devcenter.microsoft.com/v2.0/my/hardware/products/", headers = {"Authorization" : "Bearer " + access_token}, json = body)
  
  if req.status_code != 201:
    raise Exception("Unable to create new product") 

  product_id = str(req.json()['id'])

  return product_id

def create_new_submission(access_token, product_id):

  today = date.today()
  date_time = today.strftime("%Y-%m-%d"+"T"+"%H:%M:%S")

  body = {
    "name": "Drivers signature - " + date_time,
    "type": "initial"
  }

  req = requests.post("https://manage.devcenter.microsoft.com/v2.0/my/hardware/products/" + product_id + "/submissions", headers = {"Authorization" : "Bearer " + access_token}, json = body)
  
  if req.status_code != 201:
    raise Exception("Unable to create new submission")

  submission_id = str(req.json()['id'])

  for item in req.json()['downloads']['items']:
    if item['type']=="initialPackage":
        sas_url = item['url']
        return submission_id, sas_url

  raise Exception("Unable to retreive the shared access signature (SAS) URI")  

def upload_package(sas_url, cab_file):

  blob = BlobClient.from_blob_url(sas_url)

  with open(cab_file, "rb") as data:
      blob.upload_blob(data)

def download_package(signed_package, zip_file):

  blob = BlobClient.from_blob_url(signed_package)

  with open(zip_file, "wb") as my_blob:
      blob_data = blob.download_blob()
      blob_data.readinto(my_blob)

def unzip(zip_file, signed_folder_path):

  unzip_folder = "./SignedDrivers"

  with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(unzip_folder)

  copy_tree("./SignedDrivers/drivers", signed_folder_path)

def commit_submission(access_token, product_id, submission_id):

  req = requests.post("https://manage.devcenter.microsoft.com/v2.0/my/hardware/products/" + product_id + "/submissions/" + submission_id + "/commit", headers = {"Authorization" : "Bearer " + access_token})
  
  if req.status_code != 202:
    raise Exception("Unable to commit product submission")

def is_signing_complete(access_token, product_id, submission_id):

  req = requests.get("https://manage.devcenter.microsoft.com/v2.0/my/hardware/products/" + product_id + "/submissions/" + submission_id, headers = {"Authorization" : "Bearer " + access_token})

  if req.status_code != 200:
    raise Exception("Unable to check submission status")

  if req.json()['workflowStatus']['currentStep'] == "finalizeIngestion" and req.json()['workflowStatus']['state'] == 'completed':
    for item in req.json()['downloads']['items']:
      if item['type']=="signedPackage":
        return True, item['url']
    raise Exception("Unable to find signed package")
    

  if req.json()['commitStatus'] == "commitFailed":
    raise Exception("Commited submission failed") 

  return False, ""

def windows_driver_sign(cabfile, outputzip):

    if not os.path.exists(cabfile):
        raise ValueError("{} doesn't exist".format(cabfile))

    root, ext = os.path.splitext(outputzip)
    if ext != '.zip':
        raise ValueError("{} doesn't have the zip extension".format(outputzip))

    outputdir = os.path.dirname(outputzip)
    if not os.path.exists(outputdir):
        raise ValueError("{} is not a valid path".format(outputdir))
    
    access_token = get_access_token()
    product_id = create_new_product(access_token)
    submission_id, sas_url = create_new_submission(access_token, product_id)
    upload_package(sas_url, cabfile)
    commit_submission(access_token, product_id, submission_id)
    sign_complete = False
    while sign_complete == False:
      sign_complete,signed_package =  is_signing_complete(access_token, product_id, submission_id)
      time.sleep(60)
    download_package(signed_package, outputzip)

def main():
    '''Main function'''
    arguments = docopt(__doc__, version='Windows Driver Signature Utility')
    windows_driver_sign(
             cabfile=arguments['<cab_file>'],
             outputzip=arguments['<output_zip>'])

if __name__ == "__main__":
    main()
