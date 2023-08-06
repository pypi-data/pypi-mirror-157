"""A C++ port of the NEO3 Virtual Machine"""
from __future__ import annotations
from pybiginteger import BigInteger
import neo3vm
import typing

__all__ = [
    "ApplicationEngineCpp",
    "ArrayStackItem",
    "BadScriptException",
    "BooleanStackItem",
    "BufferStackItem",
    "ByteStringStackItem",
    "CompoundType",
    "EvaluationStack",
    "ExceptionHandlingContext",
    "ExceptionHandlingState",
    "ExecutionContext",
    "ExecutionEngine",
    "Instruction",
    "IntegerStackItem",
    "InteropStackItem",
    "MapStackItem",
    "Neo3vmException",
    "NullStackItem",
    "OpCode",
    "PointerStackItem",
    "PrimitiveType",
    "ReferenceCounter",
    "Script",
    "ScriptBuilder",
    "Slot",
    "StackItem",
    "StackItemType",
    "StructStackItem",
    "VMState"
]


class ExecutionEngine():
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, reference_counter: ReferenceCounter) -> None: ...
    def _execute_next(self) -> None: ...
    def context_unloaded(self, arg0: ExecutionContext) -> None: ...
    def execute(self) -> VMState: ...
    def load_cloned_context(self, arg0: int) -> None: ...
    def load_context(self, arg0: ExecutionContext) -> None: ...
    def load_script(self, script: Script, rvcount: int = -1, initial_position: int = 0) -> ExecutionContext: 
        """
        Load script into engine
        """
    def load_script_override(self, arg0: Script, arg1: bytes, arg2: int, arg3: int) -> ExecutionContext: ...
    def on_syscall(self, method_id: int) -> None: ...
    def pop(self) -> StackItem: 
        """
        Pop the top item from the evaluation stack of the current context.
        """
    def pop_bool(self) -> bool: ...
    def pop_bytes(self) -> bytes: ...
    def pop_int(self) -> BigInteger: ...
    def post_execute_instruction(self, arg0: Instruction) -> None: ...
    def pre_execute_instruction(self) -> None: ...
    def push(self, stack_item: StackItem) -> None: 
        """
        Push an item onto the evaluation stack of the current context.
        """
    def throw(self, exception_stack_item: StackItem) -> None: 
        """
        Use to throw exceptions from SYSCALLs
        """
    @property
    def current_context(self) -> ExecutionContext:
        """
        :type: ExecutionContext
        """
    @property
    def entry_context(self) -> ExecutionContext:
        """
        :type: ExecutionContext
        """
    @property
    def exception_message(self) -> str:
        """
        :type: str
        """
    @property
    def instruction_counter(self) -> int:
        """
        Instruction counter

        :type: int
        """
    @property
    def invocation_stack(self) -> typing.List[ExecutionContext]:
        """
        :type: typing.List[ExecutionContext]
        """
    @property
    def reference_counter(self) -> ReferenceCounter:
        """
        :type: ReferenceCounter
        """
    @property
    def result_stack(self) -> EvaluationStack:
        """
        :type: EvaluationStack
        """
    @property
    def state(self) -> VMState:
        """
        :type: VMState
        """
    @state.setter
    def state(self, arg0: VMState) -> None:
        pass
    @property
    def uncaught_exception(self) -> StackItem:
        """
        :type: StackItem
        """
    MAX_INVOCATION_STACK_SIZE = 1024
    MAX_ITEM_SIZE = 1048576
    MAX_SHIFT = 256
    MAX_STACK_SIZE = 2048
    MAX_TRYSTACK_NESTING_DEPTH = 16
    pass
class StackItem():
    def convert_to(self, destination_type: StackItemType) -> StackItem: 
        """
        Try to convert the current item to a different stack item type
        """
    def deep_copy(self, asImmutable: bool) -> StackItem: ...
    @staticmethod
    def from_interface(value: object) -> StackItem: 
        """
        Create a stack item (Null or InteropInterface) from any Python object.
        """
    def get_type(self) -> StackItemType: 
        """
        Get the stack item type
        """
    def to_array(self) -> bytes: ...
    def to_biginteger(self) -> BigInteger: ...
    def to_boolean(self) -> bool: ...
    pass
class BadScriptException(Exception, BaseException):
    pass
class PrimitiveType(StackItem):
    def __len__(self) -> int: ...
    def to_array(self) -> bytes: 
        """
        Return the underlying data as a bytes
        """
    pass
class BufferStackItem(StackItem):
    @typing.overload
    def __init__(self, data: bytes) -> None: 
        """
        Create a buffer with an initial size

        Create a buffer from binary data
        """
    @typing.overload
    def __init__(self, size: int) -> None: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    def to_array(self) -> bytes: ...
    pass
class ByteStringStackItem(PrimitiveType, StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, value: bytes) -> None: ...
    @typing.overload
    def __init__(self, value: str) -> None: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    __hash__ = None
    pass
class CompoundType(StackItem):
    def is_read_only(self) -> bool: ...
    pass
class EvaluationStack():
    def __init__(self, reference_counter: ReferenceCounter) -> None: ...
    def __len__(self) -> int: ...
    def clear(self) -> None: 
        """
        Remove all internal items.
        """
    def insert(self, index: int, item: StackItem) -> None: 
        """
        Add an item at a specific index
        """
    def peek(self, index: int = 0) -> StackItem: 
        """
        Return the top item or if specific the item at the given index.
        """
    def pop(self) -> StackItem: 
        """
        Remove and return the top item from the stack
        """
    def push(self, item: StackItem) -> None: 
        """
        Push item onto the stack
        """
    def remove(self, index: int) -> StackItem: 
        """
        Remove and return the item at the given index
        """
    @property
    def _items(self) -> typing.List[StackItem]:
        """
        :type: typing.List[StackItem]
        """
    pass
class ExceptionHandlingContext():
    def __init__(self, catch_pointer: int, finally_pointer: int) -> None: ...
    def has_catch(self) -> bool: ...
    def has_finally(self) -> bool: ...
    @property
    def catch_pointer(self) -> int:
        """
        :type: int
        """
    @catch_pointer.setter
    def catch_pointer(self, arg0: int) -> None:
        pass
    @property
    def end_pointer(self) -> int:
        """
        :type: int
        """
    @end_pointer.setter
    def end_pointer(self, arg0: int) -> None:
        pass
    @property
    def finally_pointer(self) -> int:
        """
        :type: int
        """
    @finally_pointer.setter
    def finally_pointer(self, arg0: int) -> None:
        pass
    @property
    def state(self) -> ExceptionHandlingState:
        """
        :type: ExceptionHandlingState
        """
    @state.setter
    def state(self, arg0: ExceptionHandlingState) -> None:
        pass
    pass
