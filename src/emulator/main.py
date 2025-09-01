from dataclasses import dataclass
from typing import NewType, Callable
import pygame
import random
import math
import time
import sys

Uint8 = NewType("Uint8", int)
Uint16 = NewType("Uint16", int)

Byte4Nibble = NewType("Byte4Nibble", int)
Byte8Nibble = NewType("Byte8Nibble", int)
Byte12Nibble = NewType("Byte12Nibble", int)

Registers_VLength = 0x10
Registers_StackLength = 0x10
Registers_FirstProgramCounterAdress = 0x200

class Registers:
    v: list[Uint8] = [0] * Registers_VLength
    i: Uint16 = 0
    pc: Uint16 = Registers_FirstProgramCounterAdress
    sp: Uint8 = -1
    dt: Uint8 = 0
    st: Uint8 = 0
    stack: list[Uint16] = [0] * Registers_StackLength

Memory_DataSize = 0xFFF
Memory_FontsetData = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,
    0x20, 0x60, 0x20, 0x20, 0x70,
    0xF0, 0x10, 0xF0, 0x80, 0xF0,
    0xF0, 0x10, 0xF0, 0x10, 0xF0,
    0x90, 0x90, 0xF0, 0x10, 0x10,
    0xF0, 0x80, 0xF0, 0x10, 0xF0,
    0xF0, 0x80, 0xF0, 0x90, 0xF0,
    0xF0, 0x10, 0x20, 0x40, 0x40,
    0xF0, 0x90, 0xF0, 0x90, 0xF0,
    0xF0, 0x90, 0xF0, 0x10, 0xF0,
    0xF0, 0x90, 0xF0, 0x90, 0x90,
    0xE0, 0x90, 0xE0, 0x90, 0xE0,
    0xF0, 0x80, 0x80, 0x80, 0xF0,
    0xE0, 0x90, 0x90, 0x90, 0xE0,
    0xF0, 0x80, 0xF0, 0x80, 0xF0,
    0xF0, 0x80, 0xF0, 0x80, 0x80,
]
Memory_FontSetFirstAddress = 0x0

class Memory:
    _data: list[Uint8] = [0] * Memory_DataSize

    def __init__(self):
        self._load_fontset()

    def _is_valide_adress(self, addr: Uint16) -> bool:
        is_overflowing = addr > Memory_DataSize or addr < 0
        if is_overflowing:
            print(f"[Memory Error]: {hex(addr)} is overflowing memory.")
        return not is_overflowing

    def _load_fontset(self) -> None:
        self.set_many(Memory_FontsetData, Memory_FontSetFirstAddress)

    def set(self, value: Uint8, addr: Uint16) -> None:
        if self._is_valide_adress(addr):
            self._data[addr] = value

    def get(self, addr: Uint16) -> Uint8:
        if self._is_valide_adress(addr):
            return self._data[addr]
        else:
            return 0

    def set_many(self, values: list[Uint8], addr: Uint16) -> None:
        last_addr = addr + len(values)
        if self._is_valide_adress(addr) and self._is_valide_adress(last_addr):
            self._data[addr:last_addr] = values

Display_Black = False
Display_White = True
Display_PixelOnWidth = 64
Display_PixelOnHeight = 32
Display_PixelDim = 16
Display_Width = Display_PixelOnWidth * Display_PixelDim
Display_Height = Display_PixelOnHeight * Display_PixelDim
Display_BlackColor = "#000000"
Display_WhiteColor = "#ffffff"
Display_Icon = "assets/icon/C8-Logo-x48.png"
Display_Caption = "Chip8 Emu"

