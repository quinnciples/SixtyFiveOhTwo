from SixtyFiveOhTwo import CPU6502
import inspect


def add(x, y):
    return x + y


def test_add():
    assert add(1, 2) == 4


def TEST_LDA_IM_0xA9():
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

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')


def TEST_LDA_IM_0xA9_ZERO_FLAG_SET():
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

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')


def TEST_LDA_IM_0xA9_NEGATIVE_FLAG_SET():
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
    #cpu.printLog()
    # cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF02)

    assert(EXPECTED_CYCLES == cpu.cycles - 1)
    assert(cpu.registers == EXPECTED_REGISTERS)
    # print(inspect.currentframe().f_code.co_name + ' PASSED.')


tests = [
    TEST_LDA_IM_0xA9
, TEST_LDA_IM_0xA9_ZERO_FLAG_SET
, TEST_LDA_IM_0xA9_NEGATIVE_FLAG_SET
]

for test in tests:
    try:
        test()
        print('PASSED: ' + test.__name__)
    except:
        print('FAILED: ' + test.__name__)