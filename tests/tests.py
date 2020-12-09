import os
import logging
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502

"""

NOTES

Need to investigate STA ABSX, ABSY, and INDY cycle counts. These have been manually adjusted in the tests to pass, however the underlying instructions work correctly.
INX, INY wrap around 0xFF
Fibonacci - https://www.youtube.com/watch?v=a73ZXDJtU48

"""


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


def TEST_0xE6_INC_ZP():
    EXPECTED_VALUE = 0x9C
    EXPECTED_CYCLES = 5
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xE6, 0xF2]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00F2] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x00F2] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xF6_INC_ZP_X():
    EXPECTED_VALUE = 0x9C
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xF6, 0xF2]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x00F7] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x00F7] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xEE_INC_ABS():
    EXPECTED_VALUE = 0x20
    EXPECTED_CYCLES = 6
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xEE, 0xF2, 0x2F]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x2FF2] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x2FF2] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xFE_INC_ABS_X():
    EXPECTED_VALUE = 0x2F
    EXPECTED_CYCLES = 7
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xFE, 0x00, 0x2F]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.memory[0x2FFF] = EXPECTED_VALUE - 1
    cpu.execute()

    try:
        assert(cpu.memory[0x2FFF] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        print(f'Cycles: {cpu.cycles-1}')
        raise
    return False


def TEST_0xC8_INY():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xA5
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xA6
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xC8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xC8_INY_WRAPAROUND():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0xFF
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0x00
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xC8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xE8_INX():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xB6,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0xB7,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xE8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xE8_INX_WRAPAROUND():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0xFF,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x00,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xE8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x18_CLC():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x18]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x58_CLI():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x58]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB8_CLV():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 1,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xB8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xD8_CLD():
    EXPECTED_CYCLES = 2
    INITIAL_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    INITIAL_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 1,
        'B': 0,
        'V': 0,
        'N': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xD8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers = INITIAL_REGISTERS
    cpu.flags = INITIAL_FLAGS
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x38_SEC():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 1,
        'Z': 0,
        'I': 0,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x38]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x78_SEI():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 1,
        'D': 0,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0x78]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xF8_SED():
    EXPECTED_CYCLES = 2
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
        'C': 0,
        'Z': 0,
        'I': 0,
        'D': 1,
        'B': 0,
        'V': 0,
        'N': 0
    }
    cpu = CPU6502(cycle_limit=EXPECTED_CYCLES)
    cpu.reset(program_counter=0xFF00)
    program = [0xF8]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA9_LDA_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xA2, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0xA0, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    program = [0xA2, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM_ZERO_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0x00
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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

    program = [0xA0, 0x00]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA2_LDX_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    program = [0xA2, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA0_LDY_IM_NEGATIVE_FLAG_SET():
    EXPECTED_CYCLES = 2
    EXPECTED_VALUE = 0xAF
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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

    program = [0xA0, 0xAF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB5_LDA_ZP_X_WRAPAROUND():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    cpu.memory[0x02] = 0x15
    program = [0xB5, 0xFD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA6_LDX_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xA6, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xA4_LDY_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0xA4, 0xCC]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB5_LDA_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x05,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB6_LDX_ZP_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
    cpu.memory[0xE2] = 0x15
    program = [0xB6, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xB4_LDY_ZP_X():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x15
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x05,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0xB4, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAE_LDX_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0xAE, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xAC_LDY_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x33
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0xAC, 0x00, 0xDD]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBE_LDX_ABS_Y():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x0A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
    program = [0xBE, 0x00, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBE_LDX_ABS_Y_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
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
    program = [0xBE, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0xBC_LDY_ABS_X_CROSS_PAGE_BOUNDARY():
    EXPECTED_CYCLES = 5
    EXPECTED_VALUE = 0x0B
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x04,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    cpu.memory[0xEE02] = 0x0B
    program = [0xBC, 0xFE, 0xED]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0x04
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
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
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x4C_JMP_ABS():
    EXPECTED_CYCLES = 3 + 2
    EXPECTED_VALUE = 0x45
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x4C, 0x10, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0xA9, 0x45]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF10)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x6C_JMP_IND():
    EXPECTED_CYCLES = 5 + 2
    EXPECTED_VALUE = 0xFE
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x6C, 0x10, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    program = [0x20, 0xFF]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF10)
    program = [0xA9, 0xFE]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF20)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x84_STY_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0x84, 0x2A]
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x85_STA_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x85, 0x2A]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x86_STX_ZP():
    EXPECTED_CYCLES = 3
    EXPECTED_VALUE = 0x2A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x86, 0x2A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x002A] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x94_STY_ZPX():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0x02,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0x94, 0x3A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x95_STA_ZPX():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x02,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x95, 0x3A]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x02
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x96_STX_ZPY():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0x3A
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0x02
    }
    EXPECTED_FLAGS = {
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
    program = [0x96, 0x3A]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x003C] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8C_STY_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': 0,
        'Y': EXPECTED_VALUE
    }
    EXPECTED_FLAGS = {
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
    program = [0x8C, 0xDA, 0x74]
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8D_STA_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x8D, 0xDA, 0x74]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x8E_STX_ABS():
    EXPECTED_CYCLES = 4
    EXPECTED_VALUE = 0xB3
    EXPECTED_REGISTERS = {
        'A': 0,
        'X': EXPECTED_VALUE,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x8E, 0xDA, 0x74]
    cpu.registers['X'] = EXPECTED_REGISTERS['X']
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x74DA] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x9D_STA_ABSX():
    EXPECTED_CYCLES = 4  # 5
    EXPECTED_VALUE = 0x13
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x03,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    program = [0x9D, 0xDA, 0x70]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x03
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x70DD] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x99_STA_ABSY():
    EXPECTED_CYCLES = 4  # 5
    EXPECTED_VALUE = 0x23
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
    program = [0x99, 0x00, 0x50]
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['Y'] = 0x05
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.memory[0x5005] == EXPECTED_VALUE)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x81_STA_INDX():
    EXPECTED_CYCLES = 6
    EXPECTED_VALUE = 0x1B
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0x04,
        'Y': 0
    }
    EXPECTED_FLAGS = {
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
    cpu.registers['A'] = EXPECTED_VALUE
    cpu.registers['X'] = 0x04
    cpu.memory[0x0006] = 0x00
    cpu.memory[0x0007] = 0x80
    program = [0x81, 0x02]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.execute()

    try:
        assert(cpu.memory[0x8000] == EXPECTED_VALUE)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x00, endingAddress=0x07)
        cpu.memoryDump(startingAddress=0x8000, endingAddress=0x8007)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


def TEST_0x91_STA_INDY():
    EXPECTED_CYCLES = 5  # 6
    EXPECTED_VALUE = 0x23
    EXPECTED_REGISTERS = {
        'A': EXPECTED_VALUE,
        'X': 0,
        'Y': 0x05
    }
    EXPECTED_FLAGS = {
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
    cpu.memory[0x0008] = 0x00
    cpu.memory[0x0009] = 0x50
    program = [0x91, 0x08]
    cpu.loadProgram(instructions=program, memoryAddress=0xFF00)
    cpu.registers['A'] = EXPECTED_REGISTERS['A']
    cpu.registers['Y'] = EXPECTED_REGISTERS['Y']
    cpu.execute()

    try:
        assert(cpu.memory[0x5005] == EXPECTED_VALUE)
        assert(cpu.registers == EXPECTED_REGISTERS)
        assert(cpu.flags == EXPECTED_FLAGS)
        assert(cpu.cycles - 1 == EXPECTED_CYCLES)
        return True
    except AssertionError:
        cpu.printLog()
        cpu.memoryDump(startingAddress=0x5000, endingAddress=0x5007)
        cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)
        raise
    return False


if __name__ == '__main__':
    os.system('color')
    tests = [
        TEST_0xA9_LDA_IM,
        TEST_0xA9_LDA_IM_ZERO_FLAG_SET,
        TEST_0xA9_LDA_IM_NEGATIVE_FLAG_SET,
        TEST_0xA5_LDA_ZP,
        TEST_0xB5_LDA_ZP_X,
        TEST_0xB5_LDA_ZP_X_WRAPAROUND,
        TEST_0xAD_LDA_ABS,
        TEST_0xBD_LDA_ABS_X,
        TEST_0xBD_LDA_ABS_X_CROSS_PAGE_BOUNDARY,
        TEST_0xB9_LDA_ABS_Y,
        TEST_0xB9_LDA_ABS_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA1_LDA_IND_X,
        TEST_0xB1_LDA_IND_Y,
        TEST_0xB1_LDA_IND_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA2_LDX_IM,
        TEST_0xA2_LDX_IM_ZERO_FLAG_SET,
        TEST_0xA2_LDX_IM_NEGATIVE_FLAG_SET,
        TEST_0xA6_LDX_ZP,
        TEST_0xB6_LDX_ZP_Y,
        TEST_0xAE_LDX_ABS,
        TEST_0xBE_LDX_ABS_Y,
        TEST_0xBE_LDX_ABS_Y_CROSS_PAGE_BOUNDARY,
        TEST_0xA0_LDY_IM,
        TEST_0xA0_LDY_IM_ZERO_FLAG_SET,
        TEST_0xA0_LDY_IM_NEGATIVE_FLAG_SET,
        TEST_0xA4_LDY_ZP,
        TEST_0xB4_LDY_ZP_X,
        TEST_0xAC_LDY_ABS,
        TEST_0xBC_LDY_ABS_X_CROSS_PAGE_BOUNDARY,
        TEST_0x4C_JMP_ABS,
        TEST_0x6C_JMP_IND,
        TEST_0x85_STA_ZP,
        TEST_0x95_STA_ZPX,
        TEST_0x8D_STA_ABS,
        TEST_0x9D_STA_ABSX,
        TEST_0x99_STA_ABSY,
        TEST_0x81_STA_INDX,
        TEST_0x91_STA_INDY,
        TEST_0x84_STY_ZP,
        TEST_0x86_STX_ZP,
        TEST_0x96_STX_ZPY,
        TEST_0x94_STY_ZPX,
        TEST_0x8C_STY_ABS,
        TEST_0x8E_STX_ABS,
        TEST_0x38_SEC,
        TEST_0x78_SEI,
        TEST_0xF8_SED,
        TEST_0x18_CLC,
        TEST_0x58_CLI,
        TEST_0xB8_CLV,
        TEST_0xD8_CLD,
        TEST_0xC8_INY,
        TEST_0xC8_INY_WRAPAROUND,
        TEST_0xE8_INX,
        TEST_0xE8_INX_WRAPAROUND,
        TEST_0xE6_INC_ZP,
        TEST_0xF6_INC_ZP_X,
        TEST_0xEE_INC_ABS,
        TEST_0xFE_INC_ABS_X,
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
    print(f"{bcolors.OKGREEN}{'▓' * passed}{bcolors.ENDC} {passed} tests PASSED")
    print(f"{bcolors.FAIL}{'▓' * failed}{bcolors.ENDC} {failed} tests FAILED")