class ExceptionHandlingState():
    """
    Members:

      TRY

      CATCH

      FINALLY
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int_(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    CATCH: neo3vm.ExceptionHandlingState # value = <ExceptionHandlingState.CATCH: 1>
    FINALLY: neo3vm.ExceptionHandlingState # value = <ExceptionHandlingState.FINALLY: 2>
    TRY: neo3vm.ExceptionHandlingState # value = <ExceptionHandlingState.TRY: 0>
    __members__: dict # value = {'TRY': <ExceptionHandlingState.TRY: 0>, 'CATCH': <ExceptionHandlingState.CATCH: 1>, 'FINALLY': <ExceptionHandlingState.FINALLY: 2>}
    pass
class ExecutionContext():
    def __init__(self, script: Script, rvcount: int, reference_counter: ReferenceCounter) -> None: ...
    def clone(self, initial_ip_position: int = 0) -> ExecutionContext: ...
    def current_instruction(self) -> Instruction: ...
    def move_next(self) -> bool: ...
    @property
    def arguments(self) -> Slot:
        """
        :type: Slot
        """
    @property
    def call_flags(self) -> int:
        """
        :type: int
        """
    @call_flags.setter
    def call_flags(self, arg0: int) -> None:
        pass
    @property
    def calling_scripthash_bytes(self) -> bytes:
        """
        :type: bytes
        """
    @calling_scripthash_bytes.setter
    def calling_scripthash_bytes(self, arg1: bytes) -> None:
        pass
    @property
    def evaluation_stack(self) -> EvaluationStack:
        """
        :type: EvaluationStack
        """
    @property
    def extra_data(self) -> object:
        """
        :type: object
        """
    @extra_data.setter
    def extra_data(self, arg0: object) -> None:
        pass
    @property
    def ip(self) -> int:
        """
        Instruction pointer

        :type: int
        """
    @ip.setter
    def ip(self, arg1: int) -> None:
        """
        Instruction pointer
        """
    @property
    def local_variables(self) -> Slot:
        """
        :type: Slot
        """
    @property
    def nef_bytes(self) -> bytes:
        """
        :type: bytes
        """
    @nef_bytes.setter
    def nef_bytes(self, arg1: bytes) -> None:
        pass
    @property
    def notification_count(self) -> int:
        """
        :type: int
        """
    @notification_count.setter
    def notification_count(self, arg0: int) -> None:
        pass
    @property
    def push_on_return(self) -> bool:
        """
        :type: bool
        """
    @push_on_return.setter
    def push_on_return(self, arg0: bool) -> None:
        pass
    @property
    def rvcount(self) -> int:
        """
        :type: int
        """
    @rvcount.setter
    def rvcount(self, arg0: int) -> None:
        pass
    @property
    def script(self) -> Script:
        """
        :type: Script
        """
    @script.setter
    def script(self, arg0: Script) -> None:
        pass
    @property
    def scripthash_bytes(self) -> bytes:
        """
        :type: bytes
        """
    @scripthash_bytes.setter
    def scripthash_bytes(self, arg1: bytes) -> None:
        pass
    @property
    def snapshot(self) -> object:
        """
        :type: object
        """
    @snapshot.setter
    def snapshot(self, arg0: object) -> None:
        pass
    @property
    def static_fields(self) -> Slot:
        """
        :type: Slot
        """
    @property
    def try_stack(self) -> typing.List[ExceptionHandlingContext]:
        """
        :type: typing.List[ExceptionHandlingContext]
        """
    pass
class ApplicationEngineCpp(ExecutionEngine):
    def __init__(self, test_mode: bool = False) -> None: ...
    def add_gas(self, amount: int) -> None: ...
    @staticmethod
    def opcode_price(opcode: OpCode) -> int: ...
    def refuel(self, gas: int) -> None: ...
    @property
    def exec_fee_factor(self) -> int:
        """
        :type: int
        """
    @exec_fee_factor.setter
    def exec_fee_factor(self, arg0: int) -> None:
        pass
    @property
    def gas_amount(self) -> int:
        """
        :type: int
        """
    @gas_amount.setter
    def gas_amount(self, arg0: int) -> None:
        pass
    @property
    def gas_consumed(self) -> int:
        """
        :type: int
        """
    MAX_INVOCATION_STACK_SIZE = 1024
    MAX_ITEM_SIZE = 1048576
    MAX_STACK_SIZE = 2048
    pass
class Instruction():
    @staticmethod
    def RET() -> Instruction: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, script: bytes, ip: int) -> None: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    @property
    def opcode(self) -> OpCode:
        """
        :type: OpCode
        """
    @property
    def operand(self) -> bytes:
        """
        :type: bytes
        """
    @property
    def token_16(self) -> bytes:
        """
        :type: bytes
        """
    @property
    def token_32(self) -> bytes:
        """
        :type: bytes
        """
    @property
    def token_8(self) -> bytes:
        """
        :type: bytes
        """
    @property
    def token_8_1(self) -> bytes:
        """
        :type: bytes
        """
    @property
    def token_i16(self) -> int:
        """
        :type: int
        """
    @property
    def token_i32(self) -> int:
        """
        :type: int
        """
    @property
    def token_i32_1(self) -> int:
        """
        :type: int
        """
    @property
    def token_i8(self) -> int:
        """
        :type: int
        """
    @property
    def token_i8_1(self) -> int:
        """
        :type: int
        """
    @property
    def token_string(self) -> str:
        """
        :type: str
        """
    @property
    def token_u16(self) -> int:
        """
        :type: int
        """
    @property
    def token_u32(self) -> int:
        """
        :type: int
        """
    @property
    def token_u8(self) -> int:
        """
        :type: int
        """
    @property
    def token_u8_1(self) -> int:
        """
        :type: int
        """
    pass
class IntegerStackItem(PrimitiveType, StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    @typing.overload
    def __init__(self, data: bytes) -> None: ...
    @typing.overload
    def __init__(self, value: BigInteger) -> None: ...
    @typing.overload
    def __init__(self, value: int) -> None: ...
    def __int_(self) -> int: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    MAX_SIZE = 32
    __hash__ = None
    pass
class InteropStackItem(StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    def __init__(self, object_instance: object) -> None: ...
    def __str__(self) -> object: ...
    def get_object(self) -> object: 
        """
        Get the internally stored object
        """
    __hash__ = None
    pass
class MapStackItem(CompoundType, StackItem):
    def __contains__(self, arg0: PrimitiveType) -> bool: ...
    def __getitem__(self, arg0: PrimitiveType) -> StackItem: ...
    def __init__(self) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    def __reversed__(self) -> typing.Iterator: ...
    def __setitem__(self, arg0: PrimitiveType, arg1: StackItem) -> None: ...
    def clear(self) -> None: 
        """
        Remove all internal items.
        """
    def keys(self) -> typing.List[StackItem]: ...
    def remove(self, key: PrimitiveType) -> None: 
        """
        Remove pair by key
        """
    def values(self) -> typing.List[StackItem]: ...
    pass
class Neo3vmException(Exception, BaseException):
    pass
class NullStackItem(StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    def __init__(self) -> None: ...
    __hash__ = None
    pass
class OpCode():
    """
    Members:

      PUSHDATA1

      PUSHDATA2

      PUSHDATA4

      PUSHINT8

      PUSHINT16

      PUSHINT32

      PUSHINT64

      PUSHINT128

      PUSHINT256

      INITSSLOT

      INITSLOT

      RET

      NOP

      PUSHM1

      PUSH0

      PUSH1

      PUSH2

      PUSH3

      PUSH4

      PUSH5

      PUSH6

      PUSH7

      PUSH8

      PUSH9

      PUSH10

      PUSH11

      PUSH12

      PUSH13

      PUSH14

      PUSH15

      PUSH16

      PUSHNULL

      PUSHA

      THROW

      TRY

      TRY_L

      ENDTRY

      ENDTRY_L

      ENDFINALLY

      ASSERT

      ABORT

      JMP

      JMP_L

      JMPIF

      JMPIF_L

      JMPIFNOT

      JMPIFNOT_L

      JMPEQ

      JMPEQ_L

      JMPNE

      JMPNE_L

      JMPGT

      JMPGT_L

      JMPGE

      JMPGE_L

      JMPLT

      JMPLT_L

      JMPLE

      JMPLE_L

      CALL

      CALL_L

      CALLA

      CALLT

      DEPTH

      DROP

      NIP

      XDROP

      CLEAR

      DUP

      OVER

      PICK

      TUCK

      SWAP

      ROT

      ROLL

      NEWMAP

      REVERSE3

      REVERSE4

      REVERSEN

      STSFLD0

      STSFLD1

      STSFLD2

      STSFLD3

      STSFLD4

      STSFLD5

      STSFLD6

      STSFLD

      LDSFLD0

      LDSFLD1

      LDSFLD2

      LDSFLD3

      LDSFLD4

      LDSFLD5

      LDSFLD6

      LDSFLD

      STLOC0

      STLOC1

      STLOC2

      STLOC3

      STLOC4

      STLOC5

      STLOC6

      STLOC

      LDLOC0

      LDLOC1

      LDLOC2

      LDLOC3

      LDLOC4

      LDLOC5

      LDLOC6

      LDLOC

      STARG0

      STARG1

      STARG2

      STARG3

      STARG4

      STARG5

      STARG6

      STARG

      LDARG0

      LDARG1

      LDARG2

      LDARG3

      LDARG4

      LDARG5

      LDARG6

      LDARG

      NEWBUFFER

      NEWARRAY

      MEMCPY

      CAT

      DEC

      CONVERT

      SUBSTR

      LEFT

      RIGHT

      INVERT

      NEWSTRUCT

      AND

      OR

      XOR

      EQUAL

      NOTEQUAL

      SIGN

      ABS

      NEGATE

      INC

      ADD

      SUB

      MUL

      DIV

      MOD

      POW

      SQRT

      MODMUL

      MODPOW

      SHL

      SHR

      NOT

      BOOLAND

      BOOLOR

      NZ

      NUMEQUAL

      NUMNOTEQUAL

      LT

      LE

      GT

      GE

      MIN

      MAX

      WITHIN

      PACK

      PACKSTRUCT

      PACKMAP

      UNPACK

      NEWARRAY0

      NEWARRAY_T

      SETITEM

      NEWSTRUCT0

      SIZE

      HASKEY

      KEYS

      VALUES

      PICKITEM

      APPEND

      REVERSEITEMS

      REMOVE

      CLEARITEMS

      POPITEM

      ISNULL

      ISTYPE

      SYSCALL
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int_(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ABORT: neo3vm.OpCode # value = <OpCode.ABORT: 56>
    ABS: neo3vm.OpCode # value = <OpCode.ABS: 154>
    ADD: neo3vm.OpCode # value = <OpCode.ADD: 158>
    AND: neo3vm.OpCode # value = <OpCode.AND: 145>
    APPEND: neo3vm.OpCode # value = <OpCode.APPEND: 207>
    ASSERT: neo3vm.OpCode # value = <OpCode.ASSERT: 57>
    BOOLAND: neo3vm.OpCode # value = <OpCode.BOOLAND: 171>
    BOOLOR: neo3vm.OpCode # value = <OpCode.BOOLOR: 172>
    CALL: neo3vm.OpCode # value = <OpCode.CALL: 52>
    CALLA: neo3vm.OpCode # value = <OpCode.CALLA: 54>
    CALLT: neo3vm.OpCode # value = <OpCode.CALLT: 55>
    CALL_L: neo3vm.OpCode # value = <OpCode.CALL_L: 53>
    CAT: neo3vm.OpCode # value = <OpCode.CAT: 139>
    CLEAR: neo3vm.OpCode # value = <OpCode.CLEAR: 73>
    CLEARITEMS: neo3vm.OpCode # value = <OpCode.CLEARITEMS: 211>
    CONVERT: neo3vm.OpCode # value = <OpCode.CONVERT: 219>
    DEC: neo3vm.OpCode # value = <OpCode.DEC: 157>
    DEPTH: neo3vm.OpCode # value = <OpCode.DEPTH: 67>
    DIV: neo3vm.OpCode # value = <OpCode.DIV: 161>
    DROP: neo3vm.OpCode # value = <OpCode.DROP: 69>
    DUP: neo3vm.OpCode # value = <OpCode.DUP: 74>
    ENDFINALLY: neo3vm.OpCode # value = <OpCode.ENDFINALLY: 63>
    ENDTRY: neo3vm.OpCode # value = <OpCode.ENDTRY: 61>
    ENDTRY_L: neo3vm.OpCode # value = <OpCode.ENDTRY_L: 62>
    EQUAL: neo3vm.OpCode # value = <OpCode.EQUAL: 151>
    GE: neo3vm.OpCode # value = <OpCode.GE: 184>
    GT: neo3vm.OpCode # value = <OpCode.GT: 183>
    HASKEY: neo3vm.OpCode # value = <OpCode.HASKEY: 203>
    INC: neo3vm.OpCode # value = <OpCode.INC: 156>
    INITSLOT: neo3vm.OpCode # value = <OpCode.INITSLOT: 87>
    INITSSLOT: neo3vm.OpCode # value = <OpCode.INITSSLOT: 86>
    INVERT: neo3vm.OpCode # value = <OpCode.INVERT: 144>
    ISNULL: neo3vm.OpCode # value = <OpCode.ISNULL: 216>
    ISTYPE: neo3vm.OpCode # value = <OpCode.ISTYPE: 217>
    JMP: neo3vm.OpCode # value = <OpCode.JMP: 34>
    JMPEQ: neo3vm.OpCode # value = <OpCode.JMPEQ: 40>
    JMPEQ_L: neo3vm.OpCode # value = <OpCode.JMPEQ_L: 41>
    JMPGE: neo3vm.OpCode # value = <OpCode.JMPGE: 46>
    JMPGE_L: neo3vm.OpCode # value = <OpCode.JMPGE_L: 47>
    JMPGT: neo3vm.OpCode # value = <OpCode.JMPGT: 44>
    JMPGT_L: neo3vm.OpCode # value = <OpCode.JMPGT_L: 45>
    JMPIF: neo3vm.OpCode # value = <OpCode.JMPIF: 36>
    JMPIFNOT: neo3vm.OpCode # value = <OpCode.JMPIFNOT: 38>
    JMPIFNOT_L: neo3vm.OpCode # value = <OpCode.JMPIFNOT_L: 39>
    JMPIF_L: neo3vm.OpCode # value = <OpCode.JMPIF_L: 37>
    JMPLE: neo3vm.OpCode # value = <OpCode.JMPLE: 50>
    JMPLE_L: neo3vm.OpCode # value = <OpCode.JMPLE_L: 51>
    JMPLT: neo3vm.OpCode # value = <OpCode.JMPLT: 48>
    JMPLT_L: neo3vm.OpCode # value = <OpCode.JMPLT_L: 49>
    JMPNE: neo3vm.OpCode # value = <OpCode.JMPNE: 42>
    JMPNE_L: neo3vm.OpCode # value = <OpCode.JMPNE_L: 43>
    JMP_L: neo3vm.OpCode # value = <OpCode.JMP_L: 35>
    KEYS: neo3vm.OpCode # value = <OpCode.KEYS: 204>
    LDARG: neo3vm.OpCode # value = <OpCode.LDARG: 127>
    LDARG0: neo3vm.OpCode # value = <OpCode.LDARG0: 120>
    LDARG1: neo3vm.OpCode # value = <OpCode.LDARG1: 121>
    LDARG2: neo3vm.OpCode # value = <OpCode.LDARG2: 122>
    LDARG3: neo3vm.OpCode # value = <OpCode.LDARG3: 123>
    LDARG4: neo3vm.OpCode # value = <OpCode.LDARG4: 124>
    LDARG5: neo3vm.OpCode # value = <OpCode.LDARG5: 125>
    LDARG6: neo3vm.OpCode # value = <OpCode.LDARG6: 126>
    LDLOC: neo3vm.OpCode # value = <OpCode.LDLOC: 111>
    LDLOC0: neo3vm.OpCode # value = <OpCode.LDLOC0: 104>
    LDLOC1: neo3vm.OpCode # value = <OpCode.LDLOC1: 105>
    LDLOC2: neo3vm.OpCode # value = <OpCode.LDLOC2: 106>
    LDLOC3: neo3vm.OpCode # value = <OpCode.LDLOC3: 107>
    LDLOC4: neo3vm.OpCode # value = <OpCode.LDLOC4: 108>
    LDLOC5: neo3vm.OpCode # value = <OpCode.LDLOC5: 109>
    LDLOC6: neo3vm.OpCode # value = <OpCode.LDLOC6: 110>
    LDSFLD: neo3vm.OpCode # value = <OpCode.LDSFLD: 95>
    LDSFLD0: neo3vm.OpCode # value = <OpCode.LDSFLD0: 88>
    LDSFLD1: neo3vm.OpCode # value = <OpCode.LDSFLD1: 89>
    LDSFLD2: neo3vm.OpCode # value = <OpCode.LDSFLD2: 90>
    LDSFLD3: neo3vm.OpCode # value = <OpCode.LDSFLD3: 91>
    LDSFLD4: neo3vm.OpCode # value = <OpCode.LDSFLD4: 92>
    LDSFLD5: neo3vm.OpCode # value = <OpCode.LDSFLD5: 93>
    LDSFLD6: neo3vm.OpCode # value = <OpCode.LDSFLD6: 94>
    LE: neo3vm.OpCode # value = <OpCode.LE: 182>
    LEFT: neo3vm.OpCode # value = <OpCode.LEFT: 141>
    LT: neo3vm.OpCode # value = <OpCode.LT: 181>
    MAX: neo3vm.OpCode # value = <OpCode.MAX: 186>
    MEMCPY: neo3vm.OpCode # value = <OpCode.MEMCPY: 137>
    MIN: neo3vm.OpCode # value = <OpCode.MIN: 185>
    MOD: neo3vm.OpCode # value = <OpCode.MOD: 162>
    MODMUL: neo3vm.OpCode # value = <OpCode.MODMUL: 165>
    MODPOW: neo3vm.OpCode # value = <OpCode.MODPOW: 166>
    MUL: neo3vm.OpCode # value = <OpCode.MUL: 160>
    NEGATE: neo3vm.OpCode # value = <OpCode.NEGATE: 155>
    NEWARRAY: neo3vm.OpCode # value = <OpCode.NEWARRAY: 195>
    NEWARRAY0: neo3vm.OpCode # value = <OpCode.NEWARRAY0: 194>
    NEWARRAY_T: neo3vm.OpCode # value = <OpCode.NEWARRAY_T: 196>
    NEWBUFFER: neo3vm.OpCode # value = <OpCode.NEWBUFFER: 136>
    NEWMAP: neo3vm.OpCode # value = <OpCode.NEWMAP: 200>
    NEWSTRUCT: neo3vm.OpCode # value = <OpCode.NEWSTRUCT: 198>
    NEWSTRUCT0: neo3vm.OpCode # value = <OpCode.NEWSTRUCT0: 197>
    NIP: neo3vm.OpCode # value = <OpCode.NIP: 70>
    NOP: neo3vm.OpCode # value = <OpCode.NOP: 33>
    NOT: neo3vm.OpCode # value = <OpCode.NOT: 170>
    NOTEQUAL: neo3vm.OpCode # value = <OpCode.NOTEQUAL: 152>
    NUMEQUAL: neo3vm.OpCode # value = <OpCode.NUMEQUAL: 179>
    NUMNOTEQUAL: neo3vm.OpCode # value = <OpCode.NUMNOTEQUAL: 180>
    NZ: neo3vm.OpCode # value = <OpCode.NZ: 177>
    OR: neo3vm.OpCode # value = <OpCode.OR: 146>
    OVER: neo3vm.OpCode # value = <OpCode.OVER: 75>
    PACK: neo3vm.OpCode # value = <OpCode.PACK: 192>
    PACKMAP: neo3vm.OpCode # value = <OpCode.PACKMAP: 190>
    PACKSTRUCT: neo3vm.OpCode # value = <OpCode.PACKSTRUCT: 191>
    PICK: neo3vm.OpCode # value = <OpCode.PICK: 77>
    PICKITEM: neo3vm.OpCode # value = <OpCode.PICKITEM: 206>
    POPITEM: neo3vm.OpCode # value = <OpCode.POPITEM: 212>
    POW: neo3vm.OpCode # value = <OpCode.POW: 163>
    PUSH0: neo3vm.OpCode # value = <OpCode.PUSH0: 16>
    PUSH1: neo3vm.OpCode # value = <OpCode.PUSH1: 17>
    PUSH10: neo3vm.OpCode # value = <OpCode.PUSH10: 26>
    PUSH11: neo3vm.OpCode # value = <OpCode.PUSH11: 27>
    PUSH12: neo3vm.OpCode # value = <OpCode.PUSH12: 28>
    PUSH13: neo3vm.OpCode # value = <OpCode.PUSH13: 29>
    PUSH14: neo3vm.OpCode # value = <OpCode.PUSH14: 30>
    PUSH15: neo3vm.OpCode # value = <OpCode.PUSH15: 31>
    PUSH16: neo3vm.OpCode # value = <OpCode.PUSH16: 32>
    PUSH2: neo3vm.OpCode # value = <OpCode.PUSH2: 18>
    PUSH3: neo3vm.OpCode # value = <OpCode.PUSH3: 19>
    PUSH4: neo3vm.OpCode # value = <OpCode.PUSH4: 20>
    PUSH5: neo3vm.OpCode # value = <OpCode.PUSH5: 21>
    PUSH6: neo3vm.OpCode # value = <OpCode.PUSH6: 22>
    PUSH7: neo3vm.OpCode # value = <OpCode.PUSH7: 23>
    PUSH8: neo3vm.OpCode # value = <OpCode.PUSH8: 24>
    PUSH9: neo3vm.OpCode # value = <OpCode.PUSH9: 25>
    PUSHA: neo3vm.OpCode # value = <OpCode.PUSHA: 10>
    PUSHDATA1: neo3vm.OpCode # value = <OpCode.PUSHDATA1: 12>
    PUSHDATA2: neo3vm.OpCode # value = <OpCode.PUSHDATA2: 13>
    PUSHDATA4: neo3vm.OpCode # value = <OpCode.PUSHDATA4: 14>
    PUSHINT128: neo3vm.OpCode # value = <OpCode.PUSHINT128: 4>
    PUSHINT16: neo3vm.OpCode # value = <OpCode.PUSHINT16: 1>
    PUSHINT256: neo3vm.OpCode # value = <OpCode.PUSHINT256: 5>
    PUSHINT32: neo3vm.OpCode # value = <OpCode.PUSHINT32: 2>
    PUSHINT64: neo3vm.OpCode # value = <OpCode.PUSHINT64: 3>
    PUSHINT8: neo3vm.OpCode # value = <OpCode.PUSHINT8: 0>
    PUSHM1: neo3vm.OpCode # value = <OpCode.PUSHM1: 15>
    PUSHNULL: neo3vm.OpCode # value = <OpCode.PUSHNULL: 11>
    REMOVE: neo3vm.OpCode # value = <OpCode.REMOVE: 210>
    RET: neo3vm.OpCode # value = <OpCode.RET: 64>
    REVERSE3: neo3vm.OpCode # value = <OpCode.REVERSE3: 83>
    REVERSE4: neo3vm.OpCode # value = <OpCode.REVERSE4: 84>
    REVERSEITEMS: neo3vm.OpCode # value = <OpCode.REVERSEITEMS: 209>
    REVERSEN: neo3vm.OpCode # value = <OpCode.REVERSEN: 85>
    RIGHT: neo3vm.OpCode # value = <OpCode.RIGHT: 142>
    ROLL: neo3vm.OpCode # value = <OpCode.ROLL: 82>
    ROT: neo3vm.OpCode # value = <OpCode.ROT: 81>
    SETITEM: neo3vm.OpCode # value = <OpCode.SETITEM: 208>
    SHL: neo3vm.OpCode # value = <OpCode.SHL: 168>
    SHR: neo3vm.OpCode # value = <OpCode.SHR: 169>
    SIGN: neo3vm.OpCode # value = <OpCode.SIGN: 153>
    SIZE: neo3vm.OpCode # value = <OpCode.SIZE: 202>
    SQRT: neo3vm.OpCode # value = <OpCode.SQRT: 164>
    STARG: neo3vm.OpCode # value = <OpCode.STARG: 135>
    STARG0: neo3vm.OpCode # value = <OpCode.STARG0: 128>
    STARG1: neo3vm.OpCode # value = <OpCode.STARG1: 129>
    STARG2: neo3vm.OpCode # value = <OpCode.STARG2: 130>
    STARG3: neo3vm.OpCode # value = <OpCode.STARG3: 131>
    STARG4: neo3vm.OpCode # value = <OpCode.STARG4: 132>
    STARG5: neo3vm.OpCode # value = <OpCode.STARG5: 133>
    STARG6: neo3vm.OpCode # value = <OpCode.STARG6: 134>
    STLOC: neo3vm.OpCode # value = <OpCode.STLOC: 119>
    STLOC0: neo3vm.OpCode # value = <OpCode.STLOC0: 112>
    STLOC1: neo3vm.OpCode # value = <OpCode.STLOC1: 113>
    STLOC2: neo3vm.OpCode # value = <OpCode.STLOC2: 114>
    STLOC3: neo3vm.OpCode # value = <OpCode.STLOC3: 115>
    STLOC4: neo3vm.OpCode # value = <OpCode.STLOC4: 116>
    STLOC5: neo3vm.OpCode # value = <OpCode.STLOC5: 117>
    STLOC6: neo3vm.OpCode # value = <OpCode.STLOC6: 118>
    STSFLD: neo3vm.OpCode # value = <OpCode.STSFLD: 103>
    STSFLD0: neo3vm.OpCode # value = <OpCode.STSFLD0: 96>
    STSFLD1: neo3vm.OpCode # value = <OpCode.STSFLD1: 97>
    STSFLD2: neo3vm.OpCode # value = <OpCode.STSFLD2: 98>
    STSFLD3: neo3vm.OpCode # value = <OpCode.STSFLD3: 99>
    STSFLD4: neo3vm.OpCode # value = <OpCode.STSFLD4: 100>
    STSFLD5: neo3vm.OpCode # value = <OpCode.STSFLD5: 101>
    STSFLD6: neo3vm.OpCode # value = <OpCode.STSFLD6: 102>
    SUB: neo3vm.OpCode # value = <OpCode.SUB: 159>
    SUBSTR: neo3vm.OpCode # value = <OpCode.SUBSTR: 140>
    SWAP: neo3vm.OpCode # value = <OpCode.SWAP: 80>
    SYSCALL: neo3vm.OpCode # value = <OpCode.SYSCALL: 65>
    THROW: neo3vm.OpCode # value = <OpCode.THROW: 58>
    TRY: neo3vm.OpCode # value = <OpCode.TRY: 59>
    TRY_L: neo3vm.OpCode # value = <OpCode.TRY_L: 60>
    TUCK: neo3vm.OpCode # value = <OpCode.TUCK: 78>
    UNPACK: neo3vm.OpCode # value = <OpCode.UNPACK: 193>
    VALUES: neo3vm.OpCode # value = <OpCode.VALUES: 205>
    WITHIN: neo3vm.OpCode # value = <OpCode.WITHIN: 187>
    XDROP: neo3vm.OpCode # value = <OpCode.XDROP: 72>
    XOR: neo3vm.OpCode # value = <OpCode.XOR: 147>
    __members__: dict # value = {'PUSHDATA1': <OpCode.PUSHDATA1: 12>, 'PUSHDATA2': <OpCode.PUSHDATA2: 13>, 'PUSHDATA4': <OpCode.PUSHDATA4: 14>, 'PUSHINT8': <OpCode.PUSHINT8: 0>, 'PUSHINT16': <OpCode.PUSHINT16: 1>, 'PUSHINT32': <OpCode.PUSHINT32: 2>, 'PUSHINT64': <OpCode.PUSHINT64: 3>, 'PUSHINT128': <OpCode.PUSHINT128: 4>, 'PUSHINT256': <OpCode.PUSHINT256: 5>, 'INITSSLOT': <OpCode.INITSSLOT: 86>, 'INITSLOT': <OpCode.INITSLOT: 87>, 'RET': <OpCode.RET: 64>, 'NOP': <OpCode.NOP: 33>, 'PUSHM1': <OpCode.PUSHM1: 15>, 'PUSH0': <OpCode.PUSH0: 16>, 'PUSH1': <OpCode.PUSH1: 17>, 'PUSH2': <OpCode.PUSH2: 18>, 'PUSH3': <OpCode.PUSH3: 19>, 'PUSH4': <OpCode.PUSH4: 20>, 'PUSH5': <OpCode.PUSH5: 21>, 'PUSH6': <OpCode.PUSH6: 22>, 'PUSH7': <OpCode.PUSH7: 23>, 'PUSH8': <OpCode.PUSH8: 24>, 'PUSH9': <OpCode.PUSH9: 25>, 'PUSH10': <OpCode.PUSH10: 26>, 'PUSH11': <OpCode.PUSH11: 27>, 'PUSH12': <OpCode.PUSH12: 28>, 'PUSH13': <OpCode.PUSH13: 29>, 'PUSH14': <OpCode.PUSH14: 30>, 'PUSH15': <OpCode.PUSH15: 31>, 'PUSH16': <OpCode.PUSH16: 32>, 'PUSHNULL': <OpCode.PUSHNULL: 11>, 'PUSHA': <OpCode.PUSHA: 10>, 'THROW': <OpCode.THROW: 58>, 'TRY': <OpCode.TRY: 59>, 'TRY_L': <OpCode.TRY_L: 60>, 'ENDTRY': <OpCode.ENDTRY: 61>, 'ENDTRY_L': <OpCode.ENDTRY_L: 62>, 'ENDFINALLY': <OpCode.ENDFINALLY: 63>, 'ASSERT': <OpCode.ASSERT: 57>, 'ABORT': <OpCode.ABORT: 56>, 'JMP': <OpCode.JMP: 34>, 'JMP_L': <OpCode.JMP_L: 35>, 'JMPIF': <OpCode.JMPIF: 36>, 'JMPIF_L': <OpCode.JMPIF_L: 37>, 'JMPIFNOT': <OpCode.JMPIFNOT: 38>, 'JMPIFNOT_L': <OpCode.JMPIFNOT_L: 39>, 'JMPEQ': <OpCode.JMPEQ: 40>, 'JMPEQ_L': <OpCode.JMPEQ_L: 41>, 'JMPNE': <OpCode.JMPNE: 42>, 'JMPNE_L': <OpCode.JMPNE_L: 43>, 'JMPGT': <OpCode.JMPGT: 44>, 'JMPGT_L': <OpCode.JMPGT_L: 45>, 'JMPGE': <OpCode.JMPGE: 46>, 'JMPGE_L': <OpCode.JMPGE_L: 47>, 'JMPLT': <OpCode.JMPLT: 48>, 'JMPLT_L': <OpCode.JMPLT_L: 49>, 'JMPLE': <OpCode.JMPLE: 50>, 'JMPLE_L': <OpCode.JMPLE_L: 51>, 'CALL': <OpCode.CALL: 52>, 'CALL_L': <OpCode.CALL_L: 53>, 'CALLA': <OpCode.CALLA: 54>, 'CALLT': <OpCode.CALLT: 55>, 'DEPTH': <OpCode.DEPTH: 67>, 'DROP': <OpCode.DROP: 69>, 'NIP': <OpCode.NIP: 70>, 'XDROP': <OpCode.XDROP: 72>, 'CLEAR': <OpCode.CLEAR: 73>, 'DUP': <OpCode.DUP: 74>, 'OVER': <OpCode.OVER: 75>, 'PICK': <OpCode.PICK: 77>, 'TUCK': <OpCode.TUCK: 78>, 'SWAP': <OpCode.SWAP: 80>, 'ROT': <OpCode.ROT: 81>, 'ROLL': <OpCode.ROLL: 82>, 'NEWMAP': <OpCode.NEWMAP: 200>, 'REVERSE3': <OpCode.REVERSE3: 83>, 'REVERSE4': <OpCode.REVERSE4: 84>, 'REVERSEN': <OpCode.REVERSEN: 85>, 'STSFLD0': <OpCode.STSFLD0: 96>, 'STSFLD1': <OpCode.STSFLD1: 97>, 'STSFLD2': <OpCode.STSFLD2: 98>, 'STSFLD3': <OpCode.STSFLD3: 99>, 'STSFLD4': <OpCode.STSFLD4: 100>, 'STSFLD5': <OpCode.STSFLD5: 101>, 'STSFLD6': <OpCode.STSFLD6: 102>, 'STSFLD': <OpCode.STSFLD: 103>, 'LDSFLD0': <OpCode.LDSFLD0: 88>, 'LDSFLD1': <OpCode.LDSFLD1: 89>, 'LDSFLD2': <OpCode.LDSFLD2: 90>, 'LDSFLD3': <OpCode.LDSFLD3: 91>, 'LDSFLD4': <OpCode.LDSFLD4: 92>, 'LDSFLD5': <OpCode.LDSFLD5: 93>, 'LDSFLD6': <OpCode.LDSFLD6: 94>, 'LDSFLD': <OpCode.LDSFLD: 95>, 'STLOC0': <OpCode.STLOC0: 112>, 'STLOC1': <OpCode.STLOC1: 113>, 'STLOC2': <OpCode.STLOC2: 114>, 'STLOC3': <OpCode.STLOC3: 115>, 'STLOC4': <OpCode.STLOC4: 116>, 'STLOC5': <OpCode.STLOC5: 117>, 'STLOC6': <OpCode.STLOC6: 118>, 'STLOC': <OpCode.STLOC: 119>, 'LDLOC0': <OpCode.LDLOC0: 104>, 'LDLOC1': <OpCode.LDLOC1: 105>, 'LDLOC2': <OpCode.LDLOC2: 106>, 'LDLOC3': <OpCode.LDLOC3: 107>, 'LDLOC4': <OpCode.LDLOC4: 108>, 'LDLOC5': <OpCode.LDLOC5: 109>, 'LDLOC6': <OpCode.LDLOC6: 110>, 'LDLOC': <OpCode.LDLOC: 111>, 'STARG0': <OpCode.STARG0: 128>, 'STARG1': <OpCode.STARG1: 129>, 'STARG2': <OpCode.STARG2: 130>, 'STARG3': <OpCode.STARG3: 131>, 'STARG4': <OpCode.STARG4: 132>, 'STARG5': <OpCode.STARG5: 133>, 'STARG6': <OpCode.STARG6: 134>, 'STARG': <OpCode.STARG: 135>, 'LDARG0': <OpCode.LDARG0: 120>, 'LDARG1': <OpCode.LDARG1: 121>, 'LDARG2': <OpCode.LDARG2: 122>, 'LDARG3': <OpCode.LDARG3: 123>, 'LDARG4': <OpCode.LDARG4: 124>, 'LDARG5': <OpCode.LDARG5: 125>, 'LDARG6': <OpCode.LDARG6: 126>, 'LDARG': <OpCode.LDARG: 127>, 'NEWBUFFER': <OpCode.NEWBUFFER: 136>, 'NEWARRAY': <OpCode.NEWARRAY: 195>, 'MEMCPY': <OpCode.MEMCPY: 137>, 'CAT': <OpCode.CAT: 139>, 'DEC': <OpCode.DEC: 157>, 'CONVERT': <OpCode.CONVERT: 219>, 'SUBSTR': <OpCode.SUBSTR: 140>, 'LEFT': <OpCode.LEFT: 141>, 'RIGHT': <OpCode.RIGHT: 142>, 'INVERT': <OpCode.INVERT: 144>, 'NEWSTRUCT': <OpCode.NEWSTRUCT: 198>, 'AND': <OpCode.AND: 145>, 'OR': <OpCode.OR: 146>, 'XOR': <OpCode.XOR: 147>, 'EQUAL': <OpCode.EQUAL: 151>, 'NOTEQUAL': <OpCode.NOTEQUAL: 152>, 'SIGN': <OpCode.SIGN: 153>, 'ABS': <OpCode.ABS: 154>, 'NEGATE': <OpCode.NEGATE: 155>, 'INC': <OpCode.INC: 156>, 'ADD': <OpCode.ADD: 158>, 'SUB': <OpCode.SUB: 159>, 'MUL': <OpCode.MUL: 160>, 'DIV': <OpCode.DIV: 161>, 'MOD': <OpCode.MOD: 162>, 'POW': <OpCode.POW: 163>, 'SQRT': <OpCode.SQRT: 164>, 'MODMUL': <OpCode.MODMUL: 165>, 'MODPOW': <OpCode.MODPOW: 166>, 'SHL': <OpCode.SHL: 168>, 'SHR': <OpCode.SHR: 169>, 'NOT': <OpCode.NOT: 170>, 'BOOLAND': <OpCode.BOOLAND: 171>, 'BOOLOR': <OpCode.BOOLOR: 172>, 'NZ': <OpCode.NZ: 177>, 'NUMEQUAL': <OpCode.NUMEQUAL: 179>, 'NUMNOTEQUAL': <OpCode.NUMNOTEQUAL: 180>, 'LT': <OpCode.LT: 181>, 'LE': <OpCode.LE: 182>, 'GT': <OpCode.GT: 183>, 'GE': <OpCode.GE: 184>, 'MIN': <OpCode.MIN: 185>, 'MAX': <OpCode.MAX: 186>, 'WITHIN': <OpCode.WITHIN: 187>, 'PACK': <OpCode.PACK: 192>, 'PACKSTRUCT': <OpCode.PACKSTRUCT: 191>, 'PACKMAP': <OpCode.PACKMAP: 190>, 'UNPACK': <OpCode.UNPACK: 193>, 'NEWARRAY0': <OpCode.NEWARRAY0: 194>, 'NEWARRAY_T': <OpCode.NEWARRAY_T: 196>, 'SETITEM': <OpCode.SETITEM: 208>, 'NEWSTRUCT0': <OpCode.NEWSTRUCT0: 197>, 'SIZE': <OpCode.SIZE: 202>, 'HASKEY': <OpCode.HASKEY: 203>, 'KEYS': <OpCode.KEYS: 204>, 'VALUES': <OpCode.VALUES: 205>, 'PICKITEM': <OpCode.PICKITEM: 206>, 'APPEND': <OpCode.APPEND: 207>, 'REVERSEITEMS': <OpCode.REVERSEITEMS: 209>, 'REMOVE': <OpCode.REMOVE: 210>, 'CLEARITEMS': <OpCode.CLEARITEMS: 211>, 'POPITEM': <OpCode.POPITEM: 212>, 'ISNULL': <OpCode.ISNULL: 216>, 'ISTYPE': <OpCode.ISTYPE: 217>, 'SYSCALL': <OpCode.SYSCALL: 65>}
    pass
class PointerStackItem(StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    def __init__(self, script: Script, position: int) -> None: ...
    @property
    def position(self) -> int:
        """
        :type: int
        """
    @property
    def script(self) -> Script:
        """
        :type: Script
        """
    __hash__ = None
    pass
class BooleanStackItem(PrimitiveType, StackItem):
    def __bool_(self) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: StackItem) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: bool) -> bool: ...
    def __init__(self, arg0: bool) -> None: ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...
    __hash__ = None
    pass
