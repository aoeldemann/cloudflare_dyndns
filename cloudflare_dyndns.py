"""Update Cloudflare DNS A-record with current public IPv4 address."""
import logging
import json
import urllib.parse
import sys
import requests


def error(msg):
    """Print out error message and exit."""
    logging.error("ERROR: %s", msg)
    sys.exit(-1)


def get_ipv4(api_endpoint):
    """Get and return IPv4 address."""
    try:
        # call api
        response = requests.get(api_endpoint)

        # parse json response
        response = response.json()
    except requests.exceptions.RequestException:
        # something went wrong, don't have an IP to return
        return None

    # was IP provided in response?
    if "ip" not in response:
        error("invalid IPv4 API response")

    # extract IP from response and return
    return response["ip"]


def main():
    """Main function."""
    # set up logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    # read json config
    try:
        with open("config.json") as config_file:
            config = json.loads(config_file.read())
    except IOError:
        error("failed to open config.json configuration file")
    except json.decoder.JSONDecodeError:
        error("failed to parse config.json configuration file")

    # what configuration options are required?
    required_config_opts = ["api_endpoint_ipv4",
                            "api_endpoint_cloudflare",
                            "cloudflare_token",
                            "cloudflare_zone_id",
                            "cloudflare_record_id",
                            "cloudflare_record_name"]

    # got all the configuration options?
    for opt in required_config_opts:
        if opt not in config:
            error("missing configuration in config.json: '%s'" % opt)

    # get ipv4 address
    ipv4 = get_ipv4(config["api_endpoint_ipv4"])

    if ipv4 is None:
        error("could not obtain IPv4 address")

    # assemble cloudflare api authentication header
    headers = {
        "Authorization": "Bearer %s" % config["cloudflare_token"]
    }

    # assemble endpoint url
    endpoint = urllib.parse.urljoin(
        config["api_endpoint_cloudflare"], "zones/%s/dns_records/%s" %
        (config["cloudflare_zone_id"], config["cloudflare_record_id"]))

    # get dns record
    try:
        response = requests.request(
            "GET", endpoint, headers=headers)
    except requests.exceptions.RequestException:
        error("cloudflare API call failed")

    # parse json response
    response = response.json()

    # call successful?
    if response["success"] is False:
        error("cloudflare API reported error")

    if response["result"]["content"] == ipv4:
        # dns record is up to date. report status and exit
        logging.info("NO CHANGE: %s - %s",
                     config["cloudflare_record_name"], ipv4)
        return

    # assemble data to post to cloudflare api to update dns entry
    data = {"type": "A",
            "name": config["cloudflare_record_name"], "content": ipv4}

    # perform api request
    try:
        response = requests.request(
            "PUT", endpoint, headers=headers, json=data)
    except requests.exceptions.RequestException:
        error("cloudflare API call failed")

    # parse json response
    response = response.json()

    # call successful?
    if response["success"] is False:
        error("cloudflare API reported error")

    # report status
    logging.info("UPDATED: %s - %s", config["cloudflare_record_name"], ipv4)


if __name__ == "__main__":
    main()
