import os
import logging
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502


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


def TEST_0xA9_LDA_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA9, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
        'C': 0,
        'Z': 1,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA9, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 1
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)

    program = [0xA9, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA5_LDA_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xCC] = 0x45
    program = [0xA5, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA5_LDA_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0xE2] = 0x15
    program = [0xB5, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAD_LDA_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.memory[0xDD00] = 0x33
    program = [0xAD, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBD_LDA_ABS_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x39
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x05
    cpu.memory[0xFF05] = 0x39
    program = [0xBD, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBD_LDA_ABS_X_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x16
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x04
    cpu.memory[0xEE02] = 0x16
    program = [0xBD, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB9_LDA_ABS_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x0A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0xFF05] = 0x0A
    program = [0xB9, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB9_LDA_ABS_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x04,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x04
    cpu.memory[0xEE02] = 0x0B
    program = [0xB9, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA1_LDA_IND_X():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x1B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['X'] = 0x04
    cpu.memory[0x0006] = 0x00
    cpu.memory[0x0007] = 0x80
    cpu.memory[0x8000] = 0x1B
    program = [0xA1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB1_LDA_IND_Y():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x02
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x04,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x04
    cpu.memory[0x0002] = 0x00
    cpu.memory[0x0003] = 0x80
    cpu.memory[0x8004] = 0x02
    program = [0xB1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB1_LDA_IND_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x06
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05,
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    cpu.registers['Y'] = 0x05
    cpu.memory[0x0002] = 0xFF
    cpu.memory[0x0003] = 0x7F
    cpu.memory[0x8004] = 0x06
    program = [0xB1, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0xA9_LDA_IM
        , TEST_0xA9_LDA_IM_ZERO_FLAG_SET
        , TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET
        , TEST_0xA5_LDA_ZP
        , TEST_0xA5_LDA_ZP_X
        , TEST_0xAD_LDA_ABS
        , TEST_0xBD_LDA_ABS_X
        , TEST_0xBD_LDA_ABS_X_CROSS_PAGE_BOUNDARY
        , TEST_0xB9_LDA_ABS_Y
        , TEST_0xB9_LDA_ABS_Y_CROSS_PAGE_BOUNDARY
        , TEST_0xA1_LDA_IND_X
        , TEST_0xB1_LDA_IND_Y
        , TEST_0xB1_LDA_IND_Y_CROSS_PAGE_BOUNDARY
    ]

    num_tests, passed, failed = len(tests), 0, 0

    for test in tests:
        try:
            if test():
                print(f"{bcolors.OKGREEN}PASSED:{bcolors.ENDC} {test.__name__}")
                passed += 1
            else:
                print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
                failed += 1
        except AssertionError:
            print(f"{bcolors.FAIL}FAILED:{bcolors.ENDC} {test.__name__}")
            logging.error("", exc_info=True)
            failed += 1
            continue

    print('TEST SUMMARY')
    print(f'{passed} tests PASSED. {failed} tests FAILED.')
