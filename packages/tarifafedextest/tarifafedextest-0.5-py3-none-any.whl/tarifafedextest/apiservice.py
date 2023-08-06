from urllib import request
import requests
from  tarifafedextest.settings import URL_API_FEDEX
import xml.etree.ElementTree as ET
class ApiService:

    def post(self,data):

        headers = {'Content-Type': 'application/xml'}
        return requests.post(URL_API_FEDEX,data = ET.tostring(data),headers = headers) 
        
        