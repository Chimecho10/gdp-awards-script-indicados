import random

def count_votes(votes, nome):
    if nome in votes:
        votes[nome] += 1
    else:
        votes[nome] = 1

def define_removable(column, nominees):
    min_votes = min(name[1] for name in nominees[column])
    to_remove = []
    for name in nominees[column]:
        if name[1] == min_votes:
            to_remove.append(name)
    return to_remove

def treat_nominees(column, nominees, num_nods):
    while len(nominees[column]) > num_nods:
        to_remove = define_removable(column, nominees)
        element_to_delete = random.choice(to_remove)
        nominees[column].remove(element_to_delete)

def treat_nominees_no_limit(column, nominees, num_nods):
    while len(nominees[column]) > num_nods:
        to_remove = define_removable(column, nominees)
        element_to_delete = random.choice(to_remove)
        nominees[column].remove(element_to_delete)