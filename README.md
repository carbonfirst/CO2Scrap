# co2signal_api
A handy Python script to collect carbon intensity and fossil fuel usage from electricityMap through co2signal.com.

## Features
* The script supports country and region-specific, and (latitude, longitude) scrapping from co2signal.com
 * If using multiple-regions, only region/country-specific support is implemented. See TODO.

* It handles errors that may happen when querying co2signal.com 
* It can also use multiple co2signal keys for multiplexing multiple regions to avoid request limiting errors.
 * See tokens.json
 
 ## Requirements
 
 * Python3
 * requests packages (use pip to install it)
 
## Usage

Visit https://co2signal.com and sign up to acquire their API keys. We suggest acquiring a couple of keys in order to avoid request limiting errors (currently set at 30 requests per-hour).

Then, edit the file tokens.json with the email address and API-key you have received.

* To see all available options:
   python3 co2_signal.py --help

## TODO
* Support (lattitude, longitude) directly in JSON
* Support other providers, e.g., WattTime
