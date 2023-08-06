import cv2
import numpy as np
import easyocr
import matplotlib.pyplot as pl
from PIL import Image, ImageChops
from pyallied.web.webWaits import customwebDriverwait
import textract
import os
import slate3k
import PyPDF2
from imap_tools import MailBox,AND
class miscellaneous(customwebDriverwait):
    def __init__(self,driver):
        super().__init__(driver)
        self.driver=driver    
    '''
    returns the embedded text in the image.
    It returns a list of detected text, with each text element containing three types of information. 
    Which are: the text, its bounding box vertices, and the confidence level of the text detection
    '''    
    def get_embeddedText_from_image(self,path:str):
        try:
            reader= easyocr.Reader(['en'])
            return reader.readtext(path)
        except Exception as error:
            raise error
    def is_images_same_compare_by_pixel(self,sourceFile, destinationFile):
        try:
            diff_img=ImageChops.difference(Image.open(sourceFile),Image.open(destinationFile)).convert('RGB')
            if diff_img.getbbox():
                return False
            else:
                return True
        except Exception as error:
            raise error        
    def pdf_content_reader(self,file1):
        try:
            file = open(file1,'rb')
          
            pdfRead=PyPDF2.PdfFileReader(file)
            #print(pdfRead.getDocumentInfo().title,' ----title----')
            output = []    
            readData=pdfRead.getPage(0)
            #print(readData.extractText(),' ----single----')
            for page in pdfRead.pages:
                output.append(page.extractText().replace("\n",""))            
            file.close()
            return output            
        except Exception as error:
            raise error
    def mail_outlook_search(self,userName,password,searchString:str,fromAddress:str):
        try:
            mailbox = MailBox('https://outlook.office.com/',993)
            mailbox.login(userName, password,'INBOX')
            responses =mailbox.idle.wait(timeout=120)
            mailText=''
            if responses:
                for msg in mailbox.fetch(AND(text=searchString,new=True,from_=fromAddress)):
                    mailText=msg.text
                    break
            return mailText
        except Exception as error:
            raise error
    def mail_outlook_Attachments(self,userName,password,searchString:str,fromAddress:str):
        try:
            mailbox = MailBox('https://outlook.office.com/',993)
            mailbox.login(userName, password,'INBOX')
            responses =mailbox.idle.wait(timeout=120)
            attachment=[]
            if responses:
                for msg in mailbox.fetch(AND(text=searchString,new=True,from_=fromAddress)):
                    for attach in msg.attachments:
                        attachment.append(attach.filename)
            return attachment                                
        except Exception as error:
            raise error                            
    def mail_outlook_Attachments_Read(self,userName,password,searchString:str,fromAddress:str):
        try:
            mailbox = MailBox('https://outlook.office.com/',993)
            mailbox.login(userName, password,'INBOX')
            responses =mailbox.idle.wait(timeout=120)
            attachment_Read={}
            if responses:
                for msg in mailbox.fetch(AND(text=searchString,new=True,from_=fromAddress)):
                    for attach in msg.attachments:
                        attachment_Read[attach.filename]=attach.payload
                        #attachment_Read.append(attach.payload)
            return attachment_Read                           
        except Exception as error:
            raise error  
