"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.halted = False
        self.sp = 7

    def load(self):
        """Load a program into memory."""

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        # def main(argv): is a reserved func name for taking in sys args.

        # consider refactoring this into ls8.py. Have def main() in ls8.py and then pass arg in cpu.load()
        if len(sys.argv) != 2:
            print('Invalid number of args')
            sys.exit(1)

        try:
            with open(f"examples/{sys.argv[1]}") as f:
                address = 0
                for line in f:
                    comment_split = line.split("#")
                    # remove white spaces
                    num = comment_split[0].strip()
                    # second arg in casting int is selecting the base. binary = 2
                    try:
                        instruction = int(num, 2)
                        self.ram_write(instruction, address)
                        address += 1
                        # print("{:08b}: {:d}".format(instruction, instruction))
                    except:
                        # print("Can't convert stirng to number")
                        # continue in this use case keeps program running rather than skipping the rest of the lines.
                        continue
                self.reg[self.sp] = len(self.ram)-1
        except:
            # custom error handling
            print("File not found")
            sys.exit(1)

    def ram_read(self, mar):
        return self.ram[mar]
    
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

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

    def run(self):
        """Run the CPU."""

        def unknown_command(*argv):
            print("IDK this command. Shutting off!")
            sys.exit(1)
        
        def HLT(*argv):
            self.halted = True

        def LDI(operand_a, operand_b):
            self.reg[operand_a] = operand_b
            self.pc += 2
        
        def PRN(*argv):
            print(self.reg[self.ram_read(self.pc+1)])
            self.pc += 1
        
        # incoporate the alu() function later.
        def MUL(operand_a, operand_b):
            self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
            self.pc += 2
        
        def PUSH(operand_a, operand_b):
            self.reg[self.sp] -= 1
            stack_address = self.reg[self.sp]
            self.ram_write(self.reg[operand_a], stack_address)
            self.pc += 1
        
        def POP(operand_a, operand_b):
            stack_address = self.reg[self.sp]
            stack_top_val = self.ram_read(stack_address)
            self.reg[operand_a] =  stack_top_val
            self.reg[self.sp] += 1
            self.pc += 1

        def CALL(operand_a, operand_b):
            self.reg[self.sp] -= 1
            address_to_next_instruction = self.pc + 2
            self.ram_write(address_to_next_instruction, self.reg[self.sp])
            next_instruction = self.reg[operand_a]
            self.pc = next_instruction - 1
        def RET(operand_a, operand_b):
            self.pc = self.ram_read(self.reg[self.sp]) - 1
            self.reg[self.sp] += 1
        
        def ADD(operand_a, operand_b):
            self.reg[operand_a] = self.reg[operand_a] + self.reg[operand_b]
            self.pc += 2
        while not self.halted:
            command_to_execute = self.ram_read(self.pc)
            # print(command_to_execute)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            def commands(command):
                switcher = {
                    0b00000001: HLT,
                    0b10000010: LDI,
                    0b01000111: PRN,
                    0b10100010: MUL,
                    0b01000101: PUSH,
                    0b01000110: POP,
                    0b01010000: CALL,
                    0b00010001: RET,
                    0b10100000: ADD,
                }
                return switcher.get(command, unknown_command)   

            execute_command = commands(command_to_execute)
            execute_command(operand_a, operand_b)
            self.pc += 1