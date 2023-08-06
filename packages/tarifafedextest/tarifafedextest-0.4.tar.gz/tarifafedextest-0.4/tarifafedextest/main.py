from cotizatarifa import CotizaTarifa
import json

ct = CotizaTarifa()

credentials = json.dumps(
    {
        "Key":"bkjIgUhxdghtLw9L",
        "Password":"6p8oOccHmDwuJZCyJs44wQ0Iw",
        "AccountNumber":"510087720",
        "MeterNumber":"119238439",
        "LanguageCode":"es",
        "LocaleCode":"mx"
    }
)



quote_params = json.dumps({
    "address_from": {
        "zip": "64000",
        "country": "MX"
    },
    "address_to": {
        "zip": "64000",
        "country": "MX"
    },
    "parcel": {
        "length": 25.0,
        "width": 28.0,
        "height": 46.0,
        "distance_unit": "cm",
        "weight": 6.5,
        "mass_unit": "kg"
    }

})



print(ct.get(credentials,quote_params))


