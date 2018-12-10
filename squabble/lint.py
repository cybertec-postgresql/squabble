""" linting engine """

import pglast


def parse_file(file_name):
    with open(file_name, 'r') as fp:
        contents = fp.read()

    return pglast.Node(pglast.parse_sql(contents))


class Engine:
    def __init__(self, rules):
        self._rules = rules
        self._stack = []
        self._failures = []

    @staticmethod
    def from_config(config, enabled_rules):
        engine = Engine(enabled_rules)
        return engine

    def add_failure(self, failure):
        self._failures.append(failure)

    def lint(self, file_name):
        root_ctx = LintContext(self)

        for rule in self._rules:
            rule.enable(root_ctx)

        ast = parse_file(file_name)
        root_ctx.traverse(ast)

        return self._failures


class LintContext:
    def __init__(self, engine):
        self._hooks = {}
        self._engine = engine

    def traverse(self, parent_node):
        for node in parent_node.traverse():
            # Ignore scalar values
            if not isinstance(node, pglast.node.Node):
                continue

            tag = node.node_tag
            for hook in self._hooks.get(tag, []):
                child_ctx = LintContext(self._engine)
                hook(child_ctx, node)

                # children can set up their own hooks, so recurse
                child_ctx.traverse(node)

        print('done!')

    def register(self, nodes, fn):
        """TODO: write me"""
        for n in nodes:
            if n not in self._hooks:
                self._hooks[n] = []

            self._hooks[n].append(fn)

    def failure(self, msg, node=None, verbose_msg=None):
        self._engine.add_failure({
            'msg': msg,
            'node': node,
            'verbose': verbose_msg
        })
