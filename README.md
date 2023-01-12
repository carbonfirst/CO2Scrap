# co2signal_api
A handy Python script to collect carbon intensity and fossil fuel usage from electricityMap.

## Features
* The script supports country and region-specific, and (latitude, longitude) scrapping from co2signal.com
 * If using multiple-regions, only region/country-specific support is implemented. See TODO.

* It handles errors that may happen when querying co2signal.com 
* It can also use multiple co2signal keys for multiplexing multiple regions to avoid request limiting errors.
 * See tokens.json

## TODO
* Support (lattitude, longitude) directly in JSON
* Support other providers, e.g., WattTime
