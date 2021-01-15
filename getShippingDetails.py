import os
from ReadPDF import getPDF

'''
for item in os.listdir('./Shipping Details'):
    getPDF('./Shipping Details/'+item,'./Shipping Details/'+os.path.splitext(item)[0]+".txt")

'''

def getShippingDetails(input_text):
    values = input_text.split('\n\n')
    shipping_details = []
    for item in values:
        shipping = item.split('\n')
        if(len(shipping)>4):
            validate_second_line = shipping[0].split(' ')
            validate_second_line = list(filter(None, validate_second_line))
            if(validate_second_line[len(validate_second_line)-1]=='-'):
                shipping_details.append(shipping[0]+shipping[1])
            else:
                shipping_details.append(shipping[0])  
    
    return shipping_details    

def ShippingDetails(shipping_details_file):
    with open(shipping_details_file,'r') as shipping_file:
        shipping_details = getShippingDetails(shipping_file.read())
        return shipping_details;
               

