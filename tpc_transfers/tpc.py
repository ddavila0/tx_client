# This script is used to cook curl commands that will perform actions similar to those in a Third Part Copy transfer
# done through FTS: request macaroon, download file, upload file, copy, get checksum, etc.

# TODO:
# * validatex509 credentials
# * Check that extract_macaroon works when curl_debug =1
# - automatic suffix 
# - trigger parallel transfers
# - verify with checksum
# - add an arg parser
#   -- pass x509 cert and key as arguments
#   -- pass source and dest enpoint as arguments

import sys
import argparse
import logging
import time
import subprocess
import pdb
import datetime
from multiprocessing import Process, Value, Lock
from tpc_utils import *

#pdb.set_trace()

def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    # Timeout in seconds for the various operations (curl's -m argument), e.g., tpc, download_file, get_checksum
    timeout = 900
    proxy= "/tmp/x509up_u0"
    url_src = sys.argv[1]
    url_dst = sys.argv[2]
    #-------------------------------------------------------------------------------

    tpc_util = TPC_util(log, timeout, curl_debug, proxy)
    
    log.info("Making TPC: "+url_src+" -> "+url_dst)
    # Get macaroons
    log.info("Requesting macaroons")
    macaroon_src = tpc_util.request_macaroon(url_src, "DOWNLOAD,DELETE,LIST")
    macaroon_dst = tpc_util.request_macaroon(url_dst, "UPLOAD,DELETE,LIST")
    
    # Start TPC
    log.info("Starting transfer")
    res = tpc_util.tpc(url_src, macaroon_src, url_dst, macaroon_dst)

    # Get Checksum 
    if(res == 0):
        log.info("Getting checksums")
        adler32_src = tpc_util.get_adler32(url_src, macaroon_src)
        adler32_dst = tpc_util.get_adler32(url_dst, macaroon_dst)

        if((adler32_src is None) or (adler32_dst is None)):
            log.error("Could not get one of the adler32s")

        elif(adler32_src == adler32_dst):
            log.info("adler32 matches")
        else: 
            log.error("adler32 doesn't match")
            log.error("adler32_src: "+adler32_src)
            log.error("adler32_dst: "+adler32_dst)

log = logging.getLogger()    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
