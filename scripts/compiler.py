from enum import Enum
from typing import Dict
import sys
import re

class Arguments:
    args: list[str] = []
    program_path: str = ""
    output_path: str = ""
    skip_parsing: bool = False

    def __init__(self):
        self._get_arguments()

    def _get_arguments(self) -> None:
        self.args = sys.argv[1:]
        self.program_path = self.args[0]
        if not self.program_path.endswith(".c8s"):
            raise Exception("[FileError] Specified file has not .c8s extension")

        self.output_path, _ = self._get_optional_argument("outpath", self._get_default_target_path())
        _, self.skip_parsing = self._get_optional_argument("skip-parsing")

    def _get_optional_argument(self, flag: str, default_value: str = "") -> tuple[str, bool]:
        for index, arg in enumerate(self.args):
            if arg == f"--{flag}":
                if index == len(self.args) - 1 or self.args[index + 1].startswith("--"):
                    return (default_value, True)
                return (self.args[index + 1], True)
        return (default_value, False)

    def _get_default_target_path(self) -> None:
        return re.sub(r"\.[^./\\]+$", ".ch8", self.program_path)



class Lexer:
    src_text: str
    tokens: list[str] = []

    _is_comment = False

    def __init__(self, program_text: str):
        self.src_text = program_text
        self._scan()

    def _scan(self) -> None:
        current_token = ""
        for char in self.src_text:
            if self._is_comment and char != "\n":
                continue
            else:
                self._is_comment = False

            match char:
                case "," | "\n":
                    if current_token != "":
                        self.tokens.append(current_token)
                        current_token = ""
                    self.tokens.append(char)
                    continue
                case " ":
                    if current_token != "":
                        self.tokens.append(current_token)
                        current_token = ""
                    continue
                case "#":
                    self._is_comment = True
                    if current_token != "":
                        self.tokens.append(current_token)
                        current_token = ""
                    continue
            current_token += char

class ParamType(Enum):
    N = 0,
    NN = 1,
    NNN = 2,
    VX = 3,
    VY = 4

class SyntaxNode:
    code: int
    param_types: list[ParamType]
    params: list[int] = []

    def __init__(self, code: int, param_types: list[ParamType]):
        self.code = code
        self.param_types = param_types

TokensMap: Dict[str, SyntaxNode] = {
    "WAIT": SyntaxNode(0x0FFF, []),
    "CLS": SyntaxNode(0x00E0, []),
    "RET": SyntaxNode(0x00EE, []),
    "JP": SyntaxNode(0x1000, [ParamType.NNN]),
    "CALL": SyntaxNode(0x2000, [ParamType.NNN]),
    "SE": SyntaxNode(0x3000, [ParamType.VX, ParamType.NN]),
    "SNE": SyntaxNode(0x4000, [ParamType.VX, ParamType.NN]),
    "SE_REG": SyntaxNode(0x5000, [ParamType.VX, ParamType.VY]),
    "LD": SyntaxNode(0x6000, [ParamType.VX, ParamType.NN]),
    "ADD": SyntaxNode(0x7000, [ParamType.VX, ParamType.NN]),
    "LD_REG": SyntaxNode(0x8000, [ParamType.VX, ParamType.VY]),
    "OR": SyntaxNode(0x8001, [ParamType.VX, ParamType.VY]),
    "AND": SyntaxNode(0x8002, [ParamType.VX, ParamType.VY]),
    "XOR": SyntaxNode(0x8003, [ParamType.VX, ParamType.VY]),
    "ADD_REG": SyntaxNode(0x8004, [ParamType.VX, ParamType.VY]),
    "SUB": SyntaxNode(0x8005, [ParamType.VX, ParamType.VY]),
    "SHR": SyntaxNode(0x8006, [ParamType.VX]),
    "SUBN": SyntaxNode(0x8007, [ParamType.VX, ParamType.VY]),
    "SHL": SyntaxNode(0x800E, [ParamType.VX]),
    "SNE_REG": SyntaxNode(0x9000, [ParamType.VX, ParamType.VY]),
    "LD_I": SyntaxNode(0xA000, [ParamType.NNN]),
    "JP_V0": SyntaxNode(0xB000, [ParamType.NNN]),
    "RND": SyntaxNode(0xC000, [ParamType.VX, ParamType.NN]),
    "DRW": SyntaxNode(0xD000, [ParamType.VX, ParamType.VY, ParamType.N]),
    "SKP": SyntaxNode(0xE09E, [ParamType.VX]),
    "SKNP": SyntaxNode(0xE0A1, [ParamType.VX]),
    "LD_VX_DT": SyntaxNode(0xF007, [ParamType.VX]),
    "LD_VX_K": SyntaxNode(0xF00A, [ParamType.VX]),
    "LD_DT_VX": SyntaxNode(0xF015, [ParamType.VX]),
    "LD_ST_VX": SyntaxNode(0xF018, [ParamType.VX]),
    "ADD_I_VX": SyntaxNode(0xF01E, [ParamType.VX]),
    "LD_F": SyntaxNode(0xF029, [ParamType.VX]),
    "LD_B": SyntaxNode(0xF033, [ParamType.VX]),
    "LD_I_TO_V": SyntaxNode(0xF055, [ParamType.VX]),
    "LD_V_TO_I": SyntaxNode(0xF065, [ParamType.VX]),
}

