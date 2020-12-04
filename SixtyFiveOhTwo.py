# 6502 machine code processor


class CPU6502:

    version = '0.01'
    MAX_MEMORY_SIZE = 1024 * 64  # 64k memory size
    opcodes = {0xA9: 'LDA_IM',
               0xA5: 'LDA_ZP',
               0xB5: 'LDA_ZPX',
               0xAD: 'LDA_ABS',
               0xBD: 'LDA_ABS_X',
               0x20: 'JSR',
               0xEA: 'NOP'}

    def __init__(self, cycle_limit=20):

        self.program_counter = 0xFFCC
        self.stack_pointer = 0x0100
        self.cycle_limit = cycle_limit

        self.INS = None

        self.registers = {
            'A': 0,
            'X': 0,
            'Y': 0,
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

    def memoryDump(self, startingAddress=0x0000, endingAddress=0x0000):
        print('\nMemory Dump:\n')
        while startingAddress <= endingAddress and startingAddress <= CPU6502.MAX_MEMORY_SIZE:
            header = '0x{0:0{1}X}'.format(startingAddress, 4) + '\t'
            row = '\t'.join('0x{0:0{1}X}'.format(self.memory[v], 2) for v in range(startingAddress, min(startingAddress + 8, CPU6502.MAX_MEMORY_SIZE)))
            line = header + row
            print(line)
            startingAddress += 8

    def cycleInc(self):
        self.logState()
        self.cycles += 1

    def programCounterInc(self):
        self.program_counter += 1
        if self.program_counter >= CPU6502.MAX_MEMORY_SIZE:
            self.program_counter = 0

    def reset(self):
        self.program_counter = 0xFFCC
        self.stack_pointer = 0x0100
        self.cycles = 0

        # Reset all registers to zero
        self.registers = dict.fromkeys(self.registers.keys(), 0)

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
        data = self.readMemory()
        while self.cycles <= self.cycle_limit and CPU6502.opcodes.get(data, None) is not None:
            opcode = CPU6502.opcodes.get(data, None)  # Use the NOP code as a safe default?
            self.INS = opcode
            if opcode == 'LDA_IM':
                # Load memory into accumulator
                data = self.readMemory()
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.registers['Z'] = 1
                else:
                    self.registers['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.registers['N'] = 1
                else:
                    self.registers['N'] = 0
            elif opcode == 'LDA_ZP':
                zp_address = self.readMemory()
                data = self.readMemory(address=zp_address, increment_pc=False)
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.registers['Z'] = 1
                else:
                    self.registers['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.registers['N'] = 1
                else:
                    self.registers['N'] = 0
            elif opcode == 'LDA_ZPX':
                zp_address = self.readMemory()
                zp_address += int(self.registers['X'])
                # Zero Page address wraps around if the value exceeds 0xFF
                while zp_address > 0xFF:
                    zp_address -= 0x100
                self.cycleInc()
                data = self.readMemory(address=zp_address, increment_pc=False)
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.registers['Z'] = 1
                else:
                    self.registers['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.registers['N'] = 1
                else:
                    self.registers['N'] = 0

            elif opcode == 'LDA_ABS':
                address = self.readMemory()
                address += (self.readMemory() * 0x100)
                data = self.readMemory(address=address, increment_pc=False)
                self.registers['A'] = data
                # Check to set zero flag
                if self.registers['A'] == 0:
                    self.registers['Z'] = 1
                else:
                    self.registers['Z'] = 0
                # Check to set negative flag
                if self.registers['A'] & 0b10000000 > 0:
                    self.registers['N'] = 1
                else:
                    self.registers['N'] = 0

            elif opcode == 'NOP':
                self.cycleInc()
            data = self.readMemory()

    def printState(self):
        combined = {**{'Cycle': self.cycles, 'INS': self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        valueString = '\t'.join(str(v) for v in combined.values())
        print(headerString)
        print(valueString)

    def initializeLog(self):
        combined = {**{'Cycle': self.cycles, 'INS': self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        headerString = '\t'.join(combined)
        self.log.append(headerString)

    def logState(self):
        combined = {**{'Cycle': self.cycles, 'INS': self.INS}, **self.registers, **{'SP': '0x{0:0{1}X}'.format(self.stack_pointer, 4), 'PC': '0x{0:0{1}X}'.format(self.program_counter, 4), 'MEM': '0x{0:0{1}X}'.format(self.memory[self.program_counter], 2)}}
        valueString = '\t'.join(str(v) for v in combined.values())
        self.log.append(valueString)

    def printLog(self):
        for line in self.log:
            print(line)

    def loadProgram(self, instructions=[], memoryAddress=0x0000):
        for ins in instructions:
            self.memory[memoryAddress] = ins
            memoryAddress += 1
            if memoryAddress >= CPU6502.MAX_MEMORY_SIZE:
                memoryAddress = 0


cpu = CPU6502()
cpu.reset()
cpu.memory[0x00CC] = 0x02
cpu.memory[0x0080] = 0x03
cpu.memory[0xFFC3] = 0x04
cpu.loadProgram(instructions=[0xA9, 0x01, 0xA5, 0xCC, 0xB5, 0x80, 0xAD, 0xC3, 0xFF], memoryAddress=0xFFCC)
cpu.execute()
cpu.printLog()
cpu.memoryDump(startingAddress=0xFFC3, endingAddress=0xFFDA)
