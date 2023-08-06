#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from yaml import safe_load_all

from .processor import Processor

# from Blender repository apparently
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = """Virtual machine of ic10 processor. Intended to test scripts."""
    )

    parser.add_argument(
        "code", 
        type=str, 
        help="Input file with ic10-mips."
    )

    parser.add_argument(
        "--env", "-e",
        type=str,
        default=None,
        help="""File dictating propertys of attached devices and expected reactions 
        from the ic10-processor after game tick(s)."""
    )

    parser.add_argument(
        "--watchregs", "-r",
        type=str,
        nargs="+",
        default=[],
        help="Registers to be logged, seperated by spaces."
    )

    parser.add_argument(
        "--watchstack", "-s",
        type=int,
        nargs="+",
        default=[],
        help="Stack addresses to be logged, seperated by spaces."
    )

    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=False,
        help="Run as a debugger."
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        default=False,
        help="Show register usage statistics."
    )
    
    parser.add_argument(
        "--end_values", "-v",
        action="store_true",
        default=False,
        help="Show register, device and stack values at the end of execution if value != 0."
    )

    args = parser.parse_args()
    
    with open(args.code, "r") as f:
        code = f.read()
    if args.env is not None:
        with open(args.env, "r") as f:
            inputs, outputs = safe_load_all(f.read())
    else:
        inputs, outputs = [], []

    if inputs is None:
        inputs = []
    if outputs is None:
        outputs = []

    proc = Processor(code)
    tick = 0
    # TODO: batch devices (id as key and enumerate multiple devices)
    # TODO: slots (number as key)
    # TODO: reagants
    def set_devices(cur_inputs):
        for dev, settings in cur_inputs.items():
            for setting, value in settings.items():
                proc._devices[dev][setting] = value
                # print(f"Updating {dev}.{setting} -> {value}.")
    
    def check_devices(cur_outputs):
        for dev, settings in cur_outputs.items():
            for setting, value in settings.items():
                # print(f"Testing {dev}.{setting}, expect {value}.")
                if proc._devices[dev][setting] != value:
                    print(f"Test of {args.code} in environment {args.env} {bcolors.FAIL}FAILED{bcolors.ENDC} on tick {tick}! {dev}.{setting} \
has the wrong value expected {value} got {proc._devices[dev][setting]}.")
                    return False
        return True
    
    inp_i = 0  # inputs sets BEFORE tick
    outp_i = 0  # also starts at 0 since outputs checked AFTER tick
    if inputs:
        if isinstance(inputs[inp_i], int):
            if inputs[inp_i] <= 0:
                inp_i += 1  
                # in case inputs start with: - 0
                set_devices(inputs[inp_i])
                inp_i += 1
            else:
                inputs[inp_i] -= 1  # decrease until tick reached
        else:
            set_devices(inputs[inp_i])
            inp_i += 1

    for _ in proc.run():
        tick+=1
        while outp_i < len(outputs):
            if isinstance(outputs[outp_i], int):
                if outputs[outp_i] <= 0:
                    outp_i += 1
                    continue  # this way multiple wait statements supported
                else:
                    outputs[outp_i] -= 1  # decrease until tick reached
                    break
            else: 
                if not check_devices(outputs[outp_i]):
                    sys.exit(-1)  # terminal interface
                outp_i += 1
                break

        # inputs for next tick must come after outputs 
        while inp_i < len(inputs):
            if isinstance(inputs[inp_i], int):
                if inputs[inp_i] <= 0:
                    inp_i += 1
                    continue  # this way multiple wait statements supported
                else:
                    inputs[inp_i] -= 1  # decrease until tick reached
                    break
            else:
                set_devices(inputs[inp_i])
                inp_i += 1
                break

    # TODO: test ended before all ouputs evaluated -> test failed
    # TODO: end test if no more outputs present
    # TODO: interactive mode with optional tests
    if args.end_values:
        print("Registers:")
        for name, idx in Processor.register_translation.items():
            if proc._registers[idx] != 0: 
                print(f"{name}={proc._registers[idx]}")
        print()
        print("Devices:")
        for dev, values in proc._devices.items():
            if values:
                print(dev+" :", values)
        print()
        print("Stack:")
        for idx, value in enumerate(proc._stack):
            if value:
                print(f"At {idx} :", value)

    if args.env is not None:
        print(f"Test of {args.code} in environment {args.env} {bcolors.OKGREEN}PASSED{bcolors.ENDC}.")
