import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from tarifafedextest.apiservice import ApiService
import requests
import xmltodict

class CotizaTarifa:

    #regresa la tarifa en base a los prametros recibidos.
    def get(self,credentials,quote_params):

        xml = self.changeJsonToXml(credentials,quote_params) 

        service = ApiService()
        req = service.post(xml)

        #Si no regresa un estatus 200, regresamos el error tal cual nos lo envio el api de fedex
        if req.status_code <200 or req.status_code > 299:
            return json.dumps(xmltodict.parse(req.content))
        else:
            try:
                return self.generateJsonResponse(req.content)
            except:
                return xmltodict.parse(req.content)

            

    #Generamos el json que se le regresara el la funcion get
    def generateJsonResponse(self,content):
    
        xmlreq = ET.fromstring(content)            
        jsonreq = xmltodict.parse(content)["RateReply"]["RateReplyDetails"]

        jsonresp = []            

        for j in jsonreq:
            jsonresaux = {}
            jsonresaux["price"] = j["RatedShipmentDetails"][0]["ShipmentRateDetail"]["TotalNetChargeWithDutiesAndTaxes"]["Amount"]
            jsonresaux["currency"] = j["RatedShipmentDetails"][0]["ShipmentRateDetail"]["TotalNetChargeWithDutiesAndTaxes"]["Currency"]
            jsonservice_level = {}

            jsonservice_level["name"] = j["ServiceType"].replace("_"," ").title()
            jsonservice_level["token"] = j["ServiceType"]            
            jsonresaux["service_level"] = jsonservice_level

            jsonresp.append(jsonresaux)

        return jsonresp

    #Creamos el XML que se enviara al servicio de Fedex
    def changeJsonToXml(self,credentials,quote_params):
        RateRequest = ET.Element("RateRequest",xmlns='http://fedex.com/ws/rate/v13')        
        WebAuthenticationDetail = ET.SubElement(RateRequest,"WebAuthenticationDetail")
        UserCredential = ET.SubElement(WebAuthenticationDetail,"UserCredential")
        ET.SubElement(UserCredential,"Key").text = json.loads(credentials)["Key"]
        ET.SubElement(UserCredential,"Password").text = json.loads(credentials)["Password"]

        ClientDetail = ET.SubElement(RateRequest,"ClientDetail")  
        ET.SubElement(ClientDetail,"AccountNumber").text = json.loads(credentials)["AccountNumber"]
        ET.SubElement(ClientDetail,"MeterNumber").text = json.loads(credentials)["MeterNumber"]
        
        Localization = ET.SubElement(ClientDetail,"Localization")  
        ET.SubElement(Localization,"LanguageCode").text = json.loads(credentials)["LanguageCode"]
        ET.SubElement(Localization,"LocaleCode").text = json.loads(credentials)["LocaleCode"]

        Version = ET.SubElement(RateRequest,"Version")  
        ET.SubElement(Version,"ServiceId").text = "crs"
        ET.SubElement(Version,"Major").text = "13"
        ET.SubElement(Version,"Intermediate").text = "0"
        ET.SubElement(Version,"Minor").text = "0"

        ET.SubElement(RateRequest,"ReturnTransitAndCommit").text = "true" 

        RequestedShipment = ET.SubElement(RateRequest,"RequestedShipment")
        ET.SubElement(RequestedShipment,"DropoffType").text = "REGULAR_PICKUP"
        ET.SubElement(RequestedShipment,"PackagingType").text = "YOUR_PACKAGING"

        Shipper = ET.SubElement(RequestedShipment,"Shipper")
        Address = ET.SubElement(Shipper,"Address")
        ET.SubElement(Address,"StreetLines").text = " "
        ET.SubElement(Address,"City").text = " "
        ET.SubElement(Address,"StateOrProvinceCode").text = "XX"
        ET.SubElement(Address,"PostalCode").text = json.loads(quote_params)["address_from"]["zip"]
        ET.SubElement(Address,"CountryCode").text = json.loads(quote_params)["address_from"]["country"]
        
        Recipient = ET.SubElement(RequestedShipment,"Recipient")
        AddressR = ET.SubElement(Recipient,"Address")
        ET.SubElement(AddressR,"StreetLines").text = " "
        ET.SubElement(AddressR,"City").text = " "
        ET.SubElement(AddressR,"StateOrProvinceCode").text = "XX"
        ET.SubElement(AddressR,"PostalCode").text = json.loads(quote_params)["address_to"]["zip"]
        ET.SubElement(AddressR,"CountryCode").text = json.loads(quote_params)["address_to"]["country"]
        ET.SubElement(AddressR,"Residential").text = "false"
        
        ShippingChargesPayment = ET.SubElement(RequestedShipment,"ShippingChargesPayment")
        ET.SubElement(ShippingChargesPayment,"PaymentType").text = "SENDER"

        ET.SubElement(RequestedShipment,"RateRequestTypes").text = "ACCOUNT"
        ET.SubElement(RequestedShipment,"PackageCount").text = "1"
        

        RequestedPackageLineItems = ET.SubElement(RequestedShipment,"RequestedPackageLineItems")
        ET.SubElement(RequestedPackageLineItems,"GroupPackageCount").text = "1"

        Weight = ET.SubElement(RequestedPackageLineItems,"Weight")
        ET.SubElement(Weight,"Units").text = "KG"
        ET.SubElement(Weight,"Value").text = "1"

        Dimensions = ET.SubElement(RequestedPackageLineItems,"Dimensions")
        ET.SubElement(Dimensions,"Length").text = "10"
        ET.SubElement(Dimensions,"Width").text = "10"
        ET.SubElement(Dimensions,"Height").text = "10"
        ET.SubElement(Dimensions,"Units").text = "CM"

        #print (self.prettify(RateRequest))
        return RateRequest


    
    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ET.tostring(elem, 'utf-8').decode('utf8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")



