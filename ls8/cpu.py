"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        # self.fl = 0b00000000
        # self.position = 0
        # flag register
        self.fl = {
            'E': 0,
            'L': 0,
            'G': 0
        }
        self.branchtable = {}
        self.branchtable[130] = self.ldi
        self.branchtable[71] = self.prn
        self.branchtable[162] = self.mul
        self.branchtable[1] = self.hlt
        self.branchtable[69] = self.push
        self.branchtable[70] = self.pop
        self.branchtable[80] = self.call
        self.branchtable[17] = self.ret
        self.branchtable[160] = self.add
        self.branchtable[167] = self.cmp_f
        self.branchtable[85] = self.jeq
        self.branchtable[86] = self.jne
        self.branchtable[84] = self.jmp
        self.running = False
        # 7 is reserved as the stack pointer 
        self.sp = 7

    def load(self, filename):
        """Load a program into memory."""

        address = 0
        
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8  load 'immediate'; next value is the register number, subsequent number is the value to add to that register
        #     0b00000000, # register number
        #     0b00001000, # value to store in register
        #     0b01000111, # PRN R0 print value from register
        #     0b00000000, # register number
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        try:
            with open(filename) as f:
                for line in f:
                    split_line = line.split('#')

                    code_value = split_line[0].strip()
                    if code_value == '':
                        continue
                    
                    num = int(code_value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print(f'{sys.argv[1]} file not found')
            sys.exit(2)


    def alu(self, op):
        """ALU operations."""
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            # bit 2 set to 1 if a < b
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl['L'] = '1'
                self.fl['E'] = '0'
                self.fl['G'] = '0'
            # bit 1 set to 1 if a > b 
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl['G'] = '1'
                self.fl['E'] = '0'
                self.fl['L'] = '0'
             # bit 0 set to 1 if equal
            elif self.reg[reg_a] == self.reg[reg_b]:
                self.fl['E'] = '1'
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

    # MAR = memory address register, contains the address that is being read or written to
    # MDR = memory data register, contains the data that was read or the data to write

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr
        return self.ram[mar]

    def hlt(self):
        self.running = False
     # day 4 work implement stack, push, pop

    #  Decrement the SP
    # Copy the value in the given register to the address pointed to by SP
    def push(self):
        given_register = self.ram[self.pc + 1]
        value_in_register = self.reg[given_register]
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = value_in_register
        self.pc += 2 

    # Copy the value from the address pointed to by SP to the given register.
    # Increment SP.
    def pop(self):
        given_register = self.ram[self.pc + 1]
        value_from_memory = self.ram[self.reg[self.sp]]
        self.reg[given_register] = value_from_memory
        self.reg[self.sp] += 1
        self.pc += 2

    # subroutine calls
    # jump to address with CALL, and then return back to where you called from with RET 

    # Calls a subroutine (function) at the address stored in the register.
    # The address of the instruction directly after(above, in stack) CALL is pushed onto the stack.
    # The PC is set to the address stored in the given register.
    # We jump to that location in RAM and execute the first instruction in the subroutine.
    def call(self):
        given_register = self.ram[self.pc + 1]
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc = self.reg[given_register]

    # Return from subroutine.
    # Pop the value from the top of the stack and store it in the PC.
    def ret(self):
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def ldi(self):
        mar = self.ram_read(self.pc + 1)
        mdr = self.ram_read(self.pc + 2)
        self.reg[mar] = mdr
        self.pc += 3

    def prn(self):
        mar = self.ram_read(self.pc + 1)
        print(self.reg[mar])
        self.pc += 2

    def mul(self):
        a = self.ram_read(self.pc + 1)
        b = self.ram_read(self.pc + 2)
        self.alu('MUL', a, b)
        self.pc += 3

    def add(self):
        self.alu('ADD')
        self.pc += 3

    def cmp_f(self):
        self.alu('CMP')
        self.pc += 3
    # jump if equal flag set >> 0b1
    def jeq(self):
        if self.fl['E'] == '1':
            given_register = self.ram[self.pc + 1]
            self.pc = self.reg[given_register]
        else:
            self.pc += 2

    # jump if E falg NOT set >> 0b100 OR 0b010
    def jne(self):
        if self.fl['E'] == '0':
            given_register = self.ram[self.pc + 1]
            self.pc = self.reg[given_register]
        else:
            self.pc += 2
    # like GOTO, 1 way no-return
    def jmp(self):
        given_register = self.ram[self.pc + 1]
        self.pc = self.reg[given_register]

    def run(self):
        """Run the CPU."""
        self.running = True

        self.reg[self.sp] = len(self.ram)
        
        # print(self.ram)

        while self.running:
            ir = self.ram_read(self.pc)
            self.branchtable[ir]()