class Display:
    _cells: list[list[bool]] = [[Display_Black] * Display_PixelOnHeight] * Display_PixelOnWidth 

    screen: pygame.Surface

    def __init__(self):
        icon = pygame.image.load(Display_Icon)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(Display_Caption)
        self.screen = pygame.display.set_mode((Display_Width, Display_Height))

    def _each_cells(self, callback: Callable[[bool, int, int], None]) -> None:
        for x in range(Display_PixelOnWidth - 1):
            for y in range(Display_PixelOnHeight - 1):
                callback(self._cells[x][y], x, y)

    def _fill_cell_if_white(self, x: int, y: int) -> None:
        if self._cells[x][y] == Display_White:
            rect = pygame.Rect(
                x * Display_PixelDim,
                y * Display_PixelDim,
                Display_PixelDim,
                Display_PixelDim
            )
            self.screen.fill(Display_WhiteColor, rect)

    def _is_pixel_on_display(self, x: int, y: int) -> bool:
        _is_on_display = x >= 0 and x < Display_PixelOnWidth and y >= 0 and y < Display_PixelOnHeight
        if not _is_on_display:
            print(f"[Display Error]: x: {x}, y: {y} are not valid display coordinates.")
        return _is_on_display

    def update(self) -> None:
        self.screen.fill(Display_Black)
        self._each_cells(lambda _, x, y: self._fill_cell_if_white(x, y))

    def clear(self) -> None:
        def cb(_, x, y):
            self._cells[x][y] = Display_Black
        self._each_cells(cb)

    def get_pixel(self, x: int, y: int) -> bool:
        if self._is_pixel_on_display(x, y):
            return self._cells[x][y]
        return Display_Black

    def set_pixel(self, x: int, y: int, value: bool) -> None:
        if self._is_pixel_on_display(x, y):
            self._cells[x][y] = value

Inputs_KeysPressedlength = 0x10
Inputs_KeyPressedCorrespondence = [
    pygame.K_KP0, pygame.K_KP1, pygame.K_KP2,
    pygame.K_KP3, pygame.K_KP4, pygame.K_KP5,
    pygame.K_KP6, pygame.K_KP7, pygame.K_KP8,
    pygame.K_KP9, pygame.K_q, pygame.K_w,
    pygame.K_e, pygame.K_r, pygame.K_t,
    pygame.K_y,
]

class Inputs:
    _keys_pressed: list[bool] = [False] * Inputs_KeysPressedlength
    _free_keys_pressed: list[int] = []
    _free_keys_just_pressed: list[int] = []
    _can_running = True

    def _get_corresponding_key_index(self, event_type: pygame.event.EventType) -> int:
        try:
            return Inputs_KeyPressedCorrespondence.index(event_type)
        except:
            return -1

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        key = self._get_corresponding_key_index(event.key)
        if key != -1:
            self._keys_pressed[key] = True
        else:
            self._set_free_key_pressed(event)

    def _handle_keyup(self, event: pygame.event.Event) -> None:
        key = self._get_corresponding_key_index(event.key)
        if key != -1:
            self._keys_pressed[key] = False
        else:
            self._set_free_key_released(event)

    def _is_key_in_range(self, key: int) -> bool:
        _is_in_range = key >= 0 and key < Inputs_KeysPressedlength
        if not _is_in_range:
            print(f"[Inputs Error]: {hex(key)} is not in the keys range.")
        return _is_in_range

    def _set_free_key_pressed(self, event: pygame.event.Event) -> None:
        if event.key not in Inputs_KeyPressedCorrespondence:
            if event.key not in self._free_keys_pressed:
                self._free_keys_just_pressed.append(event.key)
                self._free_keys_pressed.append(event.key)

    def _set_free_key_released(self, event: pygame.event.Event) -> None:
        if event.key not in Inputs_KeyPressedCorrespondence:
            if event.key in self._free_keys_pressed:
                self._free_keys_pressed.remove(event.key)


    def update(self) -> None:
        self._free_keys_just_pressed.clear()
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self._can_running = False
                case pygame.KEYDOWN:
                    self._handle_keydown(event)
                case pygame.KEYUP:
                    self._handle_keyup(event)

    def should_quit(self) -> bool:
        return not self._can_running

    def is_key_pressed(self, key: int) -> bool:
        if self._is_key_in_range(key):
            return self._keys_pressed[key]

    def get_key_pressed(self) -> int | None:
        for index, key in enumerate(self._keys_pressed):
            if key:
                return index
        return None

    def is_free_key_pressed(self, key: int) -> bool:
        return key in self._free_keys_pressed

    def is_free_key_just_pressed(self, key: int) -> bool:
        return key in self._free_keys_just_pressed

    def get_free_key_pressed(self) -> int | None:
        if self._free_keys_pressed:
            return self._free_keys_pressed[-1]
        else:
            return None

    def get_all_keys_pressed(self) -> list[bool]:
        return self._keys_pressed.copy()


