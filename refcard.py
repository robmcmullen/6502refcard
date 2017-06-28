#!/usr/bin/env python

""" Reference table generator that uses the formatting strings and opcode
tables from udis (the Universal Disassembler for 8-bit microprocessors by Jeff
Tranter) to perform pattern matching to determine the opcode and addressing
mode.

Copyright (c) 2016 by Rob McMullen <feedback@playermissile.com>
Licensed under the Apache License 2.0
"""
from __future__ import print_function

import os
import re
from collections import defaultdict

try:
    import cputables
except ImportError:
    raise RuntimeError("Generate cputables.py using cpugen.py before using")

# from UDIS source; but rather than requiring the entire udis package, just use
# this single variable for undocumented opcodes
flag_undoc = 128


import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


address_mode_order = {
    "6502": {
        'map': {'accumulator': 'implicit'},
        'order': [
            'implicit',
            'immediate',
            'zeropage',
            'zeropagex',
            'zeropagey',
            'absolute',
            'absolutex',
            'absolutey',
            'indirect',
            'indirectx',
            'indirecty',
            ],
        # generated from py65
        'cycles': [7, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 0, 4, 6, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0, 6, 6, 0, 0, 3, 3, 5, 0, 4, 2, 2, 0, 4, 4, 6, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0, 6, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 3, 4, 6, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0, 6, 6, 0, 0, 0, 3, 5, 0, 4, 2, 2, 0, 5, 4, 6, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0, 0, 6, 0, 0, 3, 3, 3, 0, 2, 0, 2, 0, 4, 4, 4, 0, 2, 6, 0, 0, 4, 4, 4, 0, 2, 5, 2, 0, 0, 5, 0, 0, 2, 6, 2, 0, 3, 3, 3, 0, 2, 2, 2, 0, 4, 4, 4, 0, 2, 5, 0, 0, 4, 4, 4, 0, 2, 4, 2, 0, 4, 4, 4, 0, 2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 3, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0, 2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 6, 0, 2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0],
        'extra_cycles': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
        'status_byte_header': "N,V,-,B,D,I,Z,C",
        'status_byte_empty': ",,,,,,,",
        'status_byte': {
"ADC": "N,V, , , , ,Z,C",
"AND": "N, , , , , ,Z, ",
"ASL": "N, , , , , ,Z,C",
"BIT": "N,V, , , , ,Z, ",
"BRK": " , , ,1, ,1, , ",
"CLC": " , , , , , , ,0",
"CLD": " , , , ,0, , , ",
"CLI": " , , , , ,0, , ",
"CLV": " ,0, , , , , , ",
"CMP": "N, , , , , ,Z,C",
"CPX": "N, , , , , ,Z,C",
"CPY": "N, , , , , ,Z,C",
"DEC": "N, , , , , ,Z, ",
"DEX": "N, , , , , ,Z, ",
"DEY": "N, , , , , ,Z, ",
"EOR": "N, , , , , ,Z, ",
"INC": "N, , , , , ,Z, ",
"INX": "N, , , , , ,Z, ",
"INY": "N, , , , , ,Z, ",
"JMP": " , , , , , , , ",
"JSR": " , , , , , , , ",
"LDA": "N, , , , , ,Z, ",
"LDX": "N, , , , , ,Z, ",
"LDY": "N, , , , , ,Z, ",
"LSR": "N, , , , , ,Z,C",
"NOP": " , , , , , , , ",
"ORA": "N, , , , , ,Z, ",
"PHA": " , , , , , , , ",
"PHP": " , , , , , , , ",
"PLA": "N, , , , , ,Z, ",
"PLP": "N,V, , ,D,I,Z,C",
"ROL": "N, , , , , ,Z,C",
"ROR": "N, , , , , ,Z,C",
"RTI": "N,V, , ,D,I,Z,C",
"RTS": " , , , , , , , ",
"SBC": "N,V, , , , ,Z,C",
"SEC": " , , , , , , ,1",
"SED": " , , , ,1, , , ",
"SEI": " , , , , ,1, , ",
"STA": " , , , , , , , ",
"STX": " , , , , , , , ",
"STY": " , , , , , , , ",
"TAX": "N, , , , , ,Z, ",
"TAY": "N, , , , , ,Z, ",
"TSX": "N, , , , , ,Z, ",
"TXA": "N, , , , , ,Z, ",
"TXS": " , , , , , , , ",
"TYA": "N, , , , , ,Z, ",
        },
    },
}

title_modes = {
    'implicit': 'implicit',
    'immediate': '#nn',
    'zeropage': '$nn',
    'zeropagex': '$nn,X',
    'zeropagey': '$nn,Y',
    'absolute': '$nnnn',
    'absolutex': '$nnnn,X',
    'absolutey': '$nnnn,Y',
    'indirect': '($nnnn)',
    'indirectx': '($nn,X)',
    'indirecty': '($nn),Y',
    'relative': '',
}

operands = dict(title_modes)
operands.update({
    'implicit': '',
})



