from uuid import uuid4
from textual import log
from rich.text import Text
from .shadow_tree import ShadowNode, ShadowTree
from .suite_tree import TestNode
from .text_styles import default, light, keyword, ret, event, revert
from .call_filters import call_method_eq, call_depth_lt, call_depth_eq


class TraceTreeNode(ShadowNode):
    def __init__(self, expanded=False):
        id = str(uuid4())
        super().__init__(id, expanded)

    def __repr__(self):
        if ('__short__' in dir(self)):
            return str(self.__short__())
        return str(self.__display__())


class CallNode(TraceTreeNode):
    args: list["LabeledArgumentNode"] = []

    def __init__(self, call):
        super().__init__(
            call_method_eq(call, "setUp") and
            call_depth_eq(call, 0) or
            call_depth_lt(call, 1))

        self.call = call
        self.args = []
        if (self.call.function.args):
            for i, arg in enumerate(self.call.function.args):
                arg_node = LabeledArgumentNode(arg, i.__str__())
                self.args.append(arg_node)
                self.add_child(arg_node)

    def __display__(self):
        return self.gas + " " + self.target + default("::") + self.function + self.call_type

    @property
    def gas(self):
        return light(f"[{self.call.gas}]")

    @property
    def call_type(self):
        if self.call.function.call_type:
            return light(f" [{self.call.function.call_type}]")
        else:
            return ''

    @property
    def target(self):
        if self.call.function.target.label:
            return keyword(self.call.function.target.label)
        else:
            return keyword(self.call.function.target.address)

    @property
    def function(self):
        return keyword(f"{self.method}(") + self.arguments + keyword(")")

    @property
    def arguments(self):
        if (self.args):
            output = Text()
            for i, arg in enumerate(self.args):
                output.append(arg.__short__())
                if i < len(self.args) - 1:
                    output.append(default(", "))
            return output
        elif self.call.function.raw_args:
            if len(self.call.function.raw_args[0]) > 32:
                return Text(self.call.function.raw_args[0][0:32] + "...")
            else:
                return Text(self.call.function.raw_args[0])
        else:
            return Text('')

    @property
    def method(self):
        if self.call.function.name:
            return Text(self.call.function.name)
        elif self.call.function.selector:
            return Text(self.call.function.selector)
        else:
            log(self.call)
            raise ValueError("No method name or selector found")


class ReturnNode(TraceTreeNode):
    def __init__(self, ret):
        super().__init__(False)
        self.ret = ret
        if ('returned_values' in self.ret and self.ret['returned_values']):
            for i, val in enumerate(self.ret.returned_values):
                val_node = LabeledArgumentNode(val, i.__str__())
                self.add_child(val_node)

    def __display__(self):
        return ret("← [Return]") + self.return_value

    @property
    def return_value(self):
        if ('returned_bytes' in self.ret):
            return default(" " + self.ret['returned_bytes']['count']) + light(" bytes of code")
        elif ('returned_values' in self.ret):
            output = Text(" ")
            for i, child in enumerate(self.children):
                output.append(child.__short__())
                if i < len(self.children) - 1:
                    output.append(", ")
            return output
        return ""


class RevertNode(TraceTreeNode):
    def __init__(self, revert):
        super().__init__(False)
        self.revert = revert

    def __display__(self):
        return revert("← [Revert] " + self.revert['reason'])


class StopNode(TraceTreeNode):
    def __init__(self):
        super().__init__(False)

    def __display__(self):
        return ret("← [Stop]")


class BaseValueNode():
    def __init__(self, value):
        self.value = value

    def __short__(self):
        return self.__display__()


class RawNode(BaseValueNode):
    def __display__(self):
        return "Raw: " + self.value.__str__()


class AddressNode(BaseValueNode):
    def __display__(self):
        if (self.value.label):
            output = Text()
            output.append(default(self.value.label + ": "))
            output.append(light(self.value.address))
            return output
        else:
            return self.value.address

    def __short__(self):
        if (self.value.label):
            output = Text()
            output.append(default(self.value.label))
            return output
        else:
            output = Text()
            output.append(default(self.value.address[0:10] + "..."))
            return output


class NumberNode(BaseValueNode):
    def __display__(self):
        output = Text()
        output.append(default(self.value.number.__str__()))
        if (self.value.scientific):
            output.append(" ")
            output.append(light(self.value.scientific.__str__()))
        return output

    def __short__(self):
        output = Text()
        if (self.value.scientific):
            output.append(default(self.value.scientific.__str__()))
        else:
            number_str = self.value.number.__str__()
            if len(number_str) > 10:
                output.append(default(number_str[0:10] + "..."))
            else:
                output.append(default(number_str))
        return output