@dataclass
class OpcodePayload:
    registers: Registers
    memory: Memory
    display: Display
    inputs: Inputs

@dataclass
class OpcodeAction:
    code: Byte4Nibble
    x: Byte4Nibble
    y: Byte4Nibble
    n: Byte4Nibble
    nn: Byte8Nibble
    nnn: Byte12Nibble

@dataclass
class OpcodeTableEntry:
    mask: Uint16
    id: Uint16
    callback: Callable[[OpcodePayload, OpcodeAction], None]

class OpcodeTable:
    _entries: list[OpcodeTableEntry] = []

    def set(self, mask: Uint16, id: Uint16, callback: Callable[[OpcodePayload, OpcodeAction], None]) -> None:
        self._entries.append(OpcodeTableEntry(mask, id, callback))

    def get(self, opcode: Uint16) -> OpcodeTableEntry | None:
        for entry in self._entries:
            if (opcode & entry.mask) == entry.id:
                return entry
        print(f"[Opcode Error]: {hex(opcode)} opcode is not supported.")
        return None

def Opcode_0x0FFF(p: OpcodePayload, a: OpcodeAction) -> None:
    pass

def Opcode_0x00E0(p: OpcodePayload, _: OpcodeAction) -> None:
    p.display.clear()

def Opcode_0x00EE(p: OpcodePayload, _: OpcodeAction) -> None:
    if p.registers.sp > 0:
        p.registers.sp -= 1
        p.registers.pc = p.registers.stack[p.registers.sp]
    else:
        p.registers.pc = p.registers.stack[0]


def Opcode_0x1000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.pc = a.nnn

def Opcode_0x2000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.sp += 1
    p.registers.stack[p.registers.sp] = p.registers.pc
    p.registers.pc = a.nnn

def Opcode_0x3000(p: OpcodePayload, a: OpcodeAction) -> None:
    if p.registers.v[a.x] == a.nn:
        p.registers.pc += 2

def Opcode_0x4000(p: OpcodePayload, a: OpcodeAction) -> None:
    if p.registers.v[a.x] != a.nn:
        p.registers.pc += 2

def Opcode_0x5000(p: OpcodePayload, a: OpcodeAction) -> None:
    if p.registers.v[a.x] == p.registers.v[a.y]:
        p.registers.pc += 2

def Opcode_0x6000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = a.nn

def Opcode_0x7000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = (p.registers.v[a.x] + a.nn) & 0xFF

def Opcode_0x8000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = p.registers.v[a.y]

def Opcode_0x8001(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] |= p.registers.v[a.y]

def Opcode_0x8002(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] &= p.registers.v[a.y]

def Opcode_0x8003(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] ^= p.registers.v[a.y]

def Opcode_0x8004(p: OpcodePayload, a: OpcodeAction) -> None:
    result = p.registers.v[a.x] + p.registers.v[a.y]
    p.registers.v[0xF] = 1 if result > 255 else 0
    p.registers.v[a.x] = result & 0xFF