def gen_csv(cpu_name, allow_undocumented=False):
    cpu = cputables.processors[cpu_name]
    lookup = address_mode_order[cpu_name]

    # Create the opcode lookup table keyed on opcode name, each entry
    # containing a dict entry for each addressing mode. The entries in that
    # dict contain the csv string including opcode value and the number of
    # bytes.
    #
    # d['ora'] = {
    #     'immediate': '$9,?,2',
    #     'inderectx': '$1,?,2',
    #       ...
    # }
    d = defaultdict(dict)
    table = cpu['opcodeTable']
    for opcode, optable in table.items():
        try:
            num_bytes, mnemonic, mode_name, flag = optable
        except ValueError:
            num_bytes, mnemonic, mode_name = optable
            flag = 0
        log.debug("%x: %s %s %d bytes, %x" % (opcode, mnemonic, mode_name, num_bytes, flag))
        if allow_undocumented or not flag & flag_undoc:
            mode_name = lookup['map'].get(mode_name, mode_name)
            d[mnemonic.upper()][mode_name] = "%02x,%d%s,%d," % (opcode, lookup['cycles'][opcode], "+" if lookup['extra_cycles'][opcode] > 0 else "", num_bytes)
        else:
            log.debug("Skipping %s %s" % (opcode, mnemonic))

    # for mnemonic in sorted(d.keys()):
    #     print(mnemonic)
    #     modes = d[mnemonic]
    #     for mode_name in order:
    #         if mode_name in modes:
    #             print("  ",mnemonic,operands[mode_name],modes[mode_name])

    create_csv(d, lookup, lookup['order'])
    create_relative_csv(d, lookup)

def create_relative_csv(d, lookup):
    header = "Opcode,Hex,,N,T,P"
    lines = [header]
    for mnemonic in sorted(d.keys()):
        mode_info = d[mnemonic]
        if 'relative' in mode_info:
            opcode, _ = mode_info['relative'].split(",",1)
            lines.append("%s,%s,,2,3,4" % (mnemonic, opcode))
    print("\n".join(lines))

def create_csv(d, lookup, order):
    main_csv = []
    implicit_csv = []
    compact_csv = []
    list_csv = []
    header = "Opcode,%s," % lookup['status_byte_header']
    implicit_csv.append(header + "Hex,C,B")
    main_header = "Opcode,%s," % lookup['status_byte_header']
    compact_header = "Opcode,%s," % lookup['status_byte_header']
    list_header = "Inst,%s,Op,Cyc,B" % lookup['status_byte_header']
    for mode_name in lookup['order']:
        main_header += "\"%s\",,," % (title_modes[mode_name])
        compact_header += "\"%s\",,," % (title_modes[mode_name])
    main_csv.append(main_header)
    compact_csv.append(compact_header)
    for mnemonic in sorted(d.keys()):
        mode_info = d[mnemonic]
        first_line = "%s,%s," % (mnemonic, lookup['status_byte'].get(mnemonic, lookup['status_byte_empty']))
        implicit_line = "%s" % first_line  # force copy
        second_line = ",%s," % lookup['status_byte_empty']
        compact_line = "%s" % first_line  # force copy
        found_mode = 0
        found_implicit = False
        for mode_name in order:
            header += "%s,,," % (title_modes[mode_name])
            if mode_name in mode_info:
                first_line += "\"%s %s\",,," % (mnemonic, operands[mode_name])
                second_line += mode_info[mode_name]
                implicit_line += mode_info[mode_name]
                compact_line += mode_info[mode_name]
                list_csv.append("\"%s %s\",%s,%s" % (mnemonic, operands[mode_name], lookup['status_byte'].get(mnemonic, lookup['status_byte_empty']),mode_info[mode_name]))
                found_mode += 1
                if mode_name == "implicit":
                    found_implicit = True
            else:
                first_line += ",,,"
                second_line += ",,,"
                compact_line += ",,,"
        if 'relative' in mode_info:
            mode_name = 'relative'
            list_csv.append("\"%s %s\",%s,%s" % (mnemonic, operands[mode_name], lookup['status_byte'].get(mnemonic, lookup['status_byte_empty']),mode_info[mode_name]))

        if found_mode:
            if found_implicit and found_mode == 1:
                implicit_csv.append(implicit_line)
            else:
                main_csv.append(first_line)
                main_csv.append(second_line)
                compact_csv.append(compact_line)

    print ("\n".join(main_csv))
    print ("\n".join(compact_csv))
    print ("\n".join(implicit_csv))
    print ("\n".join(list_csv))



if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cpu", help="Specify CPU type (defaults to 6502)", default="6502")
    parser.add_argument("-u", "--undocumented", help="Allow undocumented opcodes", action="store_true")
    parser.add_argument("-d", "--debug", help="Show debug information as the program runs", action="store_true")
    parser.add_argument("-v", "--verbose", help="Show processed instructions as the program runs", action="store_true")
    options, extra = parser.parse_known_args()
    
    if options.debug:
        log.setLevel(logging.DEBUG)

    gen_csv(options.cpu, options.undocumented)
