#import packages
import os
from shutil import copyfile,rmtree
import calendar,time,re

#import submodules
#from mails import ReadMails
from invoiceRequest import InvoiceRequest
from ReadPDF import getPDF
from PO_Details import get_PO
from downloadingPDF import DownloadDocuments
from getAccessToken import AccessToken
from getShippingDetails import ShippingDetails

#Define global variables
main_path = './Purchase Order and Shipping Details'


def main_process(ticket_detail):
    #Perform User Validation
    print('--Perform User Validation--')
    if(ticket_detail[0]['payload']['firstThread']['author']['name'].lower()=='qualyval test'):
        print('--User Validation Success. Getting Access token--')
        access_token = AccessToken()
        
        print('--Received Access token. Now performing download operation--')
        
        folder_name = str(ticket_detail[0]['payload']['ticketNumber'])+'-'+str(calendar.timegm(time.gmtime()))
        document_folder = main_path+'/'+folder_name
        os.mkdir(document_folder)
        DownloadDocuments(access_token,ticket_detail[0]['payload']['descAttachments'],main_path=document_folder)
        
        #Creating folder {ticket_number + epoch_time} and moving the documents
        '''
        folder_name = str(ticket_detail[0]['payload']['ticketNumber'])+'-'+str(calendar.timegm(time.gmtime()))
        document_folder = main_path+'/'+folder_name
        os.mkdir(document_folder)
        for item in os.listdir(main_path):
            if(os.path.isfile(main_path+'/'+item)):
                os.rename(main_path+'/'+item,document_folder+'/'+item)
        '''
        print('--Downloaded Documents. Now getting text content of documents--')
        #Convert to text files
        for item in os.listdir(document_folder):
            getPDF(document_folder+'/'+item,document_folder+'/'+os.path.splitext(item)[0]+'.txt')

        print('--Received text content. Classify document as PO as Shipping details--')
        #Validate Shipping Order and PO
        shipping_details_file_name = ''
        po_file_name = ''
        
        for item in os.listdir(document_folder):
            if(item.endswith('.txt')):
                with open(document_folder+'/'+item,'r') as text_file:
                    if(re.search(r"Purchase Order Number",text_file.read())):
                        po_file_name = item
                    else:
                        shipping_details_file_name = item 
        
        if((shipping_details_file_name=='') | (po_file_name=='')):
            raise 'No files found'

        print('--Documents Classified. Now Extracting Document contents--')
        #Data Extraction
        po_details = get_PO(document_folder+'/'+po_file_name)
        shipping_details = ShippingDetails(document_folder+'/'+shipping_details_file_name)

        print('--Documents Content Extracted. Now Generating Invoice--')
        #Creating Invoice
        invoice_no = InvoiceRequest(po_details[0],shipping_details,access_token,ticket_no = ticket_detail[0]['payload']['ticketNumber'])
        return invoice_no
    else:
        raise 'User Mismatch'    