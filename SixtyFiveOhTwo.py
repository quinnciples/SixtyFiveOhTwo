# 6502 machine code processor


class CPU6502:

    version = '0.01'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    opcodes = {0xA9: 'LDA_IM',
               0xA5: 'LDA_ZP'}

    def __init__(self):

        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100

        self.registers = {
            'A': 0,
            'X': 0,
            'Y': 0
        }

        self.flags = {
            'C': 0,
            'Z': 0,
            'I': 0,
            'D': 0,
            'B': 0,
            'V': 0,
            'N': 0
        }

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE
        self.cycles = 0
        self.log = []

        self.initializeLog()
        self.logState()

    def reset(self):
        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)

        # Reset all flags to zero
        self.flags = dict.fromkeys(self.flags.keys(), 0)

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

    def readMemory(self, location):
        self.program_counter += 1
        data = self.memory[location]
        return data

    def printState(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4)}}
        valueString = '\t'.join(str(v) for v in combined.values())
        self.log.append(valueString)

    def printLog(self):
        for line in self.log:
            print(line)


cpu = CPU6502()
cpu.reset()
