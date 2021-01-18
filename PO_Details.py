#import all modules
import re,os
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import math
import csv


#Main Function
def get_PO(purchase_order_path):
    global final_data;
    final_data = []
    with open(purchase_order_path,'r') as f:
        client,job_name = get_Client_Job_Name(os.path.splitext(purchase_order_path)[0]+'.pdf')
        print(client,job_name)
        PO_Data = get_pdf_details(f.read(),client[0],job_name[0]);
        PO_Data.insert(0,os.path.splitext(purchase_order_path)[0]+'.pdf')
        final_data.append(PO_Data)
        return final_data

#Function to get Purchase Order Details
def get_pdf_details(input_text,client_name,job_name):
    global PO_Data
    PO_Data = []
    purchase_order_value = re.findall(r"(?<=Purchase Order Number :).*.(?=Pattison)",input_text,flags = re.S)[0].replace('\n','');
    purchase_order_no = re.findall(r"PO-\d{1,}",purchase_order_value,flags = re.S)[0].replace('\n','');
    pattsion_quote = re.findall(r"(?<=Pattison Quote #:).*.(?=Special Instructions:)",input_text,flags = re.S)[0].split('\n')[2]
    
    work_client_name_design = re.findall(r"(?<=Sales Contract :).*.(?=Quantity)",input_text,flags = re.S)[0].split('\n\n')
    
    try:
        work_client_name_design.remove("JOB PARTICULARS")
    except:
        pass
        
    try:
        work_client_name_design.remove("Agency")
    except:
        pass
        
    try:
        work_client_name_design.remove("Client")
    except:
        pass   

    try:
        work_client_name_design.remove("Job Name")
    except:
        pass

    try:
        work_client_name_design.remove("Design(s)")
    except:
        pass

    try:
        work_client_name_design.remove("PRODUCT")
    except:
        pass

    try:
        work_client_name_design.remove("Description:")
    except:
        pass
    try:
        work_client_name_design.remove("Special Instructions:")
    except:
        pass

    try:
        work_client_name_design.remove("Shipping Instructions:")
    except:
        pass

    try:
        work_client_name_design.remove("'Attached'")
    except:
        pass

    try:
        work_client_name_design.remove("Final Art")
    except:
        pass

    try:
        work_client_name_design.remove("LINK")
    except:
        pass    
    work_client_name_design = list(filter(None, work_client_name_design))
    
    work_order_no = work_client_name_design[0]
    
    global design;
    design = '';
    if(work_client_name_design[2].strip()==client_name.strip()):
        for i in range(4,len(work_client_name_design)):
            if(work_client_name_design[i]!=''):
                if(str(work_client_name_design[i]).strip()!=''):
                    if(str(work_client_name_design[i]).strip()[0]=='D'):
                        design = design + '\n' + work_client_name_design[i]
    else:
        for i in range(5,len(work_client_name_design)):
            if(work_client_name_design[i]!=''):
                if(str(work_client_name_design[i]).strip()!=''):
                    if(str(work_client_name_design[i]).strip()[0]=='D'):
                        design = design + '\n' + work_client_name_design[i]

    if(client_name in work_client_name_design):
        pass
    else:
        design = ''
        for item in work_client_name_design:
            try:
                if(re.match(r"D\d{1,}",item.split('-')[0].strip())):
                    design = design + '\n' + item
            except:
                pass
            
    quantity_required_by = input_text.split('Quantity\n')
    quantity_required_by = list(filter(None, quantity_required_by))
    split_quantity_required_by = quantity_required_by[1].split('\n')
    split_quantity_required_by = list(filter(None, split_quantity_required_by))
    global quantity,require_by,quoted_price;
    quantity = []
    require_by = []
    quoted_price = []
    #Check to find all numbers for quantity and all dates for required by from document 
    for item in split_quantity_required_by:
        number = re.search(r"^[0-9]*$",item)
        if number:
            quantity.append(item)
        date_check = re.search(r"\d{1,2}/\d{1,2}/\d{4}",item)
        if date_check:
            require_by.append(item)
        price_check = re.search(r"\$\d{1,}(,\d{1,})?(.)?\d{1,}",item)
        if price_check:
            quoted_price.append(item)    
    
    global description;
    description = ''
    for item in input_text.split('\n\n'):
        if((re.search('\*\*\*all',item.lower())) or (re.search('\*all',item.lower()))):
            description = item

    if(description == ''):    
        for item in input_text.split('\n\n'):
            if(re.search('full colour',item.lower())):
                description = item

    shipping_instrucions = re.findall(r"(?<=Shipping Instructions:).*.(?=Final Art :)",input_text,flags = re.S)[0].strip()
    final_art = re.findall(r"(?<=Final Art :).*.(?=AUTHORIZATION)",input_text,flags = re.S)[0].strip().split('\n')
    final_art = list(filter(None, final_art))
    if(len(final_art)==0):
        final_art.append(' ')
    PO_Data = [purchase_order_no,pattsion_quote,work_order_no,client_name,job_name,design,';'.join(quantity),';'.join(require_by),';'.join(quoted_price),description,shipping_instrucions,final_art[0]]
    
    return PO_Data

def get_Client_Job_Name(file_name):
    # Open a PDF file.
    fp = open(file_name, 'rb')

    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)

    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)

    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    global job_name,client;
    client = []
    job_name = []
    def parse_obj(lt_objs):

        # loop over the object list
        for obj in lt_objs:
            # if it's a textbox, print text and location
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                if(((math.floor(obj.bbox[0])==139) or (math.floor(obj.bbox[0])==98)) & ((math.floor(obj.bbox[1])==588) or (math.floor(obj.bbox[1])==638))):
                    client.append(obj.get_text().replace('\n', ''))
                if(((math.floor(obj.bbox[0])==139) or (math.floor(obj.bbox[0])==98)) & ((math.floor(obj.bbox[1])==573) or (math.floor(obj.bbox[1])==574) or (math.floor(obj.bbox[1])==623))):
                    job_name.append(obj.get_text().replace('\n', ''))
            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                parse_obj(obj._objs)
                
    # loop over all pages in the document
    for page in PDFPage.create_pages(document):

        # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()

        # extract text from this object
        parse_obj(layout._objs)
        return client,job_name;  

    fp.close();    
    
def write_to_csv(csv_content):
    # name of csv file  
    filename = "pdf_output.csv"
    
    # writing to csv file  
    with open(filename, 'w') as csvfile:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvfile)
        #Write headers
        headers = [['File Name','Purchase Order No','Pattison Quote','Work Order No','Client Name','Job Name','Design','Quantity','Required By','Quoted Price','Description','Shipping Instructions','Final Arts']]
        csvwriter.writerows(headers)
        # writing the data rows  
        csvwriter.writerows(csv_content)

