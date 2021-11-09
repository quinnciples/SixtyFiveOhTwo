from cpu6502 import CPU6502


def run():
    cpu = CPU6502()
    cpu.reset()
    cpu.memory[0x00CC] = 0x02  # Used for LDA_ZP

    cpu.memory[0x0080] = 0x03  # Used for LDA_ZP_X

    cpu.memory[0x00AA] = 0x03  # Used for LDA_IND_X
    cpu.memory[0x00AB] = 0xFF  # Used for LDA_IND_X

    cpu.memory[0x00AC] = 0x01  # Used for LDA_IND_Y
    cpu.memory[0x00AD] = 0xFF  # Used for LDA_IND_Y

    cpu.memory[0xFF00] = 0x04
    cpu.memory[0xFF01] = 0x05
    cpu.memory[0xFF02] = 0x06
    cpu.memory[0xFF03] = 0x07
    cpu.memory[0xFF04] = 0x08

    cpu.loadProgram(instructions=[0xA9, 0x09, 0x6C, 0x30, 0xFF], memoryAddress=0xFF28)
    cpu.loadProgram(instructions=[0x38, 0xFF], memoryAddress=0xFF30)
    cpu.loadProgram(instructions=[0xA9, 0x0A, 0x85, 0xB0, 0xA2, 0x01, 0xA9, 0x0B, 0x95, 0xB0], memoryAddress=0xFF38)

    cpu.loadProgram(instructions=[0xA9, 0x01, 0xA5, 0xCC, 0xB5, 0x80, 0xAD, 0x00, 0xFF, 0xBD, 0x01, 0xFF, 0xB9, 0xFF, 0xFE, 0xA1, 0xAA, 0xB1, 0xAC, 0x4C, 0x28, 0xFF], memoryAddress=0xFF10)

    cpu.registers['Y'] = 0x03

    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0xFF00, endingAddress=0xFF3F)
    cpu.memoryDump(startingAddress=0x0000, endingAddress=0x00FF)
    cpu.memoryDump(startingAddress=0x00, endingAddress=0x0F)


def fibonacci_test():
    cpu = CPU6502(cycle_limit=1000, printActivity=False)
    cpu.reset(program_counter=0x0000)

    program = [0xA9, 0x01,  # LDA_IM 1
               0xA2, 0x00,  # LDX_IM 0
               0x85, 0x21,  # STA_ZP [0x21]
               0xA9, 0x00,  # LDA_IM 0
               0x65, 0x21,  # ADC [0x21]  -- This is the main loop; the jump ins below should point to the address of this line
               0xB0, 0x11,  # BCS 0x11  ; Jump to end of program if value exceeds 0xFF
               0x95, 0x30,  # STA_ZP_X [0x30]
               0xE8,        # INX
               0x85, 0x22,  # STA_ZP [0x22]
               0xA5, 0x21,  # LDA_ZP [0x21]
               0x85, 0x20,  # STA_ZP [0x20]
               0xA5, 0x22,  # LDA_ZP [0x22]
               0x85, 0x21,  # STA_ZP [0x21]
               0xA5, 0x20,  # LDA_ZP [0x20]
               0x4C, 0x08, 0x00  # JMP 0x0008
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x0000)
    cpu.execute()
    cpu.printLog()
    cpu.memoryDump(startingAddress=0x0000, endingAddress=0x001F)
    cpu.memoryDump(startingAddress=0x0020, endingAddress=0x0022, display_format='Dec')
    cpu.memoryDump(startingAddress=0x0030, endingAddress=0x003F, display_format='Dec')


