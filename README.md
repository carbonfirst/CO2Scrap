# co2signal_api
A handy Python script to collect carbon intensity and fossil fuel usage from electricityMap through co2signal.com.

## Features
* The script supports country, region-specific, and (latitude, longitude) scrapping from co2signal.com
  * If using multiple-regions, only region/country-specific support is implemented. See TODO.
* Local's and Region's time are store, so the user can understand the differences across regions and time
* It handles errors that may happen when querying co2signal.com, so only validated values are stored
* It can also use multiple co2signal keys for multiplexing regions querying and avoid request limiting errors.
  -  Edit ```tokens.json``` to use this feature
* Sleep feature to wait for a user-provided amount of seconds between requests
  -  This avoids saturating co2signal.com servers and having yourself blocked from querying
 
 ## Requirements
 
 * Python3
 * [requests](https://pypi.org/project/requests/) package (use pip to install it)
 
## Usage

Visit https://co2signal.com and sign up to acquire their API keys. We suggest acquiring a couple of keys in order to avoid request limiting errors (currently set at 30 requests per-hour).

Then, edit the file ```tokens.json``` with the email address and API-key you have received.

* To see all available options:
   ```
   python3 co2_signal.py --help
   ```

API and script error logs are output in the terminal and can be redirected directly to a file for further analysis. Use ```>>``` bash/zsh command when executing ```co2_signal.py```, e.g.,

```python3 co2_signal.py --regions-file cloud_regions.full.json --output_dir zones/ >> co2_signal.log 2>&1```

This way, regional information are read from the ```cloud_regions.full.json``` file, the energy values are stored in the ```zones/``` directory, and the error logs are stored in the ```co2_signal.log``` file.

## TODO
- [ ] Support (lattitude, longitude) directly in JSON
- [ ] Support other providers, e.g., [WattTime](https://www.watttime.org/api-documentation)
