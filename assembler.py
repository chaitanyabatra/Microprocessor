import sys
import re

def is_register(reg):
    return reg in ["ax", "bx", "cx", "dx"]

def get_code_reg(reg):
    if reg == "ax":
        return "00"
    elif reg == "bx":
        return "01"
    elif reg == "cx":
        return "10"
    elif reg == "dx":
        return "11"
    else:
        return ""

def is_immediate_valid(imm):
    try:
        im = int(imm)
        return 0 <= im <= 254
    except ValueError:
        print("> Error, register and/or immediate value doesn't exist!")
        sys.exit(0)

def encode_alu(inst1, inst2, opcode, args, num):
    if len(args) == 2 and is_register(args[0]):
        if is_register(args[1]):
            regs_tmp = int(get_code_reg(args[0]) + get_code_reg(args[1]), 2)
            regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
            return inst1 + regs + "ff"
        else:
            if is_immediate_valid(args[1]):
                regs_tmp = int(get_code_reg(args[0]) + "00", 2)
                regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
                imm = format(int(args[1]), "02x")
                return inst2 + regs + imm
            else:
                print(f"{num}: {opcode} {args[0]},¿{args[1]}?")
                print("> Error, immediate value is out of limits: 0-254!")
                sys.exit(0)
    else:
        print(f"{num}: ¿{opcode} {args[0]}?")
        print("> Error, instruction has invalid arguments!")
        sys.exit(0)

def encode(opcode, args, num, tab_labels):
    hex_code = ""
    opcode = opcode.lower()
    if not args:
        print(f"Error: Missing arguments for opcode {opcode} at line {num}")
        sys.exit(0)
    # Rest of the function remains unchanged

    if len(args) > 1:
        args[0] = args[0].lower()
        args[1] = args[1].lower()
    else:
        args[0] = args[0].lower()

    if opcode == "or":
        return encode_alu("0", "0", "OR", args, num)
    elif opcode == "not":
        if len(args) == 1 and is_register(args[0]):
            regs_tmp = int(get_code_reg(args[0]) + "00", 2)
            regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
            return "1" + regs + "ff"
        else:
            print(f"{num}: ¿{opcode} {args[0]}?")
            print("> Error, instruction has invalid registers!")
            sys.exit(0)
    elif opcode == "and":
        return encode_alu("2", "2", "AND", args, num)
    elif opcode == "xor":
        return encode_alu("3", "3", "XOR", args, num)
    elif opcode == "add":
        return encode_alu("4", "4", "ADD", args, num)
    elif opcode == "sub":
        return encode_alu("5", "5", "SUB", args, num)
    elif opcode == "mult":
        return encode_alu("6", "6", "MULT", args, num)
    elif opcode == "div":
        return encode_alu("7", "7", "DIV", args, num)
    elif opcode == "mov":
        return encode_alu("8", "9", "MOV", args, num)
    elif opcode == "load":
        if len(args) == 2 and is_register(args[0]) and is_register(args[1]):
            regs_tmp = int(get_code_reg(args[0]) + get_code_reg(args[1]), 2)
            regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
            return "a" + regs + "ff"
        else:
            print(f"{num}: ¿LOAD?")
            print("> Error, instruction has invalid arguments, its correct form: STORE REGDest, REGSource")
            sys.exit(0)
    elif opcode == "store":
        if len(args) == 2 and is_register(args[0]) and is_register(args[1]):
            regs_tmp = int(get_code_reg(args[0]) + get_code_reg(args[1]), 2)
            regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
            return "b" + regs + "ff"
        else:
            print(f"{num}: ¿STORE?")
            print("> Error, instruction has invalid arguments, its correct form: STORE REGDest, REGSource")
            sys.exit(0)
    elif opcode in ["jmpz", "jmpn", "jmpp"]:
        if len(args) == 1:
            if is_register(args[0]):
                regs_tmp = int("00" + get_code_reg(args[0]), 2)
                regs = str(regs_tmp) if regs_tmp <= 9 else chr(regs_tmp + 87)
                return f"{ord('c')+['jmpz','jmpn','jmpp'].index(opcode)}{regs}ff"
            else:
                if args[0] in tab_labels:
                    imm = format(tab_labels[args[0]], "02x")
                    return f"{chr(ord('c')+['jmpz','jmpn','jmpp'].index(opcode))}0{imm}"
                else:
                    print(f"{num}: ¿{opcode} {args[0]}?")
                    print("> Error, label doesn't exist, check your code!")
                    sys.exit(0)
        else:
            print("> Error, instruction has invalid registers!")
            sys.exit(0)
    elif opcode == "halt":
        return "f000"
    else:
        print("> Error: Unknown opcode!")
        sys.exit(0)

def processar(file):
    tab_labels = {}

    try:
        with open(file, "r") as asm, open(file + ".hex", "w") as hex_file:
            hex_file.write("v2.0 raw\n0000 ")

            line_count = 1
            for line in asm:
                line = line.strip()
                if line and not line.startswith("#"):
                    is_label = line.endswith(":")
                    if is_label:
                        label = line[:-1]
                        if label in tab_labels:
                            print(f"> Error: Label '{label}' already exists!")
                            sys.exit(0)
                        tab_labels[label] = line_count
                    else:
                        line = re.sub(r"#.*", "", line).strip()
                        tokens = re.split(r"\s*,\s*|\s+", line)
                        instruction = encode(tokens[0], tokens[1:], line_count, tab_labels)
                        hex_file.write(instruction + " ")
                        print(f"Instruction: {{{instruction}}} --- {line}")
                        line_count += 1

            print("------------------------------------------------------------------")
            print("'Assembling' successfully done, memory consumption:", line_count * 2, "bytes")
            print("Have a nice day, :D")
            print("------------------------------------------------------------------")

    except FileNotFoundError:
        print("Input file does not exist, check the entered name!")
        sys.exit(0)
    except IOError:
        print("I/O error!")
        sys.exit(0)

if __name__ == "__main__":
    print("-----------------------------------------------")

    file = input("Enter the file name to be processed: ")
    processar(file)
