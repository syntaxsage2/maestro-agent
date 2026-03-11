"""
计算器工具
"""
import ast
import operator
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> float | int:
    """
    执行数学计算。支持加减乘除、幂运算、取模等。

    Args:
        expression: 数学表达式，例如 '2 + 3 * 4', '100 / 5', '2 ** 10'

    Returns:
        float | int: 计算结果

    Examples:
        >>> calculator("2 + 3 * 4")
        14
        >>> calculator("100 / 5")
        20.0
    """
    # 允许的运算符
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        """递归求值 AST 节点"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            op = operators.get(type(node.op))
            if op is None:
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            op = operators.get(type(node.op))
            if op is None:
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
            return op(operand)
        else:
            raise ValueError(f"不支持的节点类型: {type(node).__name__}")

    try:
        node = ast.parse(expression, mode='eval').body
        result = eval_node(node)
        return result
    except Exception as e:
        raise ValueError(f"无效的数学表达式: {expression}. 错误: {str(e)}")