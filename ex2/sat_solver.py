# importing system module for reading files
import itertools
import sys


# in what follows, a formula is a collection of clauses,
# a clause is a collection of literals,
# and a literal is a non-zero integer.

# input path:  a path to a cnf file
# output: the formula represented by the file,
#         the number of variables,
#         and the number of clauses
def parse_dimacs_path(_path):
    cnf = []
    _num_vars = 0
    _num_clauses = 0
    with open(_path, 'r') as file:
        for line in file:
            line_tokens = line.strip().split()
            if len(line_tokens) > 0:
                if line_tokens[0] == 'p':
                    _num_vars = int(line_tokens[2])
                    _num_clauses = int(line_tokens[3])
                else:
                    clause = [int(literal) for literal in line_tokens[:-1]]
                    cnf.append(clause)
    return cnf, _num_vars, _num_clauses


# input cnf: a formula
# input n_vars: the number of variables in the formula
# input n_clauses: the number of clauses in the formula
# output: True if cnf is satisfiable, False otherwise
def naive_solve(cnf, n_vars):
    literals = set()
    for clause in cnf:
        for literal in clause:
            literals.add(abs(literal))
    literals = list(literals)
    truth_table = itertools.product([True, False], repeat=n_vars)
    for line in truth_table:
        unsat_cnf = False
        assignment = dict(zip(literals, line))
        for clause in cnf:
            unsat_clause = True
            for literal in clause:
                if assignment[abs(literal)] == (literal > 0):
                    unsat_clause = False
                    break
            if unsat_clause:
                unsat_cnf = True
                break
        if not unsat_cnf:
            return True
    return False


# input cnf: a formula
# input n_vars: the number of variables in the formula
# input n_clauses: the number of clauses in the formula
# output: True if cnf is satisfiable, False otherwise
def dpll_solve(cnf):
    return dpll(cnf, [])


def dpll(cnf, assignment):
    if len(cnf) == 0:
        return True

    if any([len(clause) == 0 for clause in cnf]):
        return False

    cnf, pure_assign = pure_literal(cnf)
    assignment += pure_assign

    cnf, unit_assign = unit_propagation(cnf)
    assignment += unit_assign

    if cnf is False:
        return False
    if len(cnf) == 0:
        return True
    if any([len(clause) == 0 for clause in cnf]):
        return False

    var = decide(cnf)
    cnf = update_cnf(cnf, var)
    assignment += [var]
    result = dpll(cnf, assignment)
    if result is False:
        result = backtrack(cnf, assignment, var)
    return result


def decide(cnf):
    return get_literals_list(cnf)[0]


def backtrack(cnf, assignment, var):
    cnf = update_cnf(cnf, -var)
    assignment += [-var]
    return dpll(cnf, assignment)


def unit_propagation(cnf):
    assignment = []
    unit_clauses = get_unit_clauses(cnf)

    while unit_clauses:
        unit = unit_clauses[0][0]
        cnf = update_cnf(cnf, unit)
        assignment.append(unit)

        if cnf is False:
            return False, []

        if not cnf:
            return cnf, assignment

        unit_clauses = get_unit_clauses(cnf)

    return cnf, assignment


def update_cnf(cnf, assigned_literal):
    new_cnf = []
    for clause in cnf:
        if -assigned_literal in clause:
            new_clause = []
            for literal in clause:
                if literal != -assigned_literal:
                    new_clause.append(literal)
            if len(new_clause) == 0:
                return False
            new_cnf.append(new_clause)

        if assigned_literal in clause:
            continue

        else:
            new_cnf.append(clause)

    return new_cnf


def get_literals_list(cnf):
    return list(set(number for sublist in cnf for number in sublist))


def pure_literal(cnf):
    literals_list = get_literals_list(cnf)
    pure_literals = [literal for literal in literals_list if -literal not in literals_list]
    cnf = [clause for clause in cnf if not any(literal in clause for literal in pure_literals)]
    return cnf, pure_literals


def get_unit_clauses(cnf):
    unit_clauses = []
    for clause in cnf:
        if len(clause) == 1:
            unit_clauses.append(clause)
    return unit_clauses


######################################################################

# get path to cnf file from the command line
path = sys.argv[1]

# get algorithm from the command line
algorithm = sys.argv[2]

# make sure that algorithm is either "naive" or "dpll"
assert (algorithm in ["naive", "dpll"])

# parse the file
cnf_formula, num_vars, num_clauses = parse_dimacs_path(path)

# check satisfiability based on the chosen algorithm
# and print the result
if algorithm == "naive":
    print("sat" if naive_solve(cnf_formula, num_vars) else "unsat")
else:
    print("sat" if dpll_solve(cnf_formula) else "unsat")