def Opcode_0x8005(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[0xF] = 1 if p.registers.v[a.x] > p.registers.v[a.y] else 0
    p.registers.v[a.x] -= p.registers.v[a.y]

def Opcode_0x8006(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = p.registers.v[a.y]
    p.registers.v[0xF] = p.registers.v[a.x] & 1
    p.registers.v[a.x] >>= 1

def Opcode_0x8007(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[0xF] = 1 if p.registers.v[a.y] > p.registers.v[a.x] else 0
    p.registers.v[a.x] = p.registers.v[a.y] - p.registers.v[a.x]

def Opcode_0x800E(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = p.registers.v[a.y]
    p.registers.v[0xF] = (p.registers.v[a.x] & 0x80) >> 7
    p.registers.v[a.x] <<=1

def Opcode_0x9000(p: OpcodePayload, a: OpcodeAction) -> None:
    if p.registers.v[a.x] != p.registers.v[a.y]:
        p.registers.pc += 2

def Opcode_0xA000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.i = a.nnn

def Opcode_0xB000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.pc = a.nnn + p.registers.v[0]

def Opcode_0xC000(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = random.randint(0, 255) & a.nn

def Opcode_0xD000(p: OpcodePayload, a: OpcodeAction) -> None:
    pixel_collision = False
    p.registers.v[0xF] = 0
    for y in range(0, a.n):
        sprite_raw = p.memory.get(p.registers.i + y)
        for x in range(0, 8):
            px = (sprite_raw >> (7 - x)) & 1
            x_pos = (p.registers.v[a.x] + x) % Display_PixelOnWidth
            y_pos = (p.registers.v[a.y] + y) % Display_PixelOnHeight
            current_px = int(p.display.get_pixel(x_pos, y_pos))
            new_px = current_px ^ px
            if current_px == 1 and new_px == 0:
                pixel_collision = True
            p.display.set_pixel(x_pos, y_pos, bool(new_px))
    p.registers.v[0xF] = int(pixel_collision)

def Opcode_0xE09E(p: OpcodePayload, a: OpcodeAction) -> None:
    if p.inputs.is_key_pressed(p.registers.v[a.x] & 0x0F):
        p.registers.pc += 2

def Opcode_0xE0A1(p: OpcodePayload, a: OpcodeAction) -> None:
    if not p.inputs.is_key_pressed(p.registers.v[a.x] & 0x0F):
        p.registers.pc += 2

def Opcode_0xF007(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.v[a.x] = p.registers.dt

def Opcode_0xF00A(p: OpcodePayload, a: OpcodeAction) -> None:
    pressed_key = p.inputs.get_key_pressed()
    if pressed_key == None:
        p.registers.pc -= 2
        return
    p.registers.v[a.x] = pressed_key

def Opcode_0xF015(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.dt = p.registers.v[a.x]

def Opcode_0xF018(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.st = p.registers.v[a.x]

def Opcode_0xF01E(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.i += p.registers.v[a.x]

def Opcode_0xF029(p: OpcodePayload, a: OpcodeAction) -> None:
    p.registers.i = (p.registers.v[a.x] & 0x0F) * 5

def Opcode_0xF033(p: OpcodePayload, a: OpcodeAction) -> None:
    value = p.registers.v[a.x]
    p.memory.set_many([
        math.floor(value / 100),
        math.floor((value % 100) / 10),
        value % 10
    ], p.registers.i)

def Opcode_0xF055(p: OpcodePayload, a: OpcodeAction) -> None:
    for i in range(0, a.x + 1):
        p.memory.set(p.registers.v[i], p.registers.i + i)

def Opcode_0xF065(p: OpcodePayload, a: OpcodeAction) -> None:
    for i in range(0, a.x + 1):
        p.registers.v[i] = p.memory.get(p.registers.i + i)

CPU_CycleDuration = 1 / 60
CPU_OpcodeHistoryMaxLength = 10
CPU_OmitIncrementProgramCounterOpcodes = [
    0x00EE, 0x1000, 0x2000, 0xB000
]

class CPU:
    _opcode_table = OpcodeTable()
    registers = Registers()

    _memory: Memory
    _display: Display
    _inputs: Inputs

    _last_timer_update: float
    _last_cycle_time: float

    _frequency: int = 0
    _cycles_executed: int = 0
    _last_frequency_time: float = 0.0

    _opcodes_history: list[int] = []

    def __init__(self, memory: Memory, display: Display, inputs: Inputs):
        self._memory = memory
        self._display = display
        self._inputs = inputs
        self._init_opcode_table()
        self._last_timer_update = time.perf_counter()
        self._last_cycle_time = time.perf_counter()

    def _init_opcode_table(self) -> None:
        self._opcode_table.set(0xF000, 0x0FFF, Opcode_0x0FFF)
        self._opcode_table.set(0xFFFF, 0x00E0, Opcode_0x00E0)
        self._opcode_table.set(0xFFFF, 0x00EE, Opcode_0x00EE)
        self._opcode_table.set(0xF000, 0x1000, Opcode_0x1000)
        self._opcode_table.set(0xF000, 0x2000, Opcode_0x2000)
        self._opcode_table.set(0xF000, 0x3000, Opcode_0x3000)
        self._opcode_table.set(0xF000, 0x4000, Opcode_0x4000)
        self._opcode_table.set(0xF000, 0x5000, Opcode_0x5000)
        self._opcode_table.set(0xF000, 0x6000, Opcode_0x6000)
        self._opcode_table.set(0xF000, 0x7000, Opcode_0x7000)
        self._opcode_table.set(0xF00F, 0x8000, Opcode_0x8000)
        self._opcode_table.set(0xF00F, 0x8001, Opcode_0x8001)
        self._opcode_table.set(0xF00F, 0x8002, Opcode_0x8002)
        self._opcode_table.set(0xF00F, 0x8003, Opcode_0x8003)
        self._opcode_table.set(0xF00F, 0x8004, Opcode_0x8004)
        self._opcode_table.set(0xF00F, 0x8005, Opcode_0x8005)
        self._opcode_table.set(0xF00F, 0x8006, Opcode_0x8006)
        self._opcode_table.set(0xF00F, 0x8007, Opcode_0x8007)
        self._opcode_table.set(0xF00F, 0x800E, Opcode_0x800E)
        self._opcode_table.set(0xF000, 0x9000, Opcode_0x9000)
        self._opcode_table.set(0xF000, 0xA000, Opcode_0xA000)
        self._opcode_table.set(0xF000, 0xB000, Opcode_0xB000)
        self._opcode_table.set(0xF000, 0xC000, Opcode_0xC000)
        self._opcode_table.set(0xF000, 0xD000, Opcode_0xD000)
        self._opcode_table.set(0xF0FF, 0xE09E, Opcode_0xE09E)
        self._opcode_table.set(0xF0FF, 0xE0A1, Opcode_0xE0A1)
        self._opcode_table.set(0xF0FF, 0xF007, Opcode_0xF007)
        self._opcode_table.set(0xF0FF, 0xF00A, Opcode_0xF00A)
        self._opcode_table.set(0xF0FF, 0xF015, Opcode_0xF015)
        self._opcode_table.set(0xF0FF, 0xF018, Opcode_0xF018)
        self._opcode_table.set(0xF0FF, 0xF01E, Opcode_0xF01E)
        self._opcode_table.set(0xF0FF, 0xF029, Opcode_0xF029)
        self._opcode_table.set(0xF0FF, 0xF033, Opcode_0xF033)
        self._opcode_table.set(0xF0FF, 0xF055, Opcode_0xF055)
        self._opcode_table.set(0xF0FF, 0xF065, Opcode_0xF065)

    def _read_program_line(self) -> Uint16:
        return (self._memory.get(self.registers.pc) << 8) | self._memory.get(self.registers.pc + 1)

    def _decrypt_opcode(self, opcode: Uint16) -> OpcodeAction:
        return OpcodeAction(
            code=(opcode & 0xF000) >> 12,
            x=(opcode & 0x0F00) >> 8,
            y=(opcode & 0x00F0) >> 4,
            n=opcode & 0x000F,
            nn=opcode & 0x00FF,
            nnn=opcode & 0x0FFF
        )

    def _execute_action(self) -> None:
        opcode = self._read_program_line()
        action = self._decrypt_opcode(opcode)
        entry = self._opcode_table.get(opcode)

        if opcode and entry:
            entry.callback(OpcodePayload(
                self.registers,
                self._memory,
                self._display,
                self._inputs
            ), action)

        self._add_opcode_in_history(opcode)

        if (opcode & 0xF000) not in CPU_OmitIncrementProgramCounterOpcodes:
            self.registers.pc += 2

    def _update_time(self) -> None:
        now = time.perf_counter()
        if now - self._last_timer_update >= 1 / 60:
            if self.registers.dt > 0:
                self.registers.dt -= 1
            if self.registers.st > 0:
                self.registers.st -= 1
                if self.registers.st == 0:
                    pass
            self._last_timer_update = now

    def _update_frequency(self, now: float) -> None:
        if now - self._last_frequency_time >= 1.0:
            self._frequency = self._cycles_executed / (now - self._last_frequency_time)
            self._cycles_executed = 0
            self._last_frequency_time = now

    def _add_opcode_in_history(self, opcode: int) -> None:
        if len(self._opcodes_history) >= CPU_OpcodeHistoryMaxLength:
            self._opcodes_history = self._opcodes_history[1:]
        self._opcodes_history.append(opcode)

    def tick(self) -> None:
        now = time.perf_counter()
        elapsed = now - self._last_cycle_time

        if elapsed >= CPU_CycleDuration:
            self._execute_action()
            self._update_time()
            self._last_cycle_time = now
            self._cycles_executed += 1
        self._update_frequency(now)

    def get_frequency(self) -> int:
        return self._frequency

    def get_opcodes_history(self) -> list[int]:
        return self._opcodes_history

Debugger_FontSize = 20
Debugger_Color = "green"
Debugger_BackgroundColor = "#000000"

class Debugger:
    _memory: Memory
    _display: Display
    _inputs: Inputs
    _registers: Registers
    _cpu: CPU
    _font: pygame.font.Font

    _displayed = False

    def __init__(
        self,
        memory: Memory,
        display: Display,
        inputs: Inputs,
        cpu: CPU
    ):
        self._memory = memory
        self._display = display
        self._inputs = inputs
        self._registers = cpu.registers
        self._cpu = cpu
        self._font = pygame.font.SysFont(None, Debugger_FontSize)

    def _draw_text(self, text: str, top: int) -> None:
        text_surface = self._font.render(
            text,
            True,
            pygame.Color(Debugger_Color),
            pygame.Color(Debugger_BackgroundColor)
        )
        text_rect = text_surface.get_rect(topleft=(5,top))
        self._display.screen.blit(text_surface, text_rect)

    def _draw_v_registers_text(self) -> None:
        registers_text = "[V]: " + ", ".join(str(val) for val in self._registers.v) + ";"
        self._draw_text(registers_text, 5)

    def _draw_special_registers_text(self) -> None:
        registers_text = f"[I]: {self._registers.i}; PC: {self._registers.pc}; SP: {self._registers.sp}; DT: {self._registers.dt}; ST: {self._registers.st};"
        self._draw_text(registers_text, 20)

    def _draw_stack_register_text(self) -> None:
        registers_text = "[Stack]: " + ", ".join(str(val) for val in self._registers.stack) + ";"
        self._draw_text(registers_text, 35)

    def _draw_cpu_frequency_text(self) -> None:
        frequency_text = f"[Frequency]: {round(self._cpu.get_frequency(), 3)}Hz"
        self._draw_text(frequency_text, 50)

    def _draw_last_opcodes(self) -> None:
        opcodes_text = "[Opcodes history]: " + ", ".join(hex(val) for val in self._cpu.get_opcodes_history()) + ";"
        self._draw_text(opcodes_text, 65)

    def _draw_keys_pressed(self) -> None:
        keys_pressed_text = "[Keys]: " + ", ".join(f"({hex(index)})->{1 if val else 0}" for index, val in enumerate(self._inputs.get_all_keys_pressed())) + ";"
        self._draw_text(keys_pressed_text, 80)

    def _toggle_displayed(self) -> None:
        if self._inputs.is_free_key_just_pressed(pygame.K_LSHIFT):
            self._displayed = not self._displayed

    def update(self) -> None:
        if self._displayed:
            self._draw_v_registers_text()
            self._draw_special_registers_text()
            self._draw_stack_register_text()
            self._draw_cpu_frequency_text()
            self._draw_last_opcodes()
            self._draw_keys_pressed()
        self._toggle_displayed()

class App:
    _memory = Memory()
    _display = Display()
    _inputs = Inputs()

    _cpu: CPU
    _debugger: Debugger
    _last_timer_update: float

    def __init__(self):
        self._cpu = CPU(self._memory, self._display, self._inputs)
        self._debugger = Debugger(self._memory, self._display, self._inputs, self._cpu)
        self._last_timer_update = time.perf_counter()

    def _cycle(self) -> None:
        self._display.update()
        self._inputs.update()
        self._cpu.tick()
        self._debugger.update()
        pygame.display.flip()

    def _load_rom(self, path: str) -> None:
        try:
            with open(path, "rb") as f:
                self._memory.set_many(f.read(), Registers_FirstProgramCounterAdress)
        except Exception as e:
            print(f"Failed to load rom \"{path}\": {str(e)}")

    def start(self, rom_path: str) -> None:
        self._load_rom(rom_path)
        while not self._inputs.should_quit():
            self._cycle()

pygame.init()

if __name__ == "__main__":
    app = App()
    app.start(sys.argv[1])