def fast_multiply_10():
    cpu = CPU6502(cycle_limit=100, printActivity=True)
    cpu.reset(program_counter=0x2000)

    program = [0xA9, 0x19,        # LDA_IM 25 ; Load initial value
               0x0A,              # ASL ACC ; Double accumulator value
               0x8D, 0x00, 0x30,  # STA [0x3000] ; Store doubled value in memory
               0x0A,              # ASL ACC ; Double accumulator again (x4 total)
               0x0A,              # ASL ACC ; Double accumulator again (x8 total)
               0x18,              # CLC ; Clear carry flag for some reason
               0x6D, 0x00, 0x30,  # ADC [0x3000] ; Add memory to accumulator (effectively value x 8 + value x 2 = value x 10)
               0x8D, 0x01, 0x30,  # STA [0x3000] ; Store accumulator value in memory
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x2000, mainProgram=True)
    cpu.execute()
    cpu.memoryDump(startingAddress=0x2000, endingAddress=0x2017)
    cpu.memoryDump(startingAddress=0x3000, endingAddress=0x3001, display_format='Dec')


def flags_test():
    cpu = CPU6502(cycle_limit=10)
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 0)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 1)
    cpu.getProcessorStatus()
    cpu.setFlagsManually(['C', 'Z', 'I', 'D', 'B', 'U', 'V', 'N'], 0)
    flags = ['N', 'V', 'U', 'B', 'D', 'I', 'Z', 'C']
    for flag in flags:
        print(f'Flag: {flag}')
        cpu.setFlagsManually([flag], 1)
        cpu.printState()
        value = cpu.getProcessorStatus()
        cpu.setFlagsManually([flag], 0)
        cpu.printState()
        cpu.setProcessorStatus(value)
        cpu.printState()
        print('*' * 50)


def functional_test_program():

    try:

        program = []
        print('Loading in binary file...')
        with open('binary/6502_functional_test.bin', 'rb') as f:
            data = f.read()
        print('Converting to text...')
        for d in data:
            program.append(d)

        # print(program[0x03F6: 0x040F])
        # print(len(program))

        cpu = None
        cpu = CPU6502(cycle_limit=200_000_000, printActivity=False, enableBRK=True, logging=True, logFile='log.txt')
        # cpu = CPU6502(cycle_limit=10_000_000, printActivity=False, enableBRK=True, logging=False)
        cpu.reset(program_counter=0x0400)
        cpu.loadProgram(instructions=program, memoryAddress=0x000A, mainProgram=False)
        cpu.program_counter = 0x0400
        # print(cpu.memory[0x400:0x40F])
        print('Running program...')
        cpu.execute()

    except Exception as e:
        print(str(e))

    finally:
        # print(f'{cpu.cycles:,} cycles. Elapesd time {cpu.execution_time}.')
        cpu.printBenchmarkInfo()


def runBenchmark():
    cpu = None
    cpu = CPU6502(cycle_limit=750_000, printActivity=False, enableBRK=False, logFile=None)
    cpu.reset(program_counter=0x8000)
    cpu.memory[0x0090] = 0
    program = [
        0xA2, 0x00,  # LDX 0
        0xA0, 0x00,  # LDY 0
        0xE8,  # INX ; 0x8004
        0xE0, 0xFF,  # CPX 255
        0xF0, 0x03,  # BEQ +4
        0x4C, 0x04, 0x80,  # JMP to 0x8004
        0xC8,  # INY
        0xC0, 0xFF,  # CPY 255
        0xF0, 0x03,  # BEQ +4
        0x4C, 0x04, 0x80,  # JMP to 0x8004
        0x00,  # BRK
    ]
    cpu.loadProgram(instructions=program, memoryAddress=0x8000, mainProgram=True)
    cpu.execute()
    print(f'Cycles: {cpu.cycles - 1:,} :: Elapsed time: {cpu.execution_time} :: Cycles/sec: {(cpu.cycles - 1) / cpu.execution_time.total_seconds():0,.2f}')


def hundred_doors():
    import programs.hundred_doors
    program = programs.hundred_doors.program
    starting_address = programs.hundred_doors.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=1000, printActivity=True, enableBRK=False)
    cpu.reset(program_counter=starting_address)
    cpu.loadProgram(instructions=program, memoryAddress=starting_address, mainProgram=True)
    cpu.execute()

    for test in programs.hundred_doors.tests:
        cpu.memoryDump(startingAddress=test['memory_range'][0], endingAddress=test['memory_range'][1] + 1, display_format='Dec')
        if test['expected_values'] is not None:
            print(cpu.memory[test['memory_range'][0]:test['memory_range'][1] + 1] == test['expected_values'])

    print(cpu.benchmarkInfo())


