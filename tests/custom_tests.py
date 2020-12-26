from testing_modules import bcolors
from testing_modules import generateProgram
import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502


def square_root_test() -> bool:
    TEST_NAME = 'SQUARE ROOT TEST'
    """
    http://www.6502.org/source/integers/root.htm
    """

    # cpu.memoryDump(startingAddress=0x1000, endingAddress=0x1000 + len(sqroot))
    # cpu.memoryDump(startingAddress=0x1100, endingAddress=0x1100 + len(loop))
    # cpu.memoryDump(startingAddress=0x1200, endingAddress=0x1200 + len(subtr))
    # cpu.memoryDump(startingAddress=0x1300, endingAddress=0x1300 + len(next))

    # cpu.memoryDump(startingAddress=0x00F0, endingAddress=0x00F7)

    """
    Address  Hexdump   Dissassembly
    -------------------------------
    $0600    a9 90     LDA #$90
    $0602    85 f0     STA $f0
    $0604    a9 00     LDA #$00
    $0606    85 f2     STA $f2
    $0608    85 f3     STA $f3
    $060a    85 f6     STA $f6
    $060c    a2 08     LDX #$08
    $060e    06 f6     ASL $f6
    $0610    06 f0     ASL $f0
    $0612    26 f1     ROL $f1
    $0614    26 f2     ROL $f2
    $0616    26 f3     ROL $f3
    $0618    06 f0     ASL $f0
    $061a    26 f1     ROL $f1
    $061c    26 f2     ROL $f2
    $061e    26 f3     ROL $f3
    $0620    a5 f6     LDA $f6
    $0622    85 f4     STA $f4
    $0624    a9 00     LDA #$00
    $0626    85 f5     STA $f5
    $0628    38        SEC
    $0629    26 f4     ROL $f4
    $062b    26 f5     ROL $f5
    $062d    a5 f3     LDA $f3
    $062f    c5 f5     CMP $f5
    $0631    90 16     BCC $0649
    $0633    d0 06     BNE $063b
    $0635    a5 f2     LDA $f2
    $0637    c5 f4     CMP $f4
    $0639    90 0e     BCC $0649
    $063b    a5 f2     LDA $f2
    $063d    e5 f4     SBC $f4
    $063f    85 f2     STA $f2
    $0641    a5 f3     LDA $f3
    $0643    e5 f5     SBC $f5
    $0645    85 f3     STA $f3
    $0647    e6 f6     INC $f6
    $0649    ca        DEX
    $064a    d0 c2     BNE $060e
    $064c    60        RTS

    """

    """

        *= $0600            ; can be anywhere, ROM or RAM

    SqRoot:
        LDA  #$90    ; clear A
        STA  $F0    ; clear remainder low byte
        LDA  #$00    ; clear A
        STA  $F2    ; clear remainder low byte
        STA  $F3    ; clear remainder high byte
        STA  $F6    ; clear $F6
        LDX  #$08    ; 8 pairs of bits to do
    Loop:
        ASL  $F6    ; $F6 = $F6 * 2

        ASL  $F0    ; shift highest bit of numb
        ROL  $F1    ;
        ROL  $F2    ; .. into remainder
        ROL  $F3    ;

        ASL  $F0    ; shift highest bit of number ..
        ROL  $F1    ;
        ROL  $F2    ; .. into remainder
        ROL  $F3    ;

        LDA  $F6    ; copy $F6 ..
        STA  $F4    ; .. to $F4
        LDA  #$00    ; clear byte
        STA  $F5    ; clear temp high byte

        SEC          ; +1
        ROL  $F4    ; temp = temp * 2 + 1
        ROL  $F5    ;

        LDA  $F3    ; get remainder high byte
        CMP  $F5    ; comapre with partial high byte
        BCC  Next    ; skip sub if remainder high byte smaller

        BNE  Subtr    ; do sub if <> (must be remainder>partial !)

        LDA  $F2    ; get remainder low byte
        CMP  $F4    ; comapre with partial low byte
        BCC  Next    ; skip sub if remainder low byte smaller

                        ; else remainder>=partial so subtract then
                        ; and add 1 to $F6. carry is always set here
    Subtr:
        LDA  $F2    ; get remainder low byte
        SBC  $F4    ; subtract partial low byte
        STA  $F2    ; save remainder low byte
        LDA  $F3    ; get remainder high byte
        SBC  $F5    ; subtract partial high byte
        STA  $F3    ; save remainder high byte

        INC  $F6    ; increment $F6
    Next:
        DEX          ; decrement bit pair count
        BNE  Loop    ; loop if not all done

        RTS

    """

    """
    ; Calculates the 8 bit root and 9 bit remainder of a 16 bit unsigned integer in
    ; Numberl/Numberh. The result is always in the range 0 to 255 and is held in
    ; Root, the remainder is in the range 0 to 511 and is held in Reml/Remh
    ;
    ; partial results are held in templ/temph
    ;
    ; This routine is the complement to the integer square program.
    ;
    ; Destroys A, X registers.

    ; variables - must be in RAM

    Numberl		= $F0		; number to find square root of low byte
    Numberh		= Numberl+1	; number to find square root of high byte
    Reml		= $F2		; remainder low byte
    Remh		= Reml+1	; remainder high byte
    templ		= $F4		; temp partial low byte
    temph		= templ+1	; temp partial high byte
    Root		= $F6		; square root

    *= $8000        		; can be anywhere, ROM or RAM

    SqRoot
        LDA	#$00		; clear A
        STA	Reml		; clear remainder low byte
        STA	Remh		; clear remainder high byte
        STA	Root		; clear Root
        LDX	#$08		; 8 pairs of bits to do
    Loop
        ASL	Root		; Root = Root * 2

        ASL	Numberl		; shift highest bit of number ..
        ROL	Numberh		;
        ROL	Reml		; .. into remainder
        ROL	Remh		;

        ASL	Numberl		; shift highest bit of number ..
        ROL	Numberh		;
        ROL	Reml		; .. into remainder
        ROL	Remh		;

        LDA	Root		; copy Root ..
        STA	templ		; .. to templ
        LDA	#$00		; clear byte
        STA	temph		; clear temp high byte

        SEC			    ; +1
        ROL	templ		; temp = temp * 2 + 1
        ROL	temph		;

        LDA	Remh		; get remainder high byte
        CMP	temph		; comapre with partial high byte
        BCC	Next		; skip sub if remainder high byte smaller

        BNE	Subtr		; do sub if <> (must be remainder>partial !)

        LDA	Reml		; get remainder low byte
        CMP	templ		; comapre with partial low byte
        BCC	Next		; skip sub if remainder low byte smaller

                        ; else remainder>=partial so subtract then
                        ; and add 1 to root. carry is always set here
    Subtr
        LDA	Reml		; get remainder low byte
        SBC	templ		; subtract partial low byte
        STA	Reml		; save remainder low byte
        LDA	Remh		; get remainder high byte
        SBC	temph		; subtract partial high byte
        STA	Remh		; save remainder high byte

        INC	Root		; increment Root
    Next
        DEX			    ; decrement bit pair count
        BNE	Loop		; loop if not all done

        RTS
    """

    sqroot = [
        0xA9, 0x00,  # LDA_IM 0
        0x85, 0xF2,  # STA_ZP [0xF2] Reml
        0x85, 0xF3,  # STA_ZP [0xF3] Remh
        0x85, 0xF6,  # STA_ZP [0xF6] Root
        0xA2, 0x08,  # LDX_IM 8

        0x4C, 0x00, 0x11,  # JMP TO LOOP [0x1100]
    ]
    loop = [
        0x06, 0xF6,  # ASL_ZP [0xF6] Root

        0x06, 0xF0,  # ASL_ZP [0xF0] Numberl
        0x26, 0xF1,  # ROL_ZP [0xF1] Numberh
        0x26, 0xF2,  # ROL_ZP [0xF2] Reml
        0x26, 0xF3,  # ROL_ZP [0xF3] Remh

        0x06, 0xF0,  # ASL_ZP [0xF0] Numberl
        0x26, 0xF1,  # ROL_ZP [0xF1] Numberh
        0x26, 0xF2,  # ROL_ZP [0xF2] Reml
        0x26, 0xF3,  # ROL_ZP [0xF3] Remh

        0xA5, 0xF6,  # LDA_ZP [0xF6] Root
        0x85, 0xF4,  # STA_ZP [0xF4] Templ
        0xA9, 0x00,  # LDA_IM 0
        0x85, 0xF5,  # STA_ZP [0xF5] Temph

        0x38, 0x00,  # SEC
        0x26, 0xF4,  # ROL_ZP [0xF4] Templ
        0x26, 0xF5,  # ROL_ZP [0xF5] Temph

        0xA5, 0xF3,  # LDA_ZP [0xF3] Remh
        0xC5, 0xF5,  # CMP_ZP [0xF5] Temph
        0xB0, 0x03,  # BCC [Next Subroutine] -- CHANGED TO BCS
        0x4C, 0x00, 0x13,  # JMP TO NEXT [0x1300]

        0xF0, 0xA3,  # BNE [Subtr Subroutine] -- CHANGED TO BEQ
        0x4C, 0x00, 0x12,  # JMP TO SUBTR [0x1200]

        0xA5, 0xF2,  # LDA_ZP [0xF2] Reml
        0xC5, 0xF4,  # CMP_ZP [0xF4] Templ
        0xB0, 0xA3,  # BCC [Next Subroutine] -- CHANGED TO BCS
        0x4C, 0x00, 0x13,  # JMP TO NEXT [0x1300]

        0x4C, 0x00, 0x12,  # JMP TO SUBTR [0x1200]
    ]
    subtr = [
        0xA5, 0xF2,  # LDA_ZP [0xF2] Reml
        0xE5, 0xF4,  # SBC_ZP [0xF4] Templ
        0x85, 0xF2,  # STA_ZP [0xF2] Reml
        0xA5, 0xF3,  # LDA_ZP [0xF3] Remh
        0xE5, 0xF5,  # SBC_ZP [0xF4] Temph
        0x85, 0xF3,  # STA_ZP [0xF3] Remh

        0xE6, 0xF6,  # INC_ZP [0xF6] Root

        0x4C, 0x00, 0x13  # JMP TO NEXT [0x1300]
    ]
    next = [
        0xCA, 0x00,  # DEX
        0xF0, 0x03,  # BNE [Loop Subroutine] -- CHANGED TO BEQ
        0x4C, 0x00, 0x11,  # JMP TO LOOP [0x1100]
        0x60, 0x00,  # RTS

    ]

    all_in_one = [
        0xa9, 0x51, 0x85, 0xf0, 0xa9, 0x00, 0x85, 0xf2, 0x85, 0xf3, 0x85, 0xf6, 0xa2, 0x08, 0x06, 0xf6,
        0x06, 0xf0, 0x26, 0xf1, 0x26, 0xf2, 0x26, 0xf3, 0x06, 0xf0, 0x26, 0xf1, 0x26, 0xf2, 0x26, 0xf3,
        0xa5, 0xf6, 0x85, 0xf4, 0xa9, 0x00, 0x85, 0xf5, 0x38, 0x26, 0xf4, 0x26, 0xf5, 0xa5, 0xf3, 0xc5,
        0xf5, 0x90, 0x16, 0xd0, 0x06, 0xa5, 0xf2, 0xc5, 0xf4, 0x90, 0x0e, 0xa5, 0xf2, 0xe5, 0xf4, 0x85,
        0xf2, 0xa5, 0xf3, 0xe5, 0xf5, 0x85, 0xf3, 0xe6, 0xf6, 0xca, 0xd0, 0xc2, 0x60
    ]

    all_in_one = [
        # 0xa9, 0x51, 0x85, 0xf0,  # Load low byte of number to find square root of
        # 0xa9, 0x00, 0x85, 0xf1,  # Load high byte of number to find square root of
        0xa9, 0x00, 0x85, 0xf2, 0x85, 0xf3, 0x85, 0xf6, 0xa2, 0x08, 0x06, 0xf6,
        0x06, 0xf0, 0x26, 0xf1, 0x26, 0xf2, 0x26, 0xf3, 0x06, 0xf0, 0x26, 0xf1, 0x26, 0xf2, 0x26, 0xf3,
        0xa5, 0xf6, 0x85, 0xf4, 0xa9, 0x00, 0x85, 0xf5, 0x38, 0x26, 0xf4, 0x26, 0xf5, 0xa5, 0xf3, 0xc5,
        0xf5, 0x90, 0x16, 0xd0, 0x06, 0xa5, 0xf2, 0xc5, 0xf4, 0x90, 0x0e, 0xa5, 0xf2, 0xe5, 0xf4, 0x85,
        0xf2, 0xa5, 0xf3, 0xe5, 0xf5, 0x85, 0xf3, 0xe6, 0xf6, 0xca, 0xd0, 0xc2, 0x60
    ]

    # cpu.memory[0x00F0] = 0x09  # Number to find square root of low byte
    # cpu.memory[0x00F1] = 0x00  # Number to find square root of high byte

    # cpu.loadProgram(instructions=sqroot, memoryAddress=0x1000, mainProgram=True)
    # cpu.loadProgram(instructions=loop, memoryAddress=0x1100, mainProgram=False)
    # cpu.loadProgram(instructions=subtr, memoryAddress=0x1200, mainProgram=False)
    # cpu.loadProgram(instructions=next, memoryAddress=0x1300, mainProgram=False)
    numbers_to_test = [x ** 2 for x in range(2, 16)]
    expected_values = [x for x in range(2, 16)]

    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False

    for test_value, expected_value in zip(numbers_to_test, expected_values):
        cpu = CPU6502(cycle_limit=1200)
        cpu.reset(program_counter=0x0600)
        cpu.loadProgram(instructions=all_in_one, memoryAddress=0x0600, mainProgram=True)
        cpu.memory[0x00F0] = test_value
        cpu.memory[0x00F1] = 0x00  # Number to find square root of high byte
        cpu.execute()
        print(f'\tTesting square root of {test_value}: Expected {expected_value} / got {cpu.memory[0x00F6]} -- ', end='')
        if cpu.memory[0x00F6] == expected_value:
            print(f'{bcolors.OKGREEN}PASS{bcolors.ENDC}', end='\n')
        else:
            print(f'{bcolors.FAIL}FAIL{bcolors.ENDC}', end='\n')
            errors = True
    if errors:
        return False
    return True


