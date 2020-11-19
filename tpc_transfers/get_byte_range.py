#!/usr/bin/env python
import sys
import os
import logging
import ConfigParser
import argparse
from pymacaroons import Macaroon, Verifier
from tpc_utils import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("source", help="Source URL")
    parser.add_argument("byte_start", help="First byte to download")
    parser.add_argument("byte_end", help="Last byte to download")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    url         = args.source
    byte_start  = args.byte_start
    byte_end    = args.byte_end

    if not "https" in url:
        log.error("URL has to start with https")
        sys.exit(1)
    #---------------------------------------------------------------------------

    #----- Config --------------------------------------------------------------
    # Set the logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    
    # Check that the configuration file exists
    if os.path.isfile(".config"):
        configParser = ConfigParser.RawConfigParser()
        configParser.read(".config")
        
        curl_debug = configParser.getint('all', 'curl_debug')
        proxy      = configParser.get('all', 'proxy')
        timeout    = configParser.getint('all', 'timeout')
    else:
        # If the .config file doesn't exist, set the defaults        
        curl_debug = 1
        proxy= "/tmp/x509up_u0"
        timeout = 120

    #---------------------------------------------------------------------------
   
    tpc_util = TPC_util(log, timeout, curl_debug, proxy)
    macaroon = tpc_util.request_macaroon(url, "DOWNLOAD,LIST")
    file_content = tpc_util.get_byte_range(url, macaroon, byte_start, byte_end)
    log.info("File content:\n"+file_content)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
