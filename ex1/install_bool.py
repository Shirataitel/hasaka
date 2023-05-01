import sys
from pysmt.shortcuts import Solver, And, Or, Not, BOOL, Symbol, TRUE

solver = Solver(name="z3")
symbols_set = set()


def read_file(file):
    with open(file) as f:
        text = f.read()
    lines = text.split("\n\n")
    install_line = lines[-1]
    blocks_lines = lines[:-1]
    return install_line, blocks_lines


def create_sat(install_line, blocks_lines):
    install_line = install_line.split(":")
    install_list = install_line[1].split(",")
    install_list_strip = list(map(str.strip, install_list))
    install_vars = []
    for item in install_list_strip:
        symbol = [Symbol(item, BOOL)]
        install_vars += symbol
        symbols_set.update(symbol)
    solver.add_assertion(And(install_vars))
    blocks_vars = []
    for block in blocks_lines:
        block_data = block.split("\n")
        and_list = []
        pack_sym = None
        for data in block_data:
            data_items = data.split(":")
            title = data_items[0].strip()
            if title == 'Package':
                package_name = data_items[1].strip()
                pack_sym = Symbol(package_name, BOOL)
                symbols_set.update([pack_sym])
            elif title == "Depends":
                data_clouses = data_items[1].split(",")
                or_list = []
                for clouse in data_clouses:
                    symbol_list = []
                    split_clouse = clouse.split("|")
                    for var in split_clouse:
                        symbol = [Symbol(var.strip(), BOOL)]
                        symbols_set.update(symbol)
                        symbol_list += symbol
                    or_list += [Or(symbol_list)]
                and_list += [And(or_list)]
            elif title == "Conflicts":
                data_clouses = data_items[1].split(",")
                or_list = []
                for clouse in data_clouses:
                    symbol_list = []
                    split_clouse = clouse.split("|")
                    for var in split_clouse:
                        symbol_list += [Not(Symbol(var.strip(), BOOL))]
                    or_list += [Or(symbol_list)]
                and_list += [And(or_list)]
        blocks_vars += [Or(Not(pack_sym), And(and_list))]
    solver.add_assertion(And(blocks_vars))


def print_answer():
    if solver.solve():
        print("There is an installation plan:")
        for symbol in symbols_set:
            if solver.get_value(symbol).is_true():
                print(symbol)
    else:
        print("There is no installation plan")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit(-1)
    file = sys.argv[1]
    install, blocks = read_file(file)
    create_sat(install, blocks)
    print_answer()