class StringNode(BaseValueNode):
    def __display__(self):
        return default(f"\"{self.value.string}\"")


class BytesNode(BaseValueNode):
    def __display__(self):
        output = Text()
        output.append(default(self.value[0][0:66]))
        if len(self.value[0]) > 66:
            return output.append(default("..."))
        return output

    def __short__(self):
        output = Text()
        output.append(default(self.value[0][0:10] + "..."))
        return output


class StructNode(BaseValueNode):
    def __display__(self):
        return default(self.value.struct)

    def __short__(self):
        return default(self.value.struct+"{}")


class ArrayNode(BaseValueNode):
    def __display__(self):
        return default("[]")

    def __short__(self):
        return default("[...]")


class BoolNode(BaseValueNode):
    def __display__(self):
        if (self.value.boolean):
            return default("true")
        else:
            return default("false")


class ValueNode(TraceTreeNode):
    COLLAPSABLE = False

    def __init__(self, value):
        super().__init__(False)
        if value.string:
            self.value = StringNode(value)
        elif value.address:
            self.value = AddressNode(value)
        elif value.number != '':
            self.value = NumberNode(value)
        elif (value.bytes or value.bytes32 or value.bytes16 or value.bytes8 or value.bytes4):
            self.value = BytesNode(value)
        elif value.struct:
            self.value = StructNode(value)
            for member in value.members:
                self.children.append(
                    LabeledArgumentNode(member.value, member.key))
        elif value.array:
            self.value = ArrayNode(value)
            for i, item in enumerate(value.array):
                self.children.append(LabeledArgumentNode(item, i.__str__()))
        elif value.boolean != '':
            self.value = BoolNode(value)
        else:
            log("==================================")
            log(value)
            log(value.get_name())
            log(dir(value))
            log("==================================")
            self.value = RawNode(value)

    def __short__(self):
        return self.value.__short__()

    def __display__(self):
        return self.value.__display__()


class LabeledArgumentNode(ValueNode):
    __label__: str

    def __init__(self, value, label):
        super().__init__(value)
        self.__label__ = label

    def __display__(self):
        output = Text()
        output.append(light(self.__label__ + ": "))
        output.append(super().__display__())
        return output

    def __short__(self):
        return super().__short__()


class CreateNode(TraceTreeNode):
    def __init__(self, create):
        super().__init__(False)
        self.create = create

    def __display__(self):
        output = Text()
        output.append(ret("→  new "))
        output.append(ret(self.create.contract_name))
        output.append(light("@" + self.create.address))
        return self.gas + " " + output

    @property
    def gas(self):
        return light(f"[{self.create.gas}]")


class EventNode(TraceTreeNode):
    def __init__(self, event):
        super().__init__(True)
        self.event = event
        for arg in event.args:
            self.children.append(LabeledArgumentNode(arg.value, arg.key))

    def __display__(self):
        return event(f"emit {self.event.name}") + "(" + self.arguments + ")"

    @property
    def arguments(self):
        if (self.event.args):
            output = Text()
            for i, arg in enumerate(self.event.args):
                output.append(ValueNode(arg.value).__short__())
                if i < len(self.event.args) - 1:
                    output.append(default(", "))
            return output
        else:
            return Text('')


class TraceTree(ShadowTree):
    def __init__(self, output):
        self.output = output
        suite = output.suites[0]
        test = output.suites[0].tests[0]
        self.set_root(TestNode(test.test, test, suite))

        current_node = self.root
        for line in test.setup_traces + test.traces:
            current_node = self.__add_child__(current_node, line)

    def __add_child__(self, node, line):
        if line.get_name() == "call":
            return node.add_child(CallNode(line))
        elif line.get_name() == "create":
            return node.add_child(CreateNode(line))
        elif line.get_name() == "event":
            node.add_child(EventNode(line))
            return node
        elif line.get_name() == "end":
            if ('return' in line):
                node.add_child(ReturnNode(line['return']))
            elif ('revert' in line):
                node.add_child(RevertNode(line['revert']))
            elif ('stop' in line):
                node.add_child(StopNode())
            else:
                log(f"Unknown `end` type: `{line}`")
            return node.parent
        else:
            log(f"Unknown line type: `{line.get_name()}`")
            return node
