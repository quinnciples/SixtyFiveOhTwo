from cpu6502 import CPU6502
import msvcrt


class PIA():

    def __init__(self, memory=None):
        self.hooks = {
            'KBD': 0xD010,
            'KBDCR': 0xD011,
            'DSP': 0xD012,
            'DSPCR': 0xD013
        }
        assert(memory is not None)
        self.memory = memory
        self.chars = 0

    def cycle(self):
        # Printing character to the screen
        if (self.memory[self.hooks['DSP']] & 0b10000000) > 0:
            self.memory[self.hooks['DSP']] = self.memory[self.hooks['DSP']] & 0b01111111
            self.value = self.memory[self.hooks['DSP']]
            if self.value >= 0x20 or self.value == 0x08:  # Covers ASCII letters, numbers, or backspace (0x08)
                print(chr(self.value), end='', flush=True)
                self.chars += 1

            if self.value == 0x0D or self.chars >= 40:
                print('', flush=True)
                self.chars = 0

        # Handling keyboard input
        if msvcrt.kbhit():
            key = msvcrt.getch().upper()
            key_ascii = ord(key)
            self.memory[self.hooks['KBD']] = key_ascii | 0b10000000
            self.memory[self.hooks['KBDCR']] = self.memory[self.hooks['KBDCR']] | 0b10000000


cpu = CPU6502(cycle_limit=100_000_000, printActivity=False, enableBRK=False, logging=False, continuous=False)
mem = cpu.get_memory()
pia = PIA(memory=mem)


import programs.wozmon
wozmon_program = programs.wozmon.program
wozmon_address = programs.wozmon.starting_address

import programs.apple_1_basic
basic_program = programs.apple_1_basic.program
basic_address = programs.apple_1_basic.starting_address

import programs.codebreaker

""" SAMPLE PROGRAM
    5 P=500
   10 P=P+1
   15 IF P>510 THEN GOTO 200
   50 M=P/2
   51 C=1
   52 C=C+1
   53 IF C>M THEN GOTO 60
   55 IF (P/C)*C=P THEN GOTO 100
   58 GOTO 52
   60 PRINT P;" IS PRIME"
   70 GOTO 10
   80 GOTO 200
  100 PRINT P;" IS DIVISIBLE BY ";C
  110 GOTO 10
  200 END
"""

cpu.load_program(instructions=wozmon_program, memoryAddress=wozmon_address, mainProgram=False)
cpu.load_program(instructions=basic_program, memoryAddress=basic_address, mainProgram=False)
# for tape in programs.codebreaker.tapes:
#     cpu.load_program(instructions=tape['data'], memoryAddress=tape['starting_address'], mainProgram=False)
cpu.program_counter = wozmon_address
print(f'Running {programs.apple_1_basic.name}...')
print(programs.apple_1_basic.description)
print(programs.apple_1_basic.instructions)
# print(programs.codebreaker.instructions)

try:
    while True:
        cpu.execute()
        pia.cycle()

except Exception as e:
    print(e)

finally:
    cpu.print_benchmark_info()
    from PIL import Image

    SCALE = 4
    ITEMS_PER_ROW = 256
    img = Image.new('RGB', (ITEMS_PER_ROW * SCALE, CPU6502.MAX_MEMORY_SIZE // ITEMS_PER_ROW * SCALE), "black")  # Create a new black image
    pixels = img.load()  # Create the pixel map
    print('x', img.size[0], 'y', img.size[1])
    for i, pix in enumerate(mem):
        # print(i, i % 16, i // 16)
        color_value = pix
        for x_offset in range(SCALE):
            for y_offset in range(SCALE):
                pixels[(i % ITEMS_PER_ROW) * SCALE + x_offset, (i // ITEMS_PER_ROW) * SCALE + y_offset] = (color_value, color_value, color_value)  # Set the colour accordingly
    # img.show()
    # img.save('memory.png')
