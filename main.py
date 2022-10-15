#!/usr/bin/python3
import subprocess
import threading
import argparse
import blessed
import os 
import sys
import time


def validate_args(args):
    args.method = args.method.lower()
    try:
        args.threads = int(args.threads)
    except:
        print(f"{t.red}[-] Thread count has to be an integer{t.normal}")
        sys.exit(1)
    if args.arachni_location.endswith("/"):
        args.arachni_location = args.arachni_location[:-1]
    if args.method == "file" and not os.path.isfile(args.file):
        print(f"{t.red}[-] File \"{args.file}\" doesn't exist{t.normal}")
        sys.exit(1)
    if args.method != "file" and args.method != "pipe":
        print(f"{t.red}[-] \"{args.method}\" is not a valid method.{t.normal}")
        sys.exit(1)
    if not os.path.isdir(args.arachni_location):
        print(f"{t.red}[-] Invalid arachni root directory \"{args.arachni_location}\"{t.normal}")
        sys.exit(1)
    if not os.path.isdir(args.output):
        print(f"{t.red}[-] Invalid output dir \"{args.output}\"{t.normal}")
        sys.exit(1)


def get_urls(args):
    urls = []
    if args.method == "file":
        urls = open(args.file).read().split("\n")
    if args.method == "pipe":
        urls = sys.stdin
    urls = {u:None for u in urls}.keys()
    return urls

def scan_thread(url):
    global running
    process = subprocess.Popen([f'{args.arachni_location}/bin/arachni', url, '--report-save-path', args.output], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    running -= 1

def main(args):
    global running
    running = 0
    urls = get_urls(args)
    for i,url in enumerate(urls):
        url = url.strip()
        while running >= args.threads:
            time.sleep(0.1)
        print(f"{t.green}[+]Scanning {url} ({i}/{len(urls)}){t.normal}{' ' * 20}")
        threading.Thread(target=scan_thread, args=(url,)).start()
        running += 1

    while running != 0:
        print(f"{t.blue}[i] Waiting for threads to stop.{t.normal}", end="\r")
        time.sleep(0.2)

    print(f"\n{t.green}[🚩]All scans done!{t.normal}")
        
t = blessed.Terminal()
parser = argparse.ArgumentParser()
parser.add_argument('-m', '--method', help="Method to get urls (pipe,file).", required=True)
parser.add_argument('-f', '--file', help="File to read urls from (used with -m file option).", default="None")
parser.add_argument('-a', '--arachni-location', help="Arachni root directory (for example /home/user/Downloads/arachni).", required=True)
parser.add_argument('-t', '--threads', help="How many threads will be used to scan urls.", default='2')
parser.add_argument('-o', '--output', help="Directory to put scan results in", default="output")
args=parser.parse_args()
validate_args(args)
main(args)
