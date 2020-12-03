# 6502 machine code processor


class CPU6502:

    version = '0.01'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    opcodes = {0xA9: 'LDA_IM',
               0xA5: 'LDA_ZP',
               0xEA: 'NOP'}

    def __init__(self, cycle_limit=10):

        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100
        self.cycle_limit = cycle_limit

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

    def cycleInc(self):
        self.logState()
        self.cycles += 1

    def programCounterInc(self):
        self.program_counter += 1
        if self.program_counter >= CPU6502.MAX_MEMORY_SIZE:
            self.program_counter = 0

    def reset(self):
        self.program_counter = 0xFFFC
        self.stack_pointer = 0x0100
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)

        # Reset all flags to zero
        self.flags = dict.fromkeys(self.flags.keys(), 0)

        self.memory = [0] * CPU6502.MAX_MEMORY_SIZE

    def readMemory(self, increment_pc=True, address=None) -> int:
        self.cycleInc()
        if not address:
            data = self.memory[self.program_counter]
        else:
            data = self.memory[address]

        if increment_pc:
            self.programCounterInc()
        return data

    def execute(self):
        while self.cycles <= self.cycle_limit:
            data = self.readMemory()
            opcode = CPU6502.opcodes.get(data, 0)  # Use the NOP code as a safe default?
            if opcode == 'LDA_IM':
                # Load memory into accumulator
                data = self.readMemory()
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.flags['Z'] = 1
                else:
                    self.flags['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.flags['N'] = 1
                else:
                    self.flags['N'] = 0
            elif opcode == 'LDA_ZP':
                zp_address = self.readMemory()
                data = self.readMemory(address=zp_address, increment_pc=False)
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.flags['Z'] = 1
                else:
                    self.flags['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.flags['N'] = 1
                else:
                    self.flags['N'] = 0
            elif opcode == 'NOP':
                self.cycleInc()

    def printState(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 4)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 4)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles}, **self.registers, **self.flags, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 4)}}
        valueString = '\t'.join(str(v) for v in combined.values())
        self.log.append(valueString)

    def printLog(self):
        for line in self.log:
            print(line)

    def loadProgram(self, instructions=[], memoryAddress=0x0000):
        for ins in instructions:
            self.memory[memoryAddress] = ins
            if memoryAddress >= CPU6502.MAX_MEMORY_SIZE - 1:
                memoryAddress = 0
            else:
                memoryAddress += 1


cpu = CPU6502()
cpu.reset()
cpu.memory[0xCC] = 0xFFFF
cpu.loadProgram(instructions=[0xA9, 0x20, 0xEA, 0xA5, 0x00CC, 0xEA], memoryAddress=0xFFFC)
cpu.execute()
cpu.printLog()
