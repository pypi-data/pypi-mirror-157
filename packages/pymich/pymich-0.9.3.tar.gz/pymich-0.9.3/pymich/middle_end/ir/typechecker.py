import ast

from pymich.middle_end.ir.instr_types import StdlibFunctionSpec, StdLibClassSpec
from pymich.middle_end.ir.vm_types import FunctionPrototype
from pymich.utils.compiler_stdlib import StdLib
import pymich.middle_end.ir.instr_types as t
from pymich.utils.environment import Env
import pymich.utils.exceptions as E


class TypeChecker:
    def __init__(self, std_lib: StdLib | None = None, type_parser: t.TypeParser | None = None) -> None:
        self.std_lib = std_lib if std_lib else StdLib()
        self.type_parser = type_parser if type_parser else t.TypeParser()

    def get_name_type(self, node, e: Env):
        if node.id in e.types:
            return e.types[node.id]
        elif node.id in self.std_lib.constants_mapping:
            if type(self.std_lib.constants_mapping[node.id]) == t.StdlibVariable:
                return self.std_lib.constants_mapping[node.id].type

            return self.std_lib.constants_mapping[node.id]
        else:
            raise E.FunctionNameException(node.id, node.lineno)

    def get_list_type(self, node, e: Env):
        if len(node.elts):
            elt_type = self.get_expression_type(node.elts[0], e)
            return t.List(elt_type)
        else:
            return t.List(t.Unknown())

    def get_dict_type(self, node, e: Env):
        if len(node.keys):
            key_type = self.get_expression_type(node.keys[0], e)
            value_type = self.get_expression_type(node.values[0], e)
            return t.Dict(key_type, value_type)
        else:
            return t.Dict(t.Unknown(), t.Unknown())

    def get_constant_type(self, node, e: Env):
        if type(node.value) == str:
            return t.PythonString()
        elif type(node.value) == int:
            return t.PythonInt()
        elif type(node.value) == bool:
            return t.Bool()
        else:
            raise E.TypeException(["str", "int", "bool"], node.value, node.lino)

    def get_subscript_type(self, node, e: Env):
        parent_type = self.get_expression_type(node.value, e)
        if type(parent_type) == t.Dict or type(parent_type) == t.BigMap:
            return parent_type.value_type
        elif type(parent_type) == t.List:
            return parent_type.element_type
        elif type(parent_type) == StdLibClassSpec:
            cast_type = self.type_parser.parse(node.slice, e)
            return parent_type.constructor.get_prototype([cast_type]).return_type
        elif type(parent_type) == StdlibFunctionSpec:
            cast_type = self.type_parser.parse(node.slice, e)
            return parent_type.get_prototype([cast_type]).return_type
        else:
            raise E.TypeException(t.polymorphic_types, parent_type, e)

    def get_attribute_type(self, node, e: Env):
        record = self.get_expression_type(node.value, e)
        if type(record) == StdLibClassSpec:
            if type(node.value) == ast.Name:
                if record.constructor:
                    record = record.constructor.get_prototype(t.Unknown()).return_type
                else:
                    if node.attr in record.attributes:
                        return record.attributes[node.attr].type
            elif type(record.value) == ast.Call:
                arg_types = [self.get_expression_type(arg, e) for arg in node.args]
                record = record.constructor.get_prototype(arg_types).return_type

        attr_value_type = type(record)
        if attr_value_type in self.std_lib.types_mapping:
            if node.attr in self.std_lib.types_mapping[attr_value_type].methods:
                return self.std_lib.types_mapping[attr_value_type].methods[node.attr].get_prototype(record).return_type

        if node.attr in record.attribute_names:
            return record.get_attribute_type(node.attr)
        else:
            raise E.AttributeException(record, node.attr, node.lineno)

    def get_call_type(self, node, e: Env):
        if type(node.func) == ast.Name and node.func.id in e.types:
            prototype = e.types[node.func.id]
            if type(prototype) == t.Record:
                # Dataclass constructor call
                return prototype
            elif isinstance(prototype, (t.StdlibMethodInstance, t.StdlibStaticMethodInstance)):
                # Stdlib method call
                return prototype.signature.return_type
            else:
                return e.types[node.func.id].return_type
        elif type(node.func) == ast.Name and node.func.id in self.std_lib.constants_mapping:
            if type(self.std_lib.constants_mapping[node.func.id]) == StdlibFunctionSpec:
                return self.std_lib.constants_mapping[node.func.id].get_prototype().return_type
            elif type(self.std_lib.constants_mapping[node.func.id]) == StdLibClassSpec:
                arg_types = [self.get_expression_type(arg, e) for arg in node.args]
                prototype = self.std_lib.constants_mapping[node.func.id].constructor.get_prototype(arg_types)
                if isinstance(prototype, FunctionPrototype):
                    is_polymorphic = isinstance(prototype.arg_type, t.Unknown)
                    if arg_types != [prototype.arg_type] and not is_polymorphic:
                        raise E.TypeException(prototype.arg_type, arg_types, e)
                return prototype.return_type
            else:
                raise E.CompilerException(f"Stdlib expression {node.func.id} cannot be typed", node.lineno)
        elif type(node.func) == ast.Attribute and node.func.attr == "unpack":
            cast_to_type = self.type_parser.parse(node.args[0], e)
            return self.std_lib.types_mapping[t.Bytes].methods["unpack"].get_prototype(cast_to_type).return_type
        else:
            return self.get_expression_type(node.func, e)

    def get_compare_type(self, node, e: Env):
        return t.Bool()

    def get_binop_type(self, node, e: Env):
        left_type = self.get_expression_type(node.left, e)
        right_type = self.get_expression_type(node.right, e)
        is_nat_subtraction = (
            isinstance(left_type, t.Nat)
            and isinstance(node.op, ast.Sub)
        )
        if is_nat_subtraction:
            return t.Int()

        is_mutez_subtraction = (
            isinstance(left_type, t.Mutez)
            and isinstance(node.op, ast.Sub)
        )
        if is_mutez_subtraction:
            return t.Option(t.Mutez())

        return self.get_expression_type(node.left, e)

    def get_expression_type(self, node, e: Env | None = None):
        if not e:
            e = Env({}, -1, {}, {})
            self.e = e

        if type(node) == ast.Name:
            return self.get_name_type(node, e)
        elif type(node) == ast.List:
            return self.get_list_type(node, e)
        elif type(node) == ast.Dict:
            return self.get_dict_type(node, e)
        elif type(node) == ast.Constant:
            return self.get_constant_type(node, e)
        elif type(node) == ast.Subscript:
            return self.get_subscript_type(node, e)
        elif type(node) == ast.Attribute:
            return self.get_attribute_type(node, e)
        elif type(node) == ast.Call:
            return self.get_call_type(node, e)
        elif type(node) == ast.BinOp:
            return self.get_binop_type(node, e)
        elif type(node) == ast.BoolOp:
            return t.Bool()
        elif type(node) == ast.UnaryOp:
            if isinstance(node.op, (ast.USub, ast.UAdd)):
                operand_type = self.get_expression_type(node.operand, e)
                if not isinstance(operand_type, t.PythonInt):
                    raise E.TypeException(["python_int"], operand_type, node.lineno)
                return operand_type
            return t.Bool()
        elif type(node) == ast.Compare:
            return self.get_compare_type(node, e)
        else:
            raise E.CompilerException(f"Expression {node} cannot be typed", node.lineno)


    def typecheck_module(self, m: ast.Module, e: Env) -> None:
        for key, value in ast.iter_fields(m):
            if key == "body":
                for child_node in value:
                    self.typecheck_ir(child_node, e)

    def typecheck_ir(self, node_ast, e: Env | None = None):
        if not e:
            e = Env({}, -1, {}, {})
            self.e = e

        if type(node_ast) == ast.Module:
            self.typecheck_module(node_ast, e)
        elif type(node_ast) == ast.Expr:
            self.typecheck_module(node_ast.value, e)
        else:
            self.get_expression_type(node_ast, e)
