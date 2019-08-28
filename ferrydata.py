#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 15:19:55 2019

@author: aruskey

Ferry Data Automailer
Script uses the Oceans 2.0 API to collect data from the Duke Point-Tswassen ferry run
and email that data to a user once per week.  
Data Included:
- CDOM
- O2
- Temperature (Thermosalinograph)
- Outlet Flow
- Pump Current    
    
"""
#Overall WILLDATA
#imports
## ONC library must be installed first via pip3
import datetime
from datetime import date, timedelta
import os
from onc.onc import ONC
import smtplib
import os
import shutil
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

#constants
## can be modified to change who you are sending to/from, and your date ranges
email_to = ['wglatt@oceannetworks.ca', 'aruskey@gmail.com']
email_from = 'mtc.tdprojects@gmail.com'
onc = ONC('c2542572-ad18-4fd2-9add-365d7d504e58')  #oceans 2.0 API Key
output_folder = os.getcwd()+"\\output\\"   #"/output/" for linux 
dateFrom_string = str(date.today() - timedelta(days=7))+"T00:00:00.000Z"
dateTo_string = str(date.today())+"T00:00:00.000Z"

#function to attach an image to the email
def attach_image(msg_object, img_data, filename):
    image = MIMEImage(img_data, name=filename)
    msg_object.attach(image)

#function to download the images from oceans 2.0, default values provided for all parameters except device type and desired property
#There is a somewhat limited set of things you can do, could use more exploration into capability of oceans 2.0 API
#For example I couldn't figure out how to get outlet flow and pump current onto the same graph
def download_data_product(devcategorycode, propertycode, productcode='TSSP', extension='png', locationcode='TWDP', datefrom=dateFrom_string, dateto=dateTo_string, dpoquality=1, dporesample='none'):
    filters = {
            'dataProductCode' : productcode,
            'extension' : extension,
            'locationCode' : locationcode,
            'deviceCategoryCode' : devcategorycode,
            'propertyCode' : propertycode,
            'dateFrom' : datefrom,
            'dateTo' : dateto,
            'dpo_qualityControl' : dpoquality,
            'dpo_resample' : dporesample

            }
    res = onc.orderDataProduct(filters)
    onc.print(res)    


#download desired data images
#asset function call, if you want values other than default, label them, ie. extension = 'pdf'
download_data_product(devcategorycode = 'TURBCHLFL', propertycode = 'cdomfluorescence')
download_data_product(devcategorycode = 'TSG', propertycode = 'seawatertemperature')
download_data_product(devcategorycode = 'OXYSENSOR', propertycode = 'oxygen')
download_data_product(devcategorycode = 'PVCS', propertycode = 'amperage')
download_data_product(devcategorycode = 'PVCS', propertycode = 'voltage')


#generate email and send
#generate file names into strings for image data
for file in os.listdir(output_folder):
    if file.endswith(".png"):
        if("Chlorophyll" in str(file)): #one for each parameter
            chlorophyll = output_folder + str(file)
        if("Oxygen" in str(file)):
            oxygen = output_folder + str(file)
        if("PumpCurrent" in str(file)):
            pumpcurrent = output_folder + str(file)
        if("Thermosalinograph" in str(file)):
            thermosalinograph = output_folder + str(file)
        if("OutletFlow" in str(file)):
            pumpvoltage = output_folder + str(file)
 
#read downloaded png images(data) into memory    
chlorophyll_img_data = open(chlorophyll, 'rb').read()
oxygen_img_data = open(oxygen, 'rb').read()
pumpcurrent_img_data = open(pumpcurrent, 'rb').read()
thermosalinograph_img_data = open(thermosalinograph, 'rb').read()
pumpvoltage_img_data = open(pumpvoltage, 'rb').read()

#create email content
msg = MIMEMultipart()
msg['Subject'] = 'Will Data'
msg['From'] = 'mtc.tdprojects@gmail.com' 
msg['To'] = 'aruskey@gmail.com'

text = MIMEText("Ferry Data " + str(date.today()))
msg.attach(text)

attach_image(msg, chlorophyll_img_data, 'CDOM')
attach_image(msg, oxygen_img_data, 'Oxygen')
attach_image(msg, pumpcurrent_img_data, 'Pump Current')
attach_image(msg, pumpvoltage_img_data, 'Outlet Flow')
attach_image(msg, thermosalinograph_img_data, 'Temperature')

#attempt to generate + send email
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login('mtc.tdprojects@gmail.com', '1q2w3e4R!')
    server.sendmail(email_from, email_to, msg.as_string())
    server.close()
    print ('Email Sent!')
except:
    print ("Server Full of Water")

#archive old files
#necessary as oceans 2.0 api hangs if you try to download file with the same name in folder    
for file in os.listdir(output_folder):
    if file.endswith(".png"):
        shutil.move((output_folder + str(file)), (output_folder + "old\\"+str(file))) #"/old/" for linux
        print(output_folder + "old\\" + str(file))  #"/old/" for linux 