class ReferenceCounter():
    def __init__(self) -> None: ...
    @property
    def count(self) -> int:
        """
        :type: int
        """
    pass
class Script():
    @typing.overload
    def __eq__(self, arg0: Script) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: object) -> bool: ...
    def __ge__(self, arg0: Script) -> bool: ...
    def __gt__(self, arg0: Script) -> bool: ...
    @typing.overload
    def __init__(self) -> None: 
        """
        Create a script from a byte array. Strict mode does a limited verification on the script and throws an exception if validation fails.
        """
    @typing.overload
    def __init__(self, data: bytes, strict_mode: bool = False) -> None: ...
    def __le__(self, arg0: Script) -> bool: ...
    def __len__(self) -> int: ...
    def __lt__(self, arg0: Script) -> bool: ...
    def get_instruction(self, arg0: int) -> Instruction: ...
    @property
    def _value(self) -> bytes:
        """
        :type: bytes
        """
    __hash__ = None
    pass
class ScriptBuilder():
    def __init__(self) -> None: ...
    def __len__(self) -> int: ...
    @typing.overload
    def emit(self, opcode: OpCode) -> ScriptBuilder: ...
    @typing.overload
    def emit(self, opcode: OpCode, data: buffer) -> ScriptBuilder: ...
    def emit_call(self, offset: int) -> ScriptBuilder: ...
    def emit_jump(self, opcode: OpCode, offset: int) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, data: bytes) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, data: str) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, none: None) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, number: BigInteger) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, number: int) -> ScriptBuilder: ...
    @typing.overload
    def emit_push(self, with_data: bool) -> ScriptBuilder: ...
    def emit_raw(self, arg0: bytes) -> ScriptBuilder: 
        """
        Push data without applying variable size encoding
        """
    def emit_syscall(self, api_hash: int) -> ScriptBuilder: ...
    def to_array(self) -> bytes: ...
    pass
