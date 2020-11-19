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

def make_transfer(tpc_util, url_src, url_dst, file_src, log_lock):
    res = -1
    log.info("Making TPC: "+url_src+" -> "+url_dst)
    # Get macaroons
    log.info(file_src +" Requesting macaroons")
    macaroon_src = tpc_util.request_macaroon(url_src, "DOWNLOAD,DELETE,LIST")
    macaroon_dst = tpc_util.request_macaroon(url_dst, "UPLOAD,DELETE,LIST")
    
    # Start TPC
    log.info(file_src +" starting transfer")
    res = tpc_util.tpc(url_src, macaroon_src, url_dst, macaroon_dst)
    log.info(file_src +" transfer done, res: "+str(res))
   
    # Get Checksum 
    if(res == 0):
        adler32_src = tpc_util.get_adler32(url_src, macaroon_src)
        adler32_dst = tpc_util.get_adler32(url_dst, macaroon_dst)

        if((adler32_src is None) or (adler32_dst is None)):
            log.error("Could not get one of the adler32s")
            res = 1

        elif(adler32_src == adler32_dst):
            log.info(file_src+" adler32 matches")
        else: 
            log.error(file_src+" adler32 doesn't match")
            log.error(file_src+" adler32_src: "+adler32_src)
            log.error(file_src+" adler32_dst: "+adler32_dst)
            res = 1
    return res 

def main():
    #----- Config ----------------------------------------------------------------
    curl_debug = 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    # Total number of transfers
    total_transfers = 4
    # Number of transfers to be done in parallel
    num_parallel_transfers = 4
    # Time between transfers
    time_between_tx = 30
    # Suffix for destination file. Destination file is same as source file + suffix
    ts= datetime.date.today()
    ts= datetime.datetime.now()
    suffix = ts.strftime('_%Y%m%d-%H%M%S')
    # Timeout in seconds for the various operations (curl's -m argument), e.g., tpc, download_file, get_checksum
    timeout = 900
    #url_base_src = "https://xrootd.rcac.purdue.edu:1094/store/PhEDEx_LoadTest07/LoadTest07_Debug_Purdue/"
    #url_base_dst = "https://redirector.t2.ucsd.edu:1094//store/user/ddavila/LoadTest_purdue/"
    url_base_src = "https://cms-n000.rcac.purdue.edu:1094/store/PhEDEx_LoadTest07/LoadTest07_Debug_Purdue/"
    url_base_dst = "https://gftp-2.t2.ucsd.edu:1094//store/user/ddavila/LoadTest_purdue/"
    #-------------------------------------------------------------------------------

    tpc_util = TPC_util(log, timeout, curl_debug)
    
    load_tests_filename = sys.argv[1]
    log.debug("Reading list of files from: "+load_tests_filename)
    fd = open(load_tests_filename)

    # List of the LoadTest files samples, e.g. "LoadTest07_Purdue_3E"
    load_test_list =  fd.readlines()

    i = 0
    j = 0
    while(i < total_transfers):
        log_lock = Lock()
        process_list = []
        # only attempt 'num_parallel_transfers' if that doesn't get over 'total_transfers'
        if i + num_parallel_transfers > total_transfers:
            num_parallel_transfers = total_transfers - i

        # Create N parallel transfers where N = num_parallel_transfers
        for p in range(0, num_parallel_transfers):
            # If no more test files in the list, exite the 'while' loop
            if(j >= len(load_test_list)):
                i = total_transfer
                break
            file_src = load_test_list[j][:-1]
            file_dst = file_src + suffix
            url_src = url_base_src + file_src
            url_dst = url_base_dst + file_dst
            #url_src = "https://xrootd.rcac.purdue.edu:1094/store/temp/user/ddavila/hello-purdue-009"
            #url_dst = "https://redirector.t2.ucsd.edu:1094//store/user/ddavila/LoadTest_purdue/hello-purdue-009"+suffix
            p = Process(target=make_transfer, args=(tpc_util, url_src, url_dst, file_src, log_lock))
            p.start()
            process_list.append(p)
            j = j + 1

        # Wait for the parallel transfers to finish
        for p in process_list:
            p.join()
 
        i = i + num_parallel_transfers
        # Wait in between a set of parallel transfers and the next one
        # but only if there are more transfers to be done
        if i < total_transfers: 
            time.sleep(time_between_tx)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
