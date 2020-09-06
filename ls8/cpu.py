"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # step 1 in tk
        self.pc = 0
        self.reg = [0] * 8
        # LDI-load "immediate", store a value in a register, or "set this register to this value".
        self.LDI = 0b10000010
        # PRN-a pseudo-instruction that prints the numeric value stored in a register.
        self.PRN = 0b01000111
        # HLT-halt the CPU and exit the emulator.
        self.HLT = 0b00000001
        self.ram = [0] * 256
    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

        # step 2 in tk
        # ram_read function for memory address register
        # The MAR contains the address that is being read or written to.
    def ram_read(self, MAR):
        return self.ram[MAR]
        # ram_write function memory data register
        # The MDR contains the data that was read or the data to write.
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        # step 3 in tk
        # reads the memory address that's stored in register PC, and store that result in IR-the Instruction Register. 
        running = True
        #while running instructions
        while running:
            IR = self.ram[self.pc]
            #this will load immediate LDI if self.ldi
            if IR == self.LDI:
                self.ldi()
            #this will print PRN if self.prn
            if IR == self.PRN:
                self.prn()
            #this will halt HLT if self.hlt           
            if IR == self.HLT:
                running = self.hlt()
        # hlt function
    def hlt(self):
        self.pc += 1
        return False
    
        #ldi function
    def ldi(self):
        MAR = self.ram[self.pc + 1]
        MDR = self.ram[self.pc + 2]
        self.reg[MAR] = MDR
        self.pc += 3
    
        #prn function
    def prn(self):
        MAR = self.ram[self.pc + 1]
        print(self.reg[MAR])
        self.pc +=2
