"""CPU functionality."""

import sys

LDI = 0b10000010 
PRN = 0b01000111 
HLT = 0b00000001
MUL = 0b10100010 
ADD = 0b10100000 
PUSH = 0b01000101
POP = 0b01000110
RET = 0b00010001
CALL = 0b01010000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0
        self.running = True

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def HLT(self):
        self.running = False

    def load(self):
        """Load a program into memory."""
        filename = sys.argv[1]
        address = 0

        with open(filename) as f:
            for line in f:
                line = line.split('#')[0].strip()
                if line == '':
                    continue
                else:
                    self.ram[address] = int(line, 2)
                    address += 1
                    

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if "ADD" is op:
            self.reg[reg_a] += self.reg[reg_b]
        elif "SUB" is op:
            self.reg[reg_a] -= self.reg[reg_b]
        elif "MUL" is op:
            self.reg[reg_a] *= self.reg[reg_b]
        elif "DIV" is op:
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.load()

        while self.running:
            instruction_register = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if instruction_register == HLT:
                self.running = False
                self.pc += 1

            elif LDI is instruction_register:
                self.reg[operand_a] = operand_b
                self.pc += 3

            elif PRN is instruction_register:
                print(self.reg[operand_a])
                self.pc += 2

            elif MUL is instruction_register:
                self.reg[operand_a] *= self.reg[operand_b]
                self.pc += 3

            elif PUSH is instruction_register:
                v = self.reg[operand_a]
                self.reg[SP] -= 1
                self.ram_write(self.reg[SP], v)
                self.pc += 2

            elif POP is instruction_register:
                v = self.ram_read(self.reg[SP])
                self.reg[SP] += 1
                self.reg[operand_a] = v
                self.pc += 2

            elif CALL is instruction_register:
                self.reg[SP] -= 1
                stack_address = self.reg[SP]
                returned_address = self.pc + 2
                self.ram_write(stack_address, returned_address)
                register_number = self.ram_read(self.pc + 1)
                self.pc = self.reg[register_number]

            elif RET is instruction_register:
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1  

            elif CMP is instruction_register:
                value_a = self.reg[operand_a]
                value_b = self.reg[operand_b]
                if value_a == value_b:
                    self.flags = 0b1
                elif value_a > value_b:
                    self.flags = 0b10
                elif value_b > value_a:
                    self.flags = 0b100
                self.pc += 3

            elif JMP is instruction_register:
                self.pc = self.reg[operand_a]

            elif JEQ is instruction_register:
                if not self.flags & 0b1:
                    self.pc += 2
                elif self.flags & 0B1:
                    self.pc = self.reg[operand_a]

            elif JNE is instruction_register:
                if self.flags & 0b1:
                    self.pc += 2
                elif not self.flags & 0b0:
                    self.pc = self.reg[operand_a]
            else:
                print(f"Instruction '{instruction_register}'' at address '{self.pc}' is not recognized")
                self.pc += 1
