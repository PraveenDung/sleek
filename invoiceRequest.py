import requests
import json
import os
import pandas as pd
from io import StringIO
from collections import OrderedDict 
from operator import getitem 
import datetime

#Design and product
def getNQ(str):
    name,q=str.split('(')
    q=q.replace(')','')
    return name,int(q)

def getInvoice(df,spec):
    data=df[df["Spec Id"]==spec]
    if data.empty:
        return ""
    else:
        return data["Invoice"].item()

def getPrice(df,spec,units):
    data=df[df["Spec Id"]==spec]
    if data.empty:
        return ""
    if units==1:
        return int(data['1'].item())
    elif units>200:
        return int(data['176-200'].item())
    cols=list(df.columns)
    i=cols.index('1')
    ranges={}
    for i,items in enumerate(cols[i:]):
        if '-' in items:
            a,b=items.split('-')
            a,b=int(a),int(b)
            ranges[items]=range(a,b+1)
    for k,v in ranges.items():
        if units in v:
            return(int(data[k].item()))

def getAll(design):
    design = list(filter(None, design))
    df = pd.read_csv('./processed_prices.csv')
    df.fillna(False, inplace=True, )
    designs={}

    global name_values
    global quan_values
    name_values = []
    quan_values = []

    for i,d in enumerate(design):
        try:
            *_,n,spec=d.split(' - ')
            name,quan=getNQ(n)
            name_values.append(spec)
            quan_values.append(quan)
            #invoice=getInvoice(df,spec)
            #cost=getPrice(df,spec,int(quan))
            #designs[i]={"name":name,"quantity":quan,"Spec no.":spec,"Invoice Code":invoice,"Total Cost":cost,"Design":d}
        except:
            pass    
    
    global invoice
    for i,d in enumerate(design):
        try:
            *_,n,spec=d.split(' - ')
            invoice=getInvoice(df,spec)
            name,quan=getNQ(n)
            index_values = [i for i, x in enumerate(name_values) if x == spec]
            total = 0
            for item in index_values:
                total = total + int(quan_values[item])
            cost=getPrice(df,spec,total)
            designs[i]={"name":name,"quantity":quan,"Spec no.":spec,"Invoice Code":invoice,"Total Cost":cost,"Design":d}    
        except:
            designs[i]={"name":"","quantity":0,"Spec no.":spec,"Invoice Code":invoice,"Total Cost":0,"Design":d}
    return designs