def fibonacci_test():
    TEST_NAME = 'SQUARE ROOT TEST'
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    cpu = CPU6502(cycle_limit=500)
    cpu.reset(program_counter=0x0000)

    program = [0xA9, 0x01,  # LDA_IM 1
               0xA2, 0x00,  # LDX_IM 0
               0x85, 0x21,  # STA_ZP [0x21]
               0xA9, 0x00,  # LDA_IM 0
               0x65, 0x21,  # ADC [0x21]        ; This is the main loop; the jump ins below should point to the address of this line
               0xB0, 0x11,  # BCS 0x11          ; Jump to end of program if value exceeds 0xFF
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
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0x0000, endingAddress=0x001F)
    # cpu.memoryDump(startingAddress=0x0020, endingAddress=0x0022, display_format='Dec')
    # cpu.memoryDump(startingAddress=0x0030, endingAddress=0x003F, display_format='Dec')
    EXPECTED_VALUES = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    errors = False
    print(f'\tTesting Fibonacci sequence... Expected {EXPECTED_VALUES} / got {cpu.memory[0x0030:0x003C]} -- ', end='')
    if cpu.memory[0x0030:0x003C] == EXPECTED_VALUES:
        print(f'{bcolors.OKGREEN}PASS{bcolors.ENDC}', end='\n')
    else:
        print(f'{bcolors.FAIL}FAIL{bcolors.ENDC}', end='\n')
        errors = True

    if errors:
        return False
    return True


def custom_tests():
    tests = [
        square_root_test,
        fibonacci_test,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    custom_tests()
