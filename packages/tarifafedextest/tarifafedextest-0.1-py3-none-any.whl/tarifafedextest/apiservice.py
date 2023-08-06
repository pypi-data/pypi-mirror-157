from urllib import request
import requests
import settings
import xml.etree.ElementTree as ET
class ApiService:

    def post(self,data):

        headers = {'Content-Type': 'application/xml'}
        return requests.post(settings.URL_API_FEDEX,data = ET.tostring(data),headers = headers) 
        
        