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
    TEST_NAME = 'FIBONACCI TEST'
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    errors = False
    cpu = CPU6502(cycle_limit=500)
    cpu.reset(program_counter=0x0000)

    program = [0xA9, 0x01,          # LDA_IM 1
               0xA2, 0x00,          # LDX_IM 0
               0x85, 0x21,          # STA_ZP [0x21]
               0xA9, 0x00,          # LDA_IM 0
               0x65, 0x21,          # ADC [0x21]        ; This is the main loop; the jump ins below should point to the address of this line
               0xB0, 0x11,          # BCS 0x11          ; Jump to end of program if value exceeds 0xFF
               0x95, 0x30,          # STA_ZP_X [0x30]
               0xE8,                # INX
               0x85, 0x22,          # STA_ZP [0x22]
               0xA5, 0x21,          # LDA_ZP [0x21]
               0x85, 0x20,          # STA_ZP [0x20]
               0xA5, 0x22,          # LDA_ZP [0x22]
               0x85, 0x21,          # STA_ZP [0x21]
               0xA5, 0x20,          # LDA_ZP [0x20]
               0x4C, 0x08, 0x00     # JMP 0x0008
               ]
    cpu.loadProgram(instructions=program, memoryAddress=0x0000)
    cpu.execute()

    EXPECTED_VALUES = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
    errors = False
    for pos, expected in enumerate(EXPECTED_VALUES):
        print(f'\tTesting Fibonacci sequence: Expected {expected} / got {cpu.memory[0x0030 + pos]} -- ', end='')
        if cpu.memory[0x0030 + pos] == expected:
            print(f'{bcolors.OKGREEN}PASS{bcolors.ENDC}', end='\n')
        else:
            print(f'{bcolors.FAIL}FAIL{bcolors.ENDC}', end='\n')
            errors = True
    # cpu.printLog()
    # cpu.memoryDump(startingAddress=0x0000, endingAddress=0x001F)
    # cpu.memoryDump(startingAddress=0x0020, endingAddress=0x0022, display_format='Dec')
    # cpu.memoryDump(startingAddress=0x0030, endingAddress=0x003F, display_format='Dec')

    if errors:
        return False
    return True


