from os import walk
from os.path import join
from parso import parse


def _visit_node(node, visitor, kwargs):
    if hasattr(node, 'children'):
        if visitor(node=node, **kwargs) is not False:
            for c in node.children:
                _visit_node(node=c, visitor=visitor, kwargs=kwargs)

missing = object()

def walk_code(visitor, dir='.', skip_dirs=missing, **kwargs):
    if skip_dirs is missing:
        skip_dirs = {'env3', 'venv', 'venv3', 'node_modules', '.git'}

    for root, dirs, files in walk(dir):
        if skip_dirs:
            dirs[:] = [x for x in dirs if x not in skip_dirs]

        for filename in files:
            if filename.endswith('.py'):
                full_path = join(root, filename)
                with open(full_path) as f:
                    contents = f.read()

                lines = contents.split('\n')

                ast = parse(contents)
                _visit_node(node=ast, visitor=visitor, kwargs=dict(full_path=full_path, contents=contents, lines=lines, **kwargs))

def is_function_call(node):
    return node.type == 'atom_expr' and node.children[-1].children[0].value == '('

def full_function_name(node):
    assert node.type == 'atom_expr'
    if node.children[0].type != 'name':
        # this is a call onto a literal, like {'foo'}.get('bar'}, or "foo".bar()
        return None
    return '.'.join([node.children[0].value] + [x.children[1].value for x in node.children[1:] if x.children[0].value == '.'])


def function_call_arguments(node):
    assert node.type == 'atom_expr'

    positional = []
    kwargs = {}
    arg_unpacks = []
    kwarg_unpacks = []

    def parse_argument(arg):
        if arg.type != 'argument':
            positional.append(arg)
        else:
            if arg.children[0].type == 'operator':
                if arg.children[0].value == '*':
                    arg_unpacks.append(arg)
                else:
                    assert arg.children[0].value == '**'
                    kwarg_unpacks.append(arg)
            else:
                kwargs[arg.children[0].value] = arg.children[2]

    arg_or_args = node.children[-1].children[1]
    if arg_or_args.type == 'arglist':
        args = [x for x in arg_or_args.children if x.type != 'operator']

        for arg in args:
            parse_argument(arg)
    else:
        parse_argument(arg_or_args)

    return dict(
        positional=positional,
        kwargs=kwargs,
        arg_unpacks=arg_unpacks,
        kwarg_unpacks=kwarg_unpacks,
    )
