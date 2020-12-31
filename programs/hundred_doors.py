name = "Hundred Doors"

description = """
There are 100 doors in a row that are all initially closed.

You make 100 passes by the doors.

The first time through, visit every door and  toggle  the door  (if the door is closed,  open it;   if it is open,  close it).

The second time, only visit every 2nd door   (door #2, #4, #6, ...),   and toggle it.

The third time, visit every 3rd door   (door #3, #6, #9, ...), etc,   until you only visit the 100th door.


Task

Answer the question:   what state are the doors in after the last pass?   Which are open, which are closed?


Alternate: As noted in this page's   discussion page,   the only doors that remain open are those whose numbers are perfect squares.

Opening only those doors is an   optimization   that may also be expressed; however, as should be obvious, this defeats the intent of comparing implementations across programming languages.
"""

asm_source = """
;assumes memory at $02xx is initially set to 0 and stack pointer is initialized
;the 1 to 100 door byte array will be at $0200-$0263 (decimal 512 to 611)
;Zero-page location $01 will hold delta
;At end, closed doors = $00, open doors = $01

start:  ldx #0        ;initialize index - first door will be at $200 + $0
        stx $1
        inc $1        ;start out with a delta of 1 (0+1=1)
openloop: inc $200,X    ;open X'th door
        inc $1        ;add 2 to delta
        inc $1
        txa           ;add delta to X by transferring X to A, adding delta to A, then transferring back to X
        clc           ;  clear carry before adding (6502 has no add-without-carry instruction)
        adc $1
        tax
        cpx #$64      ;check to see if we're at or past the 100th door (at $200 + $63)
        bmi openloop  ;jump back to openloop if less than 100
"""

program = [
    0xa2, 0x00,
    0x86, 0x01,
    0xe6, 0x01,
    0xfe, 0x00, 0x02,
    0xe6, 0x01,
    0xe6, 0x01,
    0x8a,
    0x18,
    0x65, 0x01,
    0xaa,
    0xe0, 0x64,
    0x30, 0xf0
]

starting_address = 0x8000

tests = [
    {
        'memory_range': [0x200, 0x263],
        'expected_values': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    }
]
