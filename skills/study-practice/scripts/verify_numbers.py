#!/usr/bin/env python3
"""Recompute every number in a worked example, so a model never marks its own homework.

Usage:
  python verify_numbers.py worked.json [--quiet]

Input: one example object, a list of them, or {"examples": [...]}.

  {
    "id": "straight-line",
    "tolerance": 0.01,
    "inputs": {"cost": 12000, "residual": 2000, "life": 5},
    "steps": [
      {"name": "annual", "formula": "(cost - residual) / life", "result": 2000},
      {"name": "nbv2",   "formula": "cost - 2 * annual",        "result": 8000}
    ],
    "checks": [
      {"label": "NBV never below residual", "left": "max(nbv2, residual)", "right": "nbv2"}
    ]
  }

Steps run in order and each result becomes a variable for later steps. Checks assert
that two expressions are equal (within tolerance). Exit code 1 if anything differs.
Formulas are parsed with a tiny safe evaluator (numbers, + - * / // % **, parentheses,
min, max, abs, round, sum, sqrt). Nothing else is allowed.
"""
import ast
import json
import math
import operator
import sys

OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow,
}
FUNCS = {"min": min, "max": max, "abs": abs, "round": round, "sum": sum, "sqrt": math.sqrt}


class UnsafeFormula(ValueError):
    pass


def ev(node, env):
    if isinstance(node, ast.Expression):
        return ev(node.body, env)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in env:
            return env[node.id]
        raise UnsafeFormula("unknown name: %s" % node.id)
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        a, b = ev(node.left, env), ev(node.right, env)
        if isinstance(node.op, ast.Pow) and abs(b) > 100:
            raise UnsafeFormula("exponent too large")
        return OPS[type(node.op)](a, b)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        v = ev(node.operand, env)
        return -v if isinstance(node.op, ast.USub) else v
    if isinstance(node, (ast.List, ast.Tuple)):
        return [ev(e, env) for e in node.elts]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCS and not node.keywords:
        return FUNCS[node.func.id](*[ev(a, env) for a in node.args])
    raise UnsafeFormula("not allowed: %s" % type(node).__name__)


def evaluate(formula, env):
    return ev(ast.parse(str(formula), mode="eval"), env)


def close(a, b, tol):
    return abs(a - b) <= tol


def check_example(ex, quiet=False):
    """Return a list of failure strings (empty means the example is verified)."""
    eid = ex.get("id", "example")
    tol = float(ex.get("tolerance", 0.01))
    env = dict(ex.get("inputs", {}))
    fails = []
    for st in ex.get("steps", []):
        name = st["name"]
        try:
            got = evaluate(st["formula"], env)
        except Exception as e:
            fails.append("%s.%s: cannot evaluate %r (%s)" % (eid, name, st["formula"], e))
            continue
        env[name] = got
        if "result" in st and not close(got, st["result"], tol):
            fails.append("%s.%s: claimed %s, recomputed %s" % (eid, name, st["result"], got))
        elif not quiet:
            print("OK   %s.%s = %s" % (eid, name, got))
    for i, ck in enumerate(ex.get("checks", [])):
        label = ck.get("label", "check %d" % (i + 1))
        try:
            l, r = evaluate(ck["left"], env), evaluate(ck["right"], env)
        except Exception as e:
            fails.append("%s: %s: cannot evaluate (%s)" % (eid, label, e))
            continue
        if not close(l, r, tol):
            fails.append("%s: %s: %s != %s" % (eid, label, l, r))
        elif not quiet:
            print("OK   %s: %s (%s)" % (eid, label, l))
    return fails


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "examples" in data:
        return data["examples"]
    return data if isinstance(data, list) else [data]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    quiet = "--quiet" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    all_fails = []
    for p in paths:
        for ex in load(p):
            all_fails += check_example(ex, quiet)
    for f in all_fails:
        print("FAIL " + f)
    if all_fails:
        print("%d problem(s). Fix the lesson or the formula, then re-run." % len(all_fails))
        return 1
    print("All numbers verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
