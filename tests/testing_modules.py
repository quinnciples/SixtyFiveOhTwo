import sys
sys.path.insert(0, '..\\SixtyFiveOhTwo')
from SixtyFiveOhTwo import CPU6502


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


def generateProgram(instruction: str, registers: dict, immediate_value: int, zp_address: int, ind_zp_address: int, sixteen_bit_address: int, CYCLE_COUNTS: dict) -> list:
    program = {}

    for opcode, command in CPU6502.opcodes.items():
        ins_set = command.split('_')
        instruct = ins_set[0]
        if instruct != instruction:
            continue
        address_mode = '_'.join(_ for _ in ins_set[1:])
        if '_ACC' in address_mode:
            continue
        else:
            instructions = []
            if address_mode == 'IM':
                instructions = [opcode, immediate_value]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ZP':
                instructions = [opcode, zp_address]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            elif address_mode == 'ZP_X':
                instructions = [opcode, zp_address - registers.get('X', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            elif address_mode == 'ZP_Y':
                instructions = [opcode, zp_address - registers.get('Y', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS':
                instructions = [opcode, sixteen_bit_address & 0b0000000011111111, (sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS_X':
                target_sixteen_bit_address = sixteen_bit_address - registers.get('X', 0)
                instructions = [opcode, target_sixteen_bit_address & 0b0000000011111111, (target_sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'ABS_Y':
                target_sixteen_bit_address = sixteen_bit_address - registers.get('Y', 0)
                instructions = [opcode, target_sixteen_bit_address & 0b0000000011111111, (target_sixteen_bit_address & 0b1111111100000000) >> 8]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'IND_X':
                instructions = [opcode, ind_zp_address - registers.get('X', 0)]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

            if address_mode == 'IND_Y':
                instructions = [opcode, ind_zp_address]
                program[address_mode] = [instructions, CYCLE_COUNTS[address_mode]]

    return program


if __name__ == '__main__':
    pass