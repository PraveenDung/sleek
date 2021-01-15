from flask import Flask, request, Response
import requests
from main import main_process
import csv

app = Flask(__name__)

@app.route('/webhook', methods=['GET','POST'])
def respond():
    #print(request.json);
    ticket_detail = request.json
    
    if(ticket_detail[0]['payload']['firstThread']['author']['name'].lower()=='qualyval test'):
        with open('log.csv', mode='a+', newline='') as log:
            log_writer = csv.writer(log, delimiter=',')
            try:
                ticket_no = str(ticket_detail[0]['payload']['ticketNumber'])
                invoice_no = main_process(ticket_detail)
                in_arr = [ticket_no,invoice_no,'Success','None']
                log_writer.writerow(in_arr)
            except Exception as e:
                try:
                    ticket_no = str(ticket_detail[0]['payload']['ticketNumber'])
                    in_arr = [ticket_no,'','Fail',str(e)]
                    log_writer.writerow(in_arr)
                except:
                    pass    
    return Response(status=200)

if __name__=='__main__':
    app.run();  