def sort_test_8_bits() -> bool:
    TEST_NAME = 'SORT TEST 8 BITS'
    """
    The subroutine (SORT8) sorts unordered lists that are comprised of 8-bit elements.
    As in the previous examples in this chapter, the starting addres is contained
    in locations $30 (low-address byte) and $31 (high-address byte).
    The length of the list is contained in the first byte of the list.
    Since a byte is 8 bits wide, the list can contain up to 255 elements.

    ;THIS SUBROUTINE ARRANGES THE 8-BIT ELEMENTS OF A LIST IN ASCENDING
    ;ORDER.  THE STARTING ADDRESS OF THE LIST IS IN LOCATIONS $30 AND
    ;$31.  THE LENGTH OF THE LIST IS IN THE FIRST BYTE OF THE LIST.  LOCATION
    ;$32 IS USED TO HOLD AN EXCHANGE FLAG.

    SORT8    LDY #$00      ;TURN EXCHANGE FLAG OFF (= 0)
            STY $32
            LDA ($30),Y   ;FETCH ELEMENT COUNT
            TAX           ; AND PUT IT INTO X
            INY           ;POINT TO FIRST ELEMENT IN LIST
            DEX           ;DECREMENT ELEMENT COUNT
    NXTEL    LDA ($30),Y   ;FETCH ELEMENT
            INY
            CMP ($30),Y   ;IS IT LARGER THAN THE NEXT ELEMENT?
            BCC CHKEND
            BEQ CHKEND
                        ;YES. EXCHANGE ELEMENTS IN MEMORY
            PHA           ; BY SAVING LOW BYTE ON STACK.
            LDA ($30),Y   ; THEN GET HIGH BYTE AND
            DEY           ; STORE IT AT LOW ADDRESS
            STA ($30),Y
            PLA           ;PULL LOW BYTE FROM STACK
            INY           ; AND STORE IT AT HIGH ADDRESS
            STA ($30),Y
            LDA #$FF      ;TURN EXCHANGE FLAG ON (= -1)
            STA $32
    CHKEND   DEX           ;END OF LIST?
            BNE NXTEL     ;NO. FETCH NEXT ELEMENT
            BIT $32       ;YES. EXCHANGE FLAG STILL OFF?
            BMI SORT8     ;NO. GO THROUGH LIST AGAIN
            RTS           ;YES. LIST IS NOW ORDERED

    Subroutine SORT8 begins by initializing an exchange flag.
    The exchange flag is an indicator in memory location $32 that can be interrogated
    upon completion of a sorting pass to find out whether any elements were exchanged
    during that pass (flag=-1) or if the pass was exected with no exchanges (flag=0).
    The latter case indicates that the list is completely ordered and needs no further sorting.

    After loading the element count into the X register, the 6502 microprocessor
    enters an element compare loop at NXTEL. As each element is fetched, it is compared
    to the next element in the list, with CMP ($30),Y. If this pair of elements are of
    equal value, or are in ascending (sorted) order, the subroutine then branches to
    CHKEND, to see if the element count in the X register has been decremented to zero
    (the end-of-list condition). Otherwise, the elements are exchanged (if the element
    pair is in the wrong order). The stack is used to save the lower-addressed element
    while the higher-addressed element is being relocated in memory. A zero page memory
    location could have been used to save the element, but it was observed that PHA and
    PLA both execute in one less cycle than their LDA and STA counterparts. Upon completion
    of an exchange operation, the exchange flag is turned on, by loading it with -1.

    Following the exchange, the element count is decremented with a DEX instruction
    (label CHKEND) and the subsequent BNE BXTEL instruction branches to NXTEL if the
    pass has not yet been completed. When the pass is completed, BIT $32 checkes whether
    the exhange is still off (Bit 7=0), or has been turned on (Bit 7=1) by an exchange
    operation during the pass. If an exchange occurred, the subroutine is reinitiated at
    ORDER8, otherwise RTS causes a return, with a now ordered list.
    """
    SEQUENCES_TO_TEST = [2, 10, 25, 50, 100, 200, 255]
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    for NUMBER_SEQUENCE_LENGTH in SEQUENCES_TO_TEST:
        # NUMBER_SEQUENCE_LENGTH = 10
        data = [NUMBER_SEQUENCE_LENGTH]
        data.extend(list(reversed([x for x in range(1, NUMBER_SEQUENCE_LENGTH + 1)])))
        EXPECTED_DATA = [NUMBER_SEQUENCE_LENGTH]
        EXPECTED_DATA.extend(sorted(data[1:]))

        cpu = None
        cpu = CPU6502(cycle_limit=3_000_000)
        cpu.reset(program_counter=0x0600)
        # Location of list to sort is in 0x0030 and 0x0031
        # List can be up to 255 elements
        program = [
            0xa0, 0x00, 0x84, 0x32, 0xb1, 0x30, 0xaa, 0xc8, 0xca, 0xb1, 0x30, 0xc8, 0xd1, 0x30, 0x90, 0x10,
            0xf0, 0x0e, 0x48, 0xb1, 0x30, 0x88, 0x91, 0x30, 0x68, 0xc8, 0x91, 0x30, 0xa9, 0xff, 0x85, 0x32,
            0xca, 0xd0, 0xe6, 0x24, 0x32, 0x30, 0xd9, 0x60
        ]

        cpu.loadProgram(instructions=program, memoryAddress=0x0600, mainProgram=True)
        cpu.loadProgram(instructions=data, memoryAddress=0x4400, mainProgram=False)
        cpu.memory[0x0030] = 0x00
        cpu.memory[0x0031] = 0x44
        # cpu.memoryDump(startingAddress=0x4400, endingAddress=0x4400 + len(data) - 1, display_format='Dec')
        cpu.execute()
        # cpu.printLog()
        # cpu.memoryDump(startingAddress=0x0600, endingAddress=0x0627)

        errors = False
        # print(f'\tTesting sort of {NUMBER_SEQUENCE_LENGTH} elements: Expected {EXPECTED_DATA[1:]} / got {cpu.memory[0x4401:0x4401 + NUMBER_SEQUENCE_LENGTH]} -- ', end='')
        print(f'\tTesting sort of {NUMBER_SEQUENCE_LENGTH} elements: ', end='')
        if cpu.memory[0x4401:0x4401 + NUMBER_SEQUENCE_LENGTH] == EXPECTED_DATA[1:]:
            print(f'{bcolors.OKGREEN}PASS{bcolors.ENDC} -- {cpu.cycles - 1:,} cycles. {cpu.execution_time}', end='\n')
        else:
            print(f'{bcolors.FAIL}FAIL{bcolors.ENDC} -- {cpu.cycles - 1:,} cycles.', end='\n')
            cpu.memoryDump(startingAddress=0x4400, endingAddress=0x4400 + len(data) - 1, display_format='Dec')
            errors = True

    if errors:
        return False
    return True