def sieve_of_erastosthenes():
    import programs.sieve_of_eratosthenes
    program = programs.sieve_of_eratosthenes.program
    starting_address = programs.sieve_of_eratosthenes.starting_address
    cpu = None
    cpu = CPU6502(cycle_limit=100_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=starting_address)
    cpu.loadProgram(instructions=program, memoryAddress=starting_address, mainProgram=True)
    # cpu.memory[0x0601] = 0x64
    cpu.execute()

    for test in programs.sieve_of_eratosthenes.tests:
        cpu.memoryDump(startingAddress=test['memory_range'][0], endingAddress=test['memory_range'][1], display_format='Dec')
        if test['expected_values'] is not None:
            print(cpu.memory[test['memory_range'][0]:test['memory_range'][1] + 1] == test['expected_values'])

    print(cpu.benchmarkInfo())


def wozmon():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=0xFF00)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.program_counter = wozmon_address
    cpu.execute()


def apple_i_basic():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)
    cpu.program_counter = wozmon_address
    print(f'{basic_address:04X}')
    cpu.execute()


def apple_i_print_chars():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_print_characters
    char_program = programs.apple_1_print_characters.program
    char_address = programs.apple_1_print_characters.starting_address

    cpu = None
    cpu = CPU6502(cycle_limit=10_000, printActivity=False, enableBRK=False, logging=True, logFile='log.txt')
    cpu.reset(program_counter=char_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=char_program, memoryAddress=char_address, mainProgram=False)
    cpu.program_counter = char_address
    cpu.execute()


def blackjack():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.blackjack

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.blackjack.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {programs.blackjack.name}...')
    print(programs.blackjack.instructions)
    cpu.execute()


def lunar_lander():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.lunar_lander

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=True, logFile='log.txt')
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.lunar_lander.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(programs.lunar_lander.instructions)
    cpu.execute()


def hammurabi():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.hammurabi

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.reset(program_counter=basic_address)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in programs.hammurabi.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(programs.hammurabi.instructions)
    cpu.execute()


def microchess():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.microchess as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def shut_the_box():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.shut_the_box as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def codebreaker():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.codebreaker as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=False, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    # cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(game.instructions)
    cpu.execute()


def applesoft_basic():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.applesoft_basic as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.instructions)
    cpu.execute()


def apple_30th():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_30th as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.description)
    print(game.instructions)
    cpu.execute()


def startrek():
    import programs.wozmon
    wozmon_program = programs.wozmon.program
    wozmon_address = programs.wozmon.starting_address

    import programs.apple_1_basic
    basic_program = programs.apple_1_basic.program
    basic_address = programs.apple_1_basic.starting_address

    import programs.startrek as game

    cpu = None
    cpu = CPU6502(cycle_limit=100_000_000_000, printActivity=False, enableBRK=True, logging=False)
    cpu.loadProgram(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
    cpu.loadProgram(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)

    for tape in game.tapes:
        cpu.loadProgram(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)

    cpu.program_counter = wozmon_address
    print(f'Running {game.name}...')
    print(game.description)
    print(game.instructions)
    cpu.execute()


if __name__ == '__main__':
    # run()
    # fibonacci_test()
    # print()
    # fast_multiply_10()
    # print()
    # flags_test()
    # print()
    functional_test_program()
    # print()
    # runBenchmark()
    # print()
    # hundred_doors()
    # print()
    # sieve_of_erastosthenes()
    # print()
    # wozmon()
    # print()
    # apple_i_basic()
    # print()
    # apple_i_print_chars()
    # print()
    # blackjack()
    # print()
    # lunar_lander()
    # print()
    # hammurabi()
    # print()
    # microchess()
    # print()
    # shut_the_box()
    # print()
    # codebreaker()
    # print()
    # applesoft_basic()
    # print()
    # apple_30th()
    # startrek()
    pass