class Slot():
    def __getitem__(self, arg0: int) -> StackItem: ...
    @typing.overload
    def __init__(self, items: typing.List[StackItem], reference_counter: ReferenceCounter) -> None: ...
    @typing.overload
    def __init__(self, slot_size: int, reference_counter: ReferenceCounter) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg0: int, arg1: StackItem) -> None: ...
    @property
    def items(self) -> list:
        """
        :type: list
        """
    pass
class ArrayStackItem(CompoundType, StackItem):
    def __eq__(self, arg0: StackItem) -> bool: ...
    def __getitem__(self, arg0: int) -> StackItem: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, stack_item: StackItem) -> None: ...
    @typing.overload
    def __init__(self, stack_items: typing.List[StackItem]) -> None: ...
    def __iter__(self) -> typing.Iterator: 
        """
        Array items.
        """
    def __len__(self) -> int: ...
    def __reversed__(self) -> typing.Iterator: 
        """
        Array items in reversed order.
        """
    def __setitem__(self, arg0: int, arg1: StackItem) -> None: ...
    @typing.overload
    def append(self, stack_item: StackItem) -> None: ...
    @typing.overload
    def append(self, stack_items: typing.List[StackItem]) -> None: ...
    def clear(self) -> None: 
        """
        Remove all internal items.
        """
    def remove(self, index: int) -> None: 
        """
        Remove element by index
        """
    @property
    def _items(self) -> typing.List[StackItem]:
        """
        :type: typing.List[StackItem]
        """
    @property
    def _sub_items(self) -> typing.List[StackItem]:
        """
        :type: typing.List[StackItem]
        """
    __hash__ = None
    pass
