# User imports
from core.Utils import *
from core.Bear import *
from core.Extractor import *
from core.C2xml import *
from core.Descriptions import *

# Default imports 
import argparse
import logging
import os

def usage():
    log_error("Run: python ", __file__, "--help", ", to know the correct usage.")
    sys.exit(-1)

def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Sys2Syz : A Utility to convert Syscalls and Ioctls to Syzkaller representation")

    parser.add_argument("-t", "--target", help="target file to generate descriptions for", type=str, required=True)
    parser.add_argument("-c", "--compile-commands", help="path to compile_commands.json", type=str, required=True)
    parser.add_argument("-v", "--verbosity", help="make Griller spit more things out", action="count")
    args = parser.parse_args()

    verbose = args.verbosity

    if args.verbosity == 1:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    
    elif args.verbosity == 2:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

    if args.target is None:
        usage()
    target = os.path.realpath(args.target)
    Utils.dir_exists(target, True)
    logging.info("[+] The target file is %s", target)

    if args.compile_commands is None:
        usage()
    compile_commands = os.path.realpath(args.compile_commands)
    Utils.file_exists(compile_commands, True)
    logging.info("[+] The compile commands is %s", compile_commands)

    #Extract ioctl commands from dev header files
    extractor = Extractor(target)
    header_files = extractor.get_header_files()
    ioctl_cmd_file, cmd_header_files = extractor.get_ioctls(header_files)
    logging.info("[+] Extracted ioctl commands")

    if ioctl_cmd_file is not None:
    #Generate preprocessed files
        bear = Bear(target, compile_commands, verbose)
        check_preprocess = bear.parse_compile_commands()
        if check_preprocess:
            logging.info("[+] Preprocessed files have been generated")
            #Generate xml files using c2xml and preprocessed files
            c2xml = C2xml(target)
            out_dir = c2xml.run_c2xml()
            logging.info("[+] Created XML files")
            descriptions = Descriptions(out_dir)
            descriptions.run(ioctl_cmd_file)
            output_path = descriptions.make_file(cmd_header_files)
            if Utils.file_exists(output_path, True):
                logging.info("[+] Description file: " + output_path)
    else:
        logging.info("[+] Exiting, ioctl call don't exist")
        exit(0)
        

if __name__ == "__main__":
    main()