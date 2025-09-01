# Chip8 Emulator

This project is a cross-platform CHIP-8 emulator written in Python. It reproduces the core components of the CHIP-8 virtual machine, including CPU, memory, input, and graphics handling. The emulator can run classic CHIP-8 ROMs, features debugging tools such as opcode tracing and program counter history, and includes a custom build system for packaging.

In addition to the emulator, the project also provides a custom CHIP-8 compiler, allowing programs written in a asm-like language to be translated into CHIP-8 opcodes.

This project is primarily an educational effort, helping me learn how emulation works under the hood, from instruction decoding to memory management, while also exploring compiler design for retro architectures.

## 🔨 Build & Scripts

This project uses a Makefile to automate building, cleaning, running in dev mode, and compiling CHIP-8 programs.

### 📦 Build the emulator
```bash
make build
```


Builds the emulator with PyInstaller and generates executables inside dist/.

On Windows, a .ico icon is used. On Linux, a .png is applied. On macOS, no icon is set by default.

### 🧹 Clean build files
```bash
make clean
```


Removes the generated files in build/.

### 🚀 Development mode

```bash
make dev
```

Runs the emulator directly with Python using the test ROM defined in:

```bash
DEV_ROM_PATH = assets/roms/test.ch8
```

### 📝 Compile a CHIP-8 program
```bash
make compile PROGRAM_SRC=examples/hello.c8s PROGRAM_OUT=build/rom.ch8
```


Calls your compiler.py script to transform a CHIP-8 source program into binary.

PROGRAM_SRC → path to the CHIP-8 source file

PROGRAM_OUT → output path for the compiled file

## C8Script Language Specifications

C8Script is a lightweight assembly-like language for CHIP-8 programs. It provides symbolic mnemonics for CHIP-8 opcodes, along with labels and comments to improve readability.

### 1. Instructions

Each instruction corresponds to a CHIP-8 opcode. The general form is:

```
MNEMONIC [operands]
```

Operands may be registers (Vx), immediate values (N, NN or NNN), or constants depending on the instruction.

**Supported Instructions**
- **WAIT** – 0x0FFF
- **CLS** – Clear the display (0x00E0)
- **RET** – Return from subroutine (0x00EE)
- **JP addr** – Jump to address NNN (0x1NNN)
- **CALL addr** – Call subroutine at NNN (0x2NNN)
- **SE Vx, NN** – Skip if Vx == NN (0x3XNN)
- **SNE Vx, NN** – Skip if Vx != NN (0x4XNN)
- **SE_REG Vx, Vy** – Skip if Vx == Vy (0x5XY0)
- **LD Vx, NN** – Load immediate NN into register Vx (0x6XNN)
- **ADD Vx, NN** – Add immediate NN to Vx (0x7XNN)
- **LD_REG** Vx, Vy – Copy value of Vy into Vx (0x8XY0)
- **OR Vx, Vy** – Bitwise OR (0x8XY1)
- **AND Vx, Vy** – Bitwise AND (0x8XY2)
- **XOR Vx, Vy** – Bitwise XOR (0x8XY3)
- **ADD_REG Vx, Vy** – Add Vy to Vx, store result in Vx (0x8XY4)
- **SUB Vx, Vy** – Subtract Vy from Vx (0x8XY5)
- **SHR Vx** – Shift right (0x8X06)
- **SUBN Vx, Vy** – Vx = Vy - Vx (0x8XY7)
- **SHL Vx** – Shift left (0x8X0E)
- **SNE_REG Vx, Vy** – Skip if Vx != Vy (0x9XY0)
- **LD_I addr** – Load index register I with NNN (0xANNN)
- **JP_V0 addr** – Jump to V0 + NNN (0xBNNN)
- **RND Vx, NN** – Vx = random & NN (0xCXNN)
- **DRW Vx, Vy, N** – Draw sprite at (Vx, Vy) with height N (0xDXYN)
- **SKP Vx** – Skip if key in Vx is pressed (0xEX9E)
- **SKNP Vx** – Skip if key in Vx is not pressed (0xEXA1)
- **LD_VX_DT Vx** – Vx = delay timer (0xFX07)
- **LD_VX_K Vx** – Wait for key press, store in Vx (0xFX0A)
- **LD_DT_VX Vx** – delay timer = Vx (0xFX15)
- **LD_ST_VX Vx** – sound timer = Vx (0xFX18)
- **ADD_I_VX Vx** – I += Vx (0xFX1E)
- **LD_F Vx** – Set I to sprite address for digit in Vx (0xFX29)
- **LD_B Vx** – Store BCD representation of Vx (0xFX33)
- **LD_I_TO_V Vx** – Store registers V0 through Vx in memory starting at I (0xFX55)
- **LD_V_TO_I Vx** – Read registers V0 through Vx from memory starting at I (0xFX65)

### 2. Labels

Labels are used to mark positions in the code for jumps and calls.
They are defined as follows:

```
my_label:
```

You can reference them later with instructions like JP my_label or CALL my_label

### 3. Comments

Comments start with a #.
Anything after # on the same line is ignored by the assembler.

```
LD V0, 5   # Load 5 into V0
```

(Note: comments are still experimental and may not be fully supported yet.)