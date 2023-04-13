# CO2Scrap
CO2Scrap is a handy Python script to collect and output carbon intensity and fossil fuel usage from different regions around the world. Currently, it only supports scrapping data from electricityMap through co2signal.com free API.

## Features
* The script supports country, region-specific, and (latitude, longitude) scrapping from co2signal.com
  * If using multiple-regions, only region/country-specific support is implemented. See TODO.
* Local's and Region's time are outputted, so the user can understand the differences across locations and time.
* It handles errors that may happen when querying co2signal.com, so only validated data samples are outputted.
* The ```--sleep``` feature can be used to wait for any amount of seconds between requests to avoid rate limiting errors.
  -  This avoids saturating co2signal.com servers and having yourself blocked from querying (in case you do not own multiple API tokens).
* It can also use multiple co2signal keys to multiplex tokens when gathering data for multiple regions at once.
 
 ## Requirements
 
 * [requests](https://pypi.org/project/requests/) package (use pip to install it)
 
## Usage

Visit https://co2signal.com, and sign up to acquire an API key.
Then, edit file ```tokens.json```, and include with the email address and API-key you have received. E.g.:

```json
[
        {
                "user": "username@email.com",
                "token": "Include-Your-Own-Token"
        }
]
```

The script automatically reads ```tokens.json``` to authenticate you with co2signal.com, but other file can be given by setting the ```--auth-tokens``` argument. Multiple tokens can be included in the tokens JSON file.

Then, you can collect data for one country as:

```python3 co2scrap.py --country-zone BR-CS```

The output follows the order

```timestamp,zone_datetime,status,zone_name,carbon_intensity_avg,carbon_intensity_unit,fossilFuelPercentage```

Where:
- *timestamp*: Local epoch timestamp
- *zone_datetime*: Region's (e.g., BR-CS) local time (in UTC)
- *status*: Sample status. We currently only output "ok" values.
- *zone_name*: Region's zone name.
- *carbon_intensity_avg*: The average carbon intensity value in the region.
- *carbon_intensity_unit*: The average carbon intensity's unit (in gCO2Eq/kWh).
- *fossilFuelPercentage*: The fossil fuel percentage used to power the region.

An output instance:

```1633671339,2021-10-08T05:00:00.000Z,ok,BR-CS,243,gCO2eq/kWh,32.62```

* The script can read a JSON file to collect data for more than one region at a time. This is done through the ```--regions-file``` option. The JSON file passed through it has to be formatted as in the example below (for two regions):

```json
[
	{
		"provider": "mass",
		"name": "MASSACHUSETTS",
		"full_name": "Commonwealth of Massachusetts",
		"code": "mass-1",
		"public": false,
		"country_code": "US-NE-ISNE",
	},
	{
		"provider": "iceland",
		"name": "Iceland",
		"full_name": "Iceland",
		"code": "iceland-1",
		"public": false,
		"country_code": "IS",
	}
]
 ```
 API and script error logs are output in the terminal and can be redirected directly to a file for further analysis. Use ```>>``` bash/zsh command when executing ```co2scrap.py```, e.g.,

```python3 co2scrap.py --regions-file regions.json --output_dir zones/ >> co2scrap.log 2>&1```

This way, regional information are read from the ```regions.json``` file, the requests are made to co2signal.com, and the data values are stored in the ```zones/``` directory as CSVs. Any error logs are stored in the ```co2scrap.log``` file. Storing data without using ```--regions-file``` option is not yet supported. We have written a simple [cronjob configuration](co2scrap_regions.cron), so you can have cron [automatically](https://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/) calls the script at times.

* To see all other available options:
   ```bash
   python3 co2scrap.py --help
   
   usage: co2scrap.py [-h] [--auth-tokens AUTH_TOKENS] [--regions-file REGIONS]
                [--output_dir OUTPUT_DIR]
                [--country-zone COUNTRY [COUNTRY ...]] [--lon LONGITUDE]
                [--lat LATITUDE] [--api_url API_URL] [--sleep SLEEP]
   ```

## Notes

Currently, co2signal.com sets a limit of 30 requests per-hour, regardless of what region you collect data for. When using the ```--regions-file``` option, having too many regions in the file may cause multiple API errors due to the rate limit. In these cases, you want to use the ```--sleep``` feature and properly time requests. It is also possible to acquire multiple co2signal.com tokens, and adding them into ```tokens.json```, in which case the CO2Scrap script will round-robin them.

Visit the [CO2signal website](https://api.electricitymap.org/v3/zones) to check all available zones as of today.
Their API is free for non-commercial use. Reach them out if you plan to commercialise it.

## TODO
- [ ] Support (lattitude, longitude) directly in a region's JSON file.
- [ ] Implement a notification feature that calls user-specified external script(s) every time new energy values are successufully retrieved.
- [ ] Support other data providers, e.g., [WattTime](https://www.watttime.org/api-documentation) or Singularity.
