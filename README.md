# Covid Vaccine Availability Notification
This tool is built off of [vaccinespotter](https://vaccinespotter.org) and will send you notifications when
vaccine appointments become available in your area.

## Upcoming Work
- UI to register and manage notification preferences
- Add API to register/unregister for notifications
- Create DynamoDB table to handle looking up people to notify
- Testing


## Engineering Notes
* Vaccine Spotter API is crawled once every 5 minutes
* Data processing pipeline does a diff on the data and the sends out emails based on users notification
preferences

### DynamoDB
* Partition Key: `<zip code>+<notification distance>`
* Range Key: `email`

### Notifications
* Emails sent using AWS SES
* Each email has a **manage notifications** presigned url in it that will allow a user to go to the website and manage 
their notifications

### Vaccine Spotter API
* features: a list of vaccination locations
* metadata: 
    - bounding_box: bounding box for state
    - provider_brands: brands available in the state
    - appointments_last_fetched: datetime of last fetch
```json
{
  "type": "FeatureCollection",
  "features": [ 
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [
          -149.9182363,
          61.1941966
        ]
      },
      "properties": {
        "id": 1047547,
        "url": "https://www.albertsons.com/pharmacy/covid-19.html",
        "city": "Anchorage",
        "name": "Carrs 1805",
        "state": "AK",
        "address": "1650 W. Northern Lights Blvd.",
        "provider": "albertsons",
        "time_zone": "US/Alaska",
        "postal_code": "99517",
        "appointments": [],
        "provider_brand": "carrs",
        "carries_vaccine": true,
        "appointment_types": {},
        "provider_brand_id": 17,
        "provider_brand_name": "Carrs",
        "provider_location_id": "1600114786078",
        "appointments_available": false,
        "appointment_vaccine_types": {},
        "appointments_last_fetched": "2021-03-31T05:12:13.791+00:00",
        "appointments_available_all_doses": false,
        "appointments_available_2nd_dose_only": false
      }
    }
  ]  
}
```