class Parser:
    tokens: list[str]
    nodes: list[SyntaxNode] = []
    labels: Dict[str, int] = {}

    _current_action_token: str = ""
    _current_line: int = 0

    _current_parameter_index: int = 0

    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self._create_nodes()

    def _create_nodes(self) -> None:
        lines_with_labels = self._get_lines()
        lines = self._register_and_remove_labels(lines_with_labels)
        for index, line in enumerate(lines):
            self._current_action_token = line[0]
            self._current_line = index
            node = self._get_node(line)
            node.params = self._get_params(line[1:], node.param_types)
            self.nodes.append(node)

    def _get_lines(self) -> list[list[str]]:
        lines: list[list[str]] = []
        current_line: list[str] = []
        for token in self.tokens:
            if token == "\n":
                lines.append(current_line.copy())
                current_line.clear()
                continue
            if token != ",":
                current_line.append(token)
        return lines

    def _get_node(self, line: list[str]) -> SyntaxNode:
        action = TokensMap.get(line[0])
        if not action:
            raise Exception(f"[ParseError] Unknown action '{self._current_action_token}' (line={self._current_line})")
        return SyntaxNode(action.code, action.param_types)

    def _get_params(self, str_params: str, param_types: list[ParamType]) -> list[int]:
        if len(param_types) > len(str_params):
                raise Exception(f"[ParseError] Missing param (action={self._current_action_token}, line={self._current_line})")

        parsed_parameters: list[int] = []

        for index, param_type in enumerate(param_types):
            self._current_parameter_index = index

            match param_type:
                case ParamType.VX | ParamType.VY:
                    parsed_parameters.append(self._get_Vx_param(str_params[index]))
                case ParamType.N:
                    parsed_parameters.append(self._get_N_param(str_params[index]))
                case ParamType.NN:
                    parsed_parameters.append(self._get_NN_param(str_params[index]))
                case ParamType.NNN:
                    parsed_parameters.append(self._get_NNN_param(str_params[index]))
        return parsed_parameters

    def _get_Vx_param(self, str_param: str) -> int:
        if not str_param.startswith("v"):
            raise Exception(f"[ParseError] Param#{self._current_parameter_index} expected Vx, got '{str_param}' (action={self._current_action_token}, line={self._current_line})")
        str_value = str_param[1:]
        if not str_value.isdigit():
            raise Exception(f"[ParseError] Invalid Vx at param#{self._current_parameter_index} (action={self._current_action_token}, line={self._current_line})")
        int_value = int(str_value)
        if int_value > 15 or int_value < 0:
            raise Exception(f"[ParseError] Overrange Vx at param#{self._current_parameter_index}, (action={self._current_action_token}, line={self._current_line})")
        return int_value

    def _get_N_param(self, str_param: str, max_value: int = 15, n_name: str = "N") -> int:
        handled_str_param = self._handle_binary(self._handle_hexa(str_param))
        if not handled_str_param.isdigit():
            raise Exception(f"[ParseError] Invalid number at param#{self._current_parameter_index} (action={self._current_action_token}, line={self._current_line})")
        int_value = int(handled_str_param)
        if int_value < 0 or int_value > max_value:
            raise Exception(f"[ParseError] Overflowing {n_name} at param#{self._current_parameter_index}, (action={self._current_action_token}, line={self._current_line})")
        return int_value

    def _get_NN_param(self, str_param: str) -> int:
        return self._get_N_param(str_param, 255, "NN")

    def _get_NNN_param(self, str_param: str) -> int:
        return self._get_N_param(self._handle_label(self._current_action_token, str_param), 4095, "NNN")

    def _is_label(self, token: str) -> bool:
        return len(token) > 1 and token[-1] == ":"

    def _add_label(self, label: str, line: int) -> None:
        self.labels[label] = 512 + (line + 1) * 2

    def _handle_label(self, token: str, str_param: str) -> str:
        accepted_tokens = ["JP", "CALL"]
        if token in accepted_tokens and not str_param.isdigit():
            registered_label = self.labels.get(str_param)
            if not registered_label:
                raise Exception(f"[ParseError] Non-existent label {str_param} (action={self._current_action_token}, line={self._current_line})")
            return str(registered_label)
        return str_param

    def _handle_binary(self, str_param: str) -> str:
        if str_param.startswith("0b"):
            param_without_0b = str_param[2:]
            if not all(c in "01" for c in param_without_0b):
                raise Exception(f"[ParseError] Invalid binary number '{str_param}' (action={self._current_action_token}, line={self._current_line})")
            return str(int(param_without_0b, 2))
        return str_param

    def _handle_hexa(self, str_param: str) -> str:
        if str_param.startswith("0x"):
            param_without_0x = str_param[2:]
            if not all(c in "0123456789ABCDEF" for c in param_without_0x):
                raise Exception(f"[ParseError] Invalid hexadecimal number '{str_param}' (action={self._current_action_token}, line={self._current_line})")
            return str(int(param_without_0x, 16))
        return str_param

    def _register_and_remove_labels(self, lines: list[list[str]]) -> list[list[str]]:
        lines_without_labels: list[list[str]] = []
        for index, line in enumerate(lines):
            if self._is_label(line[0]):
                label_name = line[0][:-1]
                if self.labels.get(label_name):
                    raise Exception(f"[ParseError] Reused label {label_name}, (line={index})")
                self._add_label(label_name, len(lines_without_labels) - 1)
            else:
                lines_without_labels.append(line)
        return lines_without_labels


class Generator:
    _nodes: list[SyntaxNode] = []

    def __init__(self, nodes: list[SyntaxNode]):
        self._nodes = nodes

    def _create_opcode(self, node: SyntaxNode) -> int:
        opcode = node.code
        for ptype, value in zip(node.param_types, node.params):
            match ptype:
                case ParamType.VX:
                    opcode |= (value & 0xF) << 8
                case ParamType.VY:
                    opcode |= (value & 0xF) << 4
                case ParamType.N:
                    opcode |= value & 0xF
                case ParamType.NN:
                    opcode |= value & 0xFF
                case ParamType.NNN:
                    opcode |= value & 0xFFF
        return opcode

    def create_rom(self, output_path: str) -> None:
        opcodes: list[int] = []
        for node in self._nodes:
            opcodes.append(self._create_opcode(node))

        with open(output_path, "wb") as f:
            for opcode in opcodes:
                f.write(opcode.to_bytes(2, byteorder="big"))
            print(f"ROM generated at {output_path}")

if __name__ == "__main__":
    arguments = Arguments()
    program = ""

    with open(arguments.program_path, "r") as f:
        program = f.read()

    lexer = Lexer(program)
    if not arguments.skip_parsing:
        parser = Parser(lexer.tokens)
        generator = Generator(parser.nodes)
        generator.create_rom(arguments.output_path)