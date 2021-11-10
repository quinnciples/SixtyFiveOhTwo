from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from cpu6502 import CPU6502


def STX_ADDRESS_MODE_TESTS() -> bool:
    TEST_NAME = f'STX_ADDRESS_MODE_TESTS'
    INSTRUCTION = 'STX'
    IMMEDIATE_VALUE = None
    # VALUE_TO_TEST = 0xA5
    ZP_ADDRESS = 0x0059
    IND_ZP_ADDRESS = 0x0069
    FULL_ADDRESS = 0xAA48
    EXPECTED_VALUE = 0x05
    CYCLE_COUNTS = {
        'ZP': 3,
        'ZP_Y': 4,
        'ABS': 4
    }
    INITIAL_REGISTERS = {
        'A': 0x01,
        'X': EXPECTED_VALUE,
        'Y': 0x05
    }
    EXPECTED_REGISTERS = {
        'A': 0x01,
        'X': EXPECTED_VALUE,
        'Y': 0x05
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

    programs = generateProgram(instruction=INSTRUCTION,
                               registers=INITIAL_REGISTERS,
                               immediate_value=IMMEDIATE_VALUE,
                               zp_address=ZP_ADDRESS,
                               ind_zp_address=IND_ZP_ADDRESS,
                               sixteen_bit_address=FULL_ADDRESS,
                               CYCLE_COUNTS=CYCLE_COUNTS)

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    for label, program in programs.items():
        print(f'\tTesting {label}... ', end='')
        PROGRAM = program[0]
        EXPECTED_CYCLES = program[1]
        cpu = CPU6502(cycle_limit=100)
        cpu.reset(program_counter=0xFF00)
        cpu.load_program(instructions=PROGRAM, memoryAddress=0xFF00)
        cpu.registers = INITIAL_REGISTERS.copy()
        cpu.flags = INITIAL_FLAGS.copy()
        # cpu.memory[ZP_ADDRESS] = VALUE_TO_TEST  # ZP, ZP_X, and ZP_Y Location
        cpu.memory[IND_ZP_ADDRESS] = FULL_ADDRESS & 0b0000000011111111
        cpu.memory[IND_ZP_ADDRESS + 1] = (FULL_ADDRESS & 0b1111111100000000) >> 8
        # cpu.memory[FULL_ADDRESS] = VALUE_TO_TEST  # ABS, ABS_X, ABS_Y, and IND_X Location
        # cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] = VALUE_TO_TEST  # IND_Y Location
        # EXPECTED_MEMORY = cpu.memory.copy()
        cpu.execute()

        if cpu.registers != EXPECTED_REGISTERS \
            or cpu.flags != EXPECTED_FLAGS \
            or cpu.cycles - 1 != EXPECTED_CYCLES \
            or (EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE) \
            or (EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE) \
            or (EXPECTED_VALUE is not None and label in ['IND_Y'] and cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] != EXPECTED_VALUE):

            print(f'{bcolors.FAIL}FAILED{bcolors.ENDC}', end='\n')
            if cpu.registers != EXPECTED_REGISTERS:
                print(f'\t{bcolors.FAIL}REGISTERS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.flags != EXPECTED_FLAGS:
                print(f'\t{bcolors.FAIL}FLAGS DO NOT MATCH{bcolors.ENDC}', end='\n')
            if cpu.cycles - 1 != EXPECTED_CYCLES:
                print(f'\t{bcolors.FAIL}CYCLE COUNT DOES NOT MATCH{bcolors.ENDC}', end='\n')

            # Memory tests
            # Test that memory was unchanged
            # if EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y', 'ABS', 'ABS_X', 'ABS_Y', 'IND_X', 'IND_Y'] and cpu.memory != EXPECTED_MEMORY:
                # print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')

            # Test that value was written to correct memory location
            if (EXPECTED_VALUE is not None and label in ['ZP', 'ZP_X', 'ZP_Y'] and cpu.memory[ZP_ADDRESS] != EXPECTED_VALUE) \
                or (EXPECTED_VALUE is not None and label in ['ABS', 'ABS_X', 'ABS_Y', 'IND_X'] and cpu.memory[FULL_ADDRESS] != EXPECTED_VALUE) \
                or (EXPECTED_VALUE is not None and label in ['IND_Y'] and cpu.memory[FULL_ADDRESS + INITIAL_REGISTERS['Y']] != EXPECTED_VALUE):
                print(f'\t{bcolors.FAIL}MEMORY CONTENTS DO NOT MATCH{bcolors.ENDC}', end='\n')

            cpu.print_log()
            cpu.memory_dump(startingAddress=0xFF00, endingAddress=(0xFF00 + len(program)))
            cpu.memory_dump(startingAddress=ZP_ADDRESS, endingAddress=ZP_ADDRESS + 1)
            cpu.memory_dump(startingAddress=IND_ZP_ADDRESS, endingAddress=IND_ZP_ADDRESS + 1)
            cpu.memory_dump(startingAddress=FULL_ADDRESS, endingAddress=FULL_ADDRESS + 1)

            print(f'Program: ' + ', '.join('0x{0:0{1}X}'.format(x, 2) for x in program[0]))
            print(f'Cycles: {cpu.cycles-1} Expected Cycles: {EXPECTED_CYCLES}')
            print(f'Expected Registers: {EXPECTED_REGISTERS}')
            print(f'Expected Flags: {EXPECTED_FLAGS}')
            errors = True
        else:
            print(f'{bcolors.OKGREEN}PASSED{bcolors.ENDC}', end='\n')

    if errors:
        return False
    return True


def STX_tests():
    tests = [
        STX_ADDRESS_MODE_TESTS
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    STX_tests()
