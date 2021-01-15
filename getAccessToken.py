import requests

#Defining global variables
#Grant_Token-1000.221e5c980b51041fce3c242c65d7baf8.a33a943c0e8dc03425ca52b20deda29b
#Scope-Desk.tickets.All,ZohoInvoice.invoices.All,ZohoInvoice.contacts.All,ZohoInvoice.settings.All
refresh_token = '1000.6e978bc62a8ed872c193f4e222960f46.95d1217ef4f59808b6921ef352fe9304'
client_id = '1000.CWA8XPLJA8NEAZSQJ8VEHQQ8R92NNV'
client_secret = '7c33e1e63941c3c7a53c8492dcdf9956389a72fdee'

def AccessToken():
    #Refreshing access token
    resp = requests.post(url="https://accounts.zoho.com/oauth/v2/token?refresh_token="+refresh_token+"&client_id="+client_id+"&client_secret="+client_secret+"&redirect_uri=http://www.zoho.com/invoice&grant_type=refresh_token")
    access_token = resp.json()['access_token']
    return access_token