class StackItemType():
    """
    Members:

      ANY

      POINTER

      BOOLEAN

      INTEGER

      BYTESTRING

      BUFFER

      ARRAY

      STRUCT

      MAP

      INTEROP
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int_(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    ANY: neo3vm.StackItemType # value = <StackItemType.ANY: 0>
    ARRAY: neo3vm.StackItemType # value = <StackItemType.ARRAY: 64>
    BOOLEAN: neo3vm.StackItemType # value = <StackItemType.BOOLEAN: 32>
    BUFFER: neo3vm.StackItemType # value = <StackItemType.BUFFER: 48>
    BYTESTRING: neo3vm.StackItemType # value = <StackItemType.BYTESTRING: 40>
    INTEGER: neo3vm.StackItemType # value = <StackItemType.INTEGER: 33>
    INTEROP: neo3vm.StackItemType # value = <StackItemType.INTEROP: 96>
    MAP: neo3vm.StackItemType # value = <StackItemType.MAP: 72>
    POINTER: neo3vm.StackItemType # value = <StackItemType.POINTER: 16>
    STRUCT: neo3vm.StackItemType # value = <StackItemType.STRUCT: 65>
    __members__: dict # value = {'ANY': <StackItemType.ANY: 0>, 'POINTER': <StackItemType.POINTER: 16>, 'BOOLEAN': <StackItemType.BOOLEAN: 32>, 'INTEGER': <StackItemType.INTEGER: 33>, 'BYTESTRING': <StackItemType.BYTESTRING: 40>, 'BUFFER': <StackItemType.BUFFER: 48>, 'ARRAY': <StackItemType.ARRAY: 64>, 'STRUCT': <StackItemType.STRUCT: 65>, 'MAP': <StackItemType.MAP: 72>, 'INTEROP': <StackItemType.INTEROP: 96>}
    pass
class StructStackItem(ArrayStackItem, CompoundType, StackItem):
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, stack_item: StackItem) -> None: ...
    @typing.overload
    def __init__(self, stack_items: typing.List[StackItem]) -> None: ...
    pass
class VMState():
    """
    Members:

      NONE

      HALT

      FAULT

      BREAK
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int_(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    BREAK: neo3vm.VMState # value = <VMState.BREAK: 4>
    FAULT: neo3vm.VMState # value = <VMState.FAULT: 2>
    HALT: neo3vm.VMState # value = <VMState.HALT: 1>
    NONE: neo3vm.VMState # value = <VMState.NONE: 0>
    __members__: dict # value = {'NONE': <VMState.NONE: 0>, 'HALT': <VMState.HALT: 1>, 'FAULT': <VMState.FAULT: 2>, 'BREAK': <VMState.BREAK: 4>}
    pass