def InvoiceRequest(po_details,shipping_details,access_token,ticket_no):
    #--PDF Values--#
    purchase_order_no = po_details[1]
    description = po_details[10]
    shipping_instruction = po_details[11]
    final_art = po_details[12]
    misc_notes = 'Description:\n'+description+'\n\n'+'Shipping Instructions:\n'+shipping_instruction+'\n\n'+'Final Art:\n'+final_art
    date_time_str = str(datetime.datetime.strptime(str(po_details[8].split(';')[0]), '%m/%d/%Y').date())
    print(date_time_str)
    pdf_due_date = date_time_str
    #print(product_name)
    price = 1
    job_name = po_details[5]
    client_name = po_details[4]
    pattison_quote=po_details[2]
    work_order_number = po_details[3]
    design = po_details[6].split('\n')
    designs=getAll(design)
    shipping_detail = ''

    #Shipping
    for item in shipping_details:
        shipping_detail = shipping_detail+'\n'+item
        
    product_quantity = 1
    header_descritpion = client_name + '\n' + job_name + '\n' + 'Quote:'+pattison_quote + '\n' + 'PWO#:' + work_order_number
    customer_name = 'jjg corp.'
    
    #Defining Request header
    headers = {
        "Authorization": "Zoho-oauthtoken "+access_token,
        "X-com-zoho-invoice-organizationid": "708754792"
    }

    #Finding Contact id
    count = 1
    found_contact = False
    contact_id = ''

    while True:
        resp = requests.get(headers=headers,url='https://invoice.zoho.com/api/v3/contacts?page='+str(count))
        customer_list = resp.json()['contacts']
        for item in customer_list:
            if(item['customer_name'].lower().strip() == customer_name):
                contact_id = item['contact_id']
                found_contact = True
        count=count+1
        if((resp.json()['page_context']['has_more_page']==False) | (found_contact==True)):
            break

    



    #--Field Values--#
    custom_fields = [{"label":"Misc Customer Notes","value": misc_notes},{"label":"Ticket","value":ticket_no}]
    customer_id = contact_id
    x = datetime.datetime.now()
    date = str(x).split(' ')[0]
    #date = pdf_due_date
    global line_item;
    line_item = [
        {
            "item_id": "",
            "rate": 0,
            "description":header_descritpion,
            "quantity":1
        }
        ]
    
    final_json_string = {
        "reference_number":purchase_order_no,
        "customer_id":customer_id,
        "date":date,
        "line_items":line_item,
        "custom_fields":custom_fields
    }

    resp = requests.post(headers = headers,url = 'https://invoice.zoho.com/api/v3/invoices', data = {"JSONString" : str(final_json_string)})
    
    invoice_details = resp.json();

    #print(invoice_details)

    line_item = [
        {
            "item_id": "",
            "rate": 0,
            "description":header_descritpion,
            "quantity":1
        }
        ]

    #Finding Quantity
    global check_product_name
    global quantity_values
    global design_values
    quantity_values = []
    design_values = []
    
    design_sorted = OrderedDict(sorted(designs.items(),key = lambda x: getitem(x[1], 'Invoice Code')))
    
    for design in design_sorted.values():
        design_values.append(design['Invoice Code'].lower())
        quantity_values.append(design['quantity'])
                          

    #Finding Product id
    #print(design_values,quantity_values)
    check_product_name = ''
    global index
    index = 0
    global unmapped_design
    global unmapped_product
    unmapped_design = []
    unmapped_product = []
    
    
    for design in design_sorted.values():
        product_name = design['Invoice Code'].lower()
        if(product_name==''):
            unmapped_design.append(design['Design'])
            continue
        count = 1
        found_product = False
        global product_id;
        product_id = ''
        if(product_name == check_product_name):
            if(product_name in unmapped_product):
                unmapped_design.append(design['Design'])
                continue
            index = index + 1
            line_item_json = {
                "item_id": 2174584000000327539,
                "rate": 0,
                "description":invoice_details['invoice']['invoice_number']+'-'+str(index)+'-'+design['Design'],
                "quantity":design['quantity']
                }
            line_item.append(line_item_json)    
        else:
            while True:
                resp = requests.get(headers=headers,url='https://invoice.zoho.com/api/v3/items?page='+str(count))
                product_list = resp.json()['items']
                for item in product_list:
                    if(item['name'].lower().strip() == product_name):
                        product_id = item['item_id']
                        found_product = True
                count=count+1
                if((resp.json()['page_context']['has_more_page']==False) | (found_product==True)):
                    break
            
            if(product_id == ''):
                unmapped_product.append(product_name)
                unmapped_design.append(design['Design'])
                continue

            index_values = []
            index_values = [i for i, x in enumerate(design_values) if x == product_name]

            global quantity_total
            quantity_total = 0
            for item in index_values:
                quantity_total = quantity_total + quantity_values[item]

            line_item.append({
                "item_id": product_id,
                "rate": design['Total Cost'],
                "quantity": quantity_total
                })
            index = index + 1
            line_item_json = {
                "item_id": 2174584000000327539,
                "rate": 0,
                "description":invoice_details['invoice']['invoice_number']+'-'+str(index)+'-'+design['Design'],
                "quantity":design['quantity']
                }
            line_item.append(line_item_json);    
            check_product_name = product_name         
                      

    shipping_json = {
        "item_id": 2174584000000327593,
        "rate": 0,
        "description":shipping_detail,
        "quantity":1
        }
    line_item.append(shipping_json)   
    unmapped_design_string = ''
    for item in unmapped_design:
        unmapped_design_string = unmapped_design_string + '\n' + item

    custom_fields = [{"label":"Misc Customer Notes","value": misc_notes},{"label":"Ticket","value":ticket_no},{"label":"Unmapped Information","value":unmapped_design_string}]    
    update_json_string = {
        "line_items":line_item,
        "custom_fields":custom_fields

    }

    resp = requests.put(headers=headers,url='https://invoice.zoho.com/api/v3/invoices/'+invoice_details['invoice']['invoice_id'], data = {"JSONString" : str(update_json_string)})
    print('Success',resp.status_code)
    return invoice_details['invoice']['invoice_number']






    