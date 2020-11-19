#!/usr/bin/env python
import sys
import os
import logging
import ConfigParser
import argparse
from tpc_utils import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("source", help="Source URL")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    url = args.source
    if not "https" in url:
        print("ERROR: URL has to start with https")
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
    macaroon = tpc_util.request_macaroon(url, "READ_METADATA,DOWNLOAD,LIST")

    if macaroon:
        log.debug(macaroon)
    else:
        log.info("no macaroon found, using x509 instead")
    
    adler32 = tpc_util.get_adler32(url, macaroon)

    if adler32:
       log.info(adler32)
    else:
       log.error("no checksum returned")


log = logging.getLogger()    
if __name__ == "__main__":
    main()
