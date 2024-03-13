#!/bin/python
import os
import argparse
import csv
from urllib import request

# To fetch the value of 'charset' from 'Content-Type' header in the Response
from email.message import Message

examples = """
Examples:
[+] python3 scope-grabber.py -p paypal
[+] python3 scope-grabber.py -p paypal -b
"""

parser = argparse.ArgumentParser(
    description="Automating the boring stuff in Bug Bounty.",
    epilog=examples,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument(
    "-p",
    dest="program",
    type=str,
    required=True,
    help="The program name as it's registered in HackerOne."
)

parser.add_argument(
    "-o",
    dest="output",
    type=str,
    help="The output path for the folder."
)

parser.add_argument(
    "-b",
    action="store_const",
    const=True,
    help="If enabled, downloads the Burp Suite config file of the program."
)

headers = {
    "Accept": "text/html",
    "Accept-Language": "en-GB,en",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "DNT": "1",
}

timeout = 5

def download_burp_suite_config_file(program):
    url = f"https://hackerone.com/teams/{program}/assets/download_burp_project_file.json"
    request.urlretrieve(url, f"{path}/{program}/burp_config.json")
    
def download_scope_csv(program, csv_file):
    url = f"https://hackerone.com/teams/{program}/assets/download_csv.csv"

    req = request.Request(url, headers=headers)
    resp = request.urlopen(req, timeout=timeout)

    m = Message()
    m["Content-Type"] = resp.getheader("Content-Type")

    charset = m.get_param("charset")

    data = resp.read()

    html = data.decode(charset)

    with open(f"{path}/{program}/{csv_file}", "w") as f:
        f.write(html)


def parse_csv(csv_file):
    urls = list()

    with open(f"{path}/{program}/{csv_file}", "r") as f:
        csv_reader = csv.DictReader(f)
        itercsv = iter(csv_reader)

        # Skip the headers
        next(itercsv)

        for row in itercsv:
            if row["asset_type"] == "URL" or row["asset_type"] == "WILDCARD":
                urls.append(row["identifier"])

    with open(f"{path}/{program}/URLs.txt", "w") as f:
            f.write("\n".join(urls))

if __name__ == "__main__":
    args = parser.parse_args()

    program = args.program
    csv_file = f"scope.csv"

    if args.output:
        path = args.output
    else:
        path = "."

    if not os.path.exists(f"{path}/{program}"):
        os.mkdir(f"{path}/{program}")

    try:
        download_scope_csv(program, csv_file)
        parse_csv(csv_file)

        if args.b:
            download_burp_suite_config_file(program)
    except TimeoutError:
        print("Timed out")
    except StopIteration:
        print(f"This program does not have a Scope CSV file. You can instead examine their profile on HackerOne: https://hackerone.com/{program}")
