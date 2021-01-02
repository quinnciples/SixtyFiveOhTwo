name = "APPLE I PRINT CHARACTERS"

description = """
Prints the available ASCII characters to the screen
"""

asm_source = """

"""

program = [
    0xA9, 0x00,  # LDA_IM 0x00
    0xAA,  # TAX
    0x20, 0xEF, 0xFF,  # JSR 0xFFEF
    0xE8,  # INX
    0x8A,  # TXA
    0x4C, 0x02, 0x00  # JMP 0x0002
]

starting_address = 0x0000

tests = [
    {
        'memory_range': None,
        'expected_values': None
    }
]
