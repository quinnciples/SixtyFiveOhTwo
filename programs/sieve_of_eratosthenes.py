name = "Sieve of Eratosthenes"

description = """
The Sieve of Eratosthenes is a simple algorithm that finds the prime numbers up to a given integer.

Task
Implement the Sieve of Eratosthenes algorithm, with the only allowed optimization that the outer loop can stop at the square root of the limit, and the inner loop may start at the square of the prime just found.
That means especially that you shouldn't optimize by using pre-computed wheels, i.e. don't assume you need only to cross out odd numbers (wheel based on 2), numbers equal to 1 or 5 modulo 6 (wheel based on 2 and 3), or similar wheels based on low primes.
If there's an easy way to add such a wheel based optimization, implement it as an alternative version.

Note
    It is important that the sieve algorithm be the actual algorithm used to find prime numbers for the task.
"""

asm_source = """
ERATOS: STA  $D0      ; value of n
        LDA  #$00
        LDX  #$00
SETUP:  STA  $1000,X  ; populate array
        ADC  #$01
        INX
        CPX  $D0
        BPL  SET
        JMP  SETUP
SET:    LDX  #$02
SIEVE:  LDA  $1000,X  ; find non-zero
        INX
        CPX  $D0
        BPL  SIEVED
        CMP  #$00
        BEQ  SIEVE
        STA  $D1      ; current prime
MARK:   CLC
        ADC  $D1
        TAY
        LDA  #$00
        STA  $1000,Y
        TYA
        CMP  $D0
        BPL  SIEVE
        JMP  MARK
SIEVED: LDX  #$01
        LDY  #$00
COPY:   INX
        CPX  $D0
        BPL  COPIED
        LDA  $1000,X
        CMP  #$00
        BEQ  COPY
        STA  $2000,Y
        INY
        JMP  COPY
COPIED: TYA           ; how many found
        RTS
"""

program = [
    0xa9, 0x80,
    0x85, 0xd0, 0xa9, 0x00, 0xa2, 0x00, 0x9d, 0x00, 0x10, 0x69, 0x01, 0xe8, 0xe4, 0xd0,
    0x10, 0x03, 0x4c, 0x08, 0x06, 0xa2, 0x02, 0xbd, 0x00, 0x10, 0xe8, 0xe4, 0xd0, 0x10, 0x17, 0xc9,
    0x00, 0xf0, 0xf4, 0x85, 0xd1, 0x18, 0x65, 0xd1, 0xa8, 0xa9, 0x00, 0x99, 0x00, 0x10, 0x98, 0xc5,
    0xd0, 0x10, 0xe4, 0x4c, 0x25, 0x06, 0xa2, 0x01, 0xa0, 0x00, 0xe8, 0xe4, 0xd0, 0x10, 0x0e, 0xbd,
    0x00, 0x10, 0xc9, 0x00, 0xf0, 0xf4, 0x99, 0x00, 0x20, 0xc8, 0x4c, 0x3a, 0x06, 0x98, 0x60
]

starting_address = 0x0600

tests = [
    {
        'memory_range': [0x1000, 0x1000 + 127],
        'expected_values': [0, 1, 2, 3, 0, 5, 0, 7, 0, 0, 0, 11, 0, 13, 0, 0, 0, 17, 0, 19, 0, 0, 0, 23, 0, 0, 0, 0, 0, 29, 0, 31, 0, 0, 0, 0, 0, 37, 0, 0, 0, 41, 0, 43, 0, 0, 0, 47, 0, 0, 0, 0, 0, 53, 0, 0, 0, 0, 0, 59, 0, 61, 0, 0, 0, 0, 0, 67, 0, 0, 0, 71, 0, 73, 0, 0, 0, 0, 0, 79, 0, 0, 0, 83, 0, 0, 0, 0, 0, 89, 0, 0, 0, 0, 0, 0, 0, 97, 0, 0, 0, 101, 0, 103, 0, 0, 0, 107, 0, 109, 0, 0, 0, 113, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 127]
    }
]