def sort_test_16_bits() -> bool:
    TEST_NAME = 'SORT TEST 16 BITS'
    """
    The sort subroutine discussed in the preceding example (see 8-bit Bubble Sort)
    was relatively simple because the elements were 8-bit values, and could be
    compared with a CMP instruction and exchanged without too much difficulty.
    Unfortunately, the 6502 microprocessor has no 16-bit compare instruction,
    so a comparison must be made by actually subtracting the elements and testing the
    status of the result; if a borrow occurs, the elements must be exchanged, otherwise
    the elements can remain in their present order. The SORT16 subroutine sorts 16-bit
    elements using the bubble-sort algorithm and a 16-bit "compare" sequence.

    ;THIS SUBROUTINE ARRANGES THE 16-BIT ELEMENTS OF A LIST IN
    ;ASCENDING ORDER.  THE STARTING ADDRESS OF THE LIST IS IN LOCATIONS
    ;$30 AND $31.  THE LENGTH OF THE LIST IS IN THE FIRST BYTE OF THE LIST.
    ;LOCATION $32 IS USED TO HOLD AN EXCHANGE FLAG.

    SORT16   LDY #$00     ;TURN EXCHANGE FLAG OFF (= 0)
            STY $32
            LDA ($30),Y  ;FETCH ELEMENT COUNT
            TAY          ;  AND USE IT TO INDEX LAST ELEMENT
    NXTEL    LDA ($30),Y  ;FETCH MSBY
            PHA          ;  AND PUSH IT ONTO STACK
            DEY
            LDA ($30),Y  ;FETCH LSBY
            SEC
            DEY
            DEY
            SBC ($30),Y  ; AND SUBTRACT LSBY OF PRECEDING ELEMENT
            PLA
            INY
            SBC ($30),Y  ; AND SUBTRACT MSBY OF PRECEDING ELEMENT
            BCC SWAP     ;ARE THESE ELEMENTS OUT OF ORDER?
            CPY #$02     ;NO. LOOP UNTIL ALL ELEMENTS COMPARED
            BNE NXTEL
            BIT $32      ;EXCHANGE FLAG STILL OFF?
            BMI SORT16   ;NO. GO THROUGH LIST AGAIN
            RTS

    ;THIS ROUTINE BELOW EXCHANGES TWO 16-BIT ELEMENTS IN MEMORY

    SWAP     LDA ($30),Y  ;SAVE MSBY1 ON STACK
            PHA
            DEY
            LDA ($30),Y  ;SAVE LSBY1 ON STACK
            PHA
            INY
            INY
            INY
            LDA ($30),Y  ;SAVE MSBY2 ON STACK
            PHA
            DEY
            LDA ($30),Y  ;LOAD LSBY2 INTO ACCUMULATOR
            DEY
            DEY
            STA ($30),Y  ; AND STORE IT AT LSBY1 POSITION
            LDX #$03
    SLOOP    INY          ;STORE THE OTHER THREE BYTES
            PLA
            STA ($30),Y
            DEX
            BNE SLOOP    ;LOOP UNTIL THREE BYTE STORED
            LDA #$FF     ;TURN EXCHANGE FLAG ON (= -1)
            STA $32
            CPY #04      ;WAS EXCHANGE DONE AT START OF LIST?
            BEQ SORT16   ;YES. GO THROUGH LIST AGAIN.
            DEY          ;NO. COMPARE NEXT ELEMENT PAIR
            DEY
            JMP NXTEL

    The SORT16 subroutine is designed with the same algorithm as SORT8, so the two
    subroutines have several characteristics in common. For example, both SORT8 and
    SORT16 have an exchange flag (in the same location, $32) that indicates whether
    or not an exchange occurred during the last pass through the list. Like SORT8,
    the SORT16 subroutine also compares adjacent elements (albeit with a 16-bit
    subtraction, as opposed to the simple 8-bit comparison of the SORT8) and has
    an exchange routine that interchanges misordered elements in memory.

    Aside from the fact that SORT8 and SORT16 operate on different size elements,
    the only other real difference between them is that SORT16 processes the list
    from the end and works upward, whereas, SORT8 process the list from the beginning
    and works downward. Why the difference in procedure? There is no good reason,
    other than to demonstrate that a bubble sort can operate in either direction.

    SORT16 starts by initializing the exchange flag to zero, and fetching the element
    count from the first byte of the list. Using that value to point Y at the last
    element, the 6502 microprocessor executes "compare" (subtraction) instructions.
    These instructions, which start with the NXTEL instruction, perform a double-precision
    subtraction. In this subtraction, the lest-significant bytes (LSBYs) are subtracted
    first, and any borrow from that operation is passed, via the Carry, to the subtraction
    of the most-significant bytes (MSBYs).

    Operations on multiple-precision elements typically require a lot of pointer
    manipulation, as you can see by the instructions that follow the NXTEL label.
    To get the higher-addressed LSBY, the Y register must be decremented from its
    MSBY position. Before decrementing the Y register, however, the higher-addressed
    MSBY is pushed onto the stack for later use. With several more Y register decrements,
    the two LSBYs are addressed and subtracted. The result of the subtraction is not saved,
    since we are only interested in the final status of the operation, not the numerical
    result.

            |           |                     |           |
            +-----------+                     +-----------+
    ADDR     |   LSBY1   |            ADDR     |   LSBY2   |
            +-----------+                     +-----------+
    ADDR + 1 |   MSBY1   |            ADDR + 1 |   MSBY2   |
            +-----------+                     +-----------+
    ADDR + 2 |   LSBY2   |            ADDR + 2 |   LSBY1   |
            +-----------+                     +-----------+
    ADDR + 3 |   MSBY2   |            ADDR + 3 |   MSBY1   |
            +-----------+                     +-----------+
            |           |                     |           |

        (A) Before Swap.                  (B) After Swap.

    Figure 1: Swapping two 16-bit values in memory.

    The most-significant bytes (MSBYs) are subtracted next, by retrieving the higher-addressed
    MSBY from the stack and subtracting the lower-addressed MSBY from it. With this subtraction,
    we can make the exchange/no-exchange decision based ont he state of the Carry flag. If Carry
    is set (no borrow occurred), the elements are in the correct order; if Carry is reset
    (a borrow occurred), the elements must be exchanged.

    Figure 1 shows what the SWAP routine actually does, by presenting the "before" and "after"
    diagrams of the exchanged 16-bit elements. The higher-valued elements initially resides in
    symbolic addresses ADDR + 2 and ADDR + 3, and its bytes are designated as LSBY2 and MSBY2.
    The lower-valued elements initially resides in symbolic addressed ADDR and ADDR + 1, and its
    bytes are designated LSBY1 and MSBY1. The sequence of the SWAP routine will be more easily
    understood if you refer to Figure 1 while studying the instructions of the routine.

    Due to the previous subtraction routine, the Y register index is pointing at MSBY1 when the
    SWAP routine is initiated. Taking advantage of this pointer, SWAP saves MSBY1 and the adjacent
    byte, LSBY1, on the stack. Recalling that information is retrieved from a stack in the opposite
    order from which it was entered on the stack, the MSBY1-then-LSBY1 push sequence implies which
    byte will be the next to be pushed onto the stack- it will be MSBY2. With these three bytes
    on the stack, the final byte LSBY2 is moved from ADDR + 2 (again, refer to Figure 1) to ADDR.
    A short loop (SLOOP) pulls bytes MSBY2, LSBY1, and MSBY1 off the stack and stores them in the
    locations following LSBY2. The SWAP routine ends by turning on the exchange flag in location $32.
    If Elements 1 and 2 were exchanged, a BEQ SORT16 instrucion branches to the top of the subroutine;
    otherwise, control jumps to NXTEL, for the next comparison.

    Address  Hexdump   Dissassembly
    -------------------------------
    $0600    a0 00     LDY #$00
    $0602    84 32     STY $32
    $0604    b1 30     LDA ($30),Y
    $0606    a8        TAY
    $0607    b1 30     LDA ($30),Y
    $0609    48        PHA
    $060a    88        DEY
    $060b    b1 30     LDA ($30),Y
    $060d    38        SEC
    $060e    88        DEY
    $060f    88        DEY
    $0610    f1 30     SBC ($30),Y
    $0612    68        PLA
    $0613    c8        INY
    $0614    f1 30     SBC ($30),Y
    $0616    90 09     BCC $0621
    $0618    c0 02     CPY #$02
    $061a    d0 eb     BNE $0607
    $061c    24 32     BIT $32
    $061e    30 e0     BMI $0600
    $0620    60        RTS
    $0621    b1 30     LDA ($30),Y
    $0623    48        PHA
    $0624    88        DEY
    $0625    b1 30     LDA ($30),Y
    $0627    48        PHA
    $0628    c8        INY
    $0629    c8        INY
    $062a    c8        INY
    $062b    b1 30     LDA ($30),Y
    $062d    48        PHA
    $062e    88        DEY
    $062f    b1 30     LDA ($30),Y
    $0631    88        DEY
    $0632    88        DEY
    $0633    91 30     STA ($30),Y
    $0635    a2 03     LDX #$03
    $0637    c8        INY
    $0638    68        PLA
    $0639    91 30     STA ($30),Y
    $063b    ca        DEX
    $063c    d0 f9     BNE $0637
    $063e    a9 ff     LDA #$ff
    $0640    85 32     STA $32
    $0642    c0 04     CPY #$04
    $0644    f0 ba     BEQ $0600
    $0646    88        DEY
    $0647    88        DEY
    $0648    4c 07 06  JMP $0607

    """
    SEQUENCES_TO_TEST = [2, 10, 25, 50, 100, 127]
    print(f'{bcolors.UNDERLINE}Running {TEST_NAME}{bcolors.ENDC}')
    for NUMBER_SEQUENCE_LENGTH in SEQUENCES_TO_TEST:
        data = [NUMBER_SEQUENCE_LENGTH * 2]
        EXPECTED_DATA = [NUMBER_SEQUENCE_LENGTH * 2]
        for x in range(1, NUMBER_SEQUENCE_LENGTH + 1, 1):
            data.append(0x00)
            data.append(NUMBER_SEQUENCE_LENGTH + 1 - x)
            EXPECTED_DATA.append(0x00)
            EXPECTED_DATA.append(x)
        # EXPECTED_DATA.extend(sorted(data[1:]))

        cpu = None
        cpu = CPU6502(cycle_limit=2_000_000)
        cpu.reset(program_counter=0x0600)
        # Location of list to sort is in 0x0030 and 0x0031
        # List can be up to 255 elements
        program = [
            0xa0, 0x00, 0x84, 0x32, 0xb1, 0x30, 0xa8, 0xb1, 0x30, 0x48, 0x88, 0xb1, 0x30, 0x38, 0x88, 0x88,
            0xf1, 0x30, 0x68, 0xc8, 0xf1, 0x30, 0x90, 0x09, 0xc0, 0x02, 0xd0, 0xeb, 0x24, 0x32, 0x30, 0xe0,
            0x60, 0xb1, 0x30, 0x48, 0x88, 0xb1, 0x30, 0x48, 0xc8, 0xc8, 0xc8, 0xb1, 0x30, 0x48, 0x88, 0xb1,
            0x30, 0x88, 0x88, 0x91, 0x30, 0xa2, 0x03, 0xc8, 0x68, 0x91, 0x30, 0xca, 0xd0, 0xf9, 0xa9, 0xff,
            0x85, 0x32, 0xc0, 0x04, 0xf0, 0xba, 0x88, 0x88, 0x4c, 0x07, 0x06
        ]

        cpu.loadProgram(instructions=program, memoryAddress=0x0600, mainProgram=True)
        cpu.loadProgram(instructions=data, memoryAddress=0x4400, mainProgram=False)
        cpu.memory[0x0030] = 0x00
        cpu.memory[0x0031] = 0x44
        # cpu.memoryDump(startingAddress=0x4400, endingAddress=0x4400 + len(data) - 1, display_format='Dec')
        cpu.execute()
        # cpu.printLog()
        # cpu.memoryDump(startingAddress=0x0600, endingAddress=0x0627)

        errors = False
        # print(f'\tTesting sort of {NUMBER_SEQUENCE_LENGTH} elements: Expected {EXPECTED_DATA[1:]} / got {cpu.memory[0x4401:0x4401 + NUMBER_SEQUENCE_LENGTH]} -- ', end='')
        print(f'\tTesting sort of {NUMBER_SEQUENCE_LENGTH} elements: ', end='')
        if cpu.memory[0x4401:0x4401 + NUMBER_SEQUENCE_LENGTH * 2] == EXPECTED_DATA[1:]:
            print(f'{bcolors.OKGREEN}PASS{bcolors.ENDC} -- {cpu.cycles - 1:,} cycles. {cpu.execution_time}', end='\n')
        else:
            print(f'{bcolors.FAIL}FAIL{bcolors.ENDC} -- {cpu.cycles - 1:,} cycles.', end='\n')
            cpu.memoryDump(startingAddress=0x4400, endingAddress=0x4400 + len(data) - 1, display_format='Dec')
            errors = True

    if errors:
        return False
    return True


def custom_tests():
    tests = [
        square_root_test,
        fibonacci_test,
        sort_test_8_bits,
        sort_test_16_bits,
    ]
    results = []
    for test in tests:
        results.append(test())
    return results


if __name__ == '__main__':
    custom_tests()
