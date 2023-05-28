"""
Module dedicated to create directed acyclic graphs
"""
import random as rd
import numpy as np


def is_valid(mat):
    """
    Function that checks wether a matrix is valid to be used as a dag
    """
    return (
        np.count_nonzero(mat, axis=0).max() <= 2
        and np.count_nonzero(mat, axis=1)[:-1].min() >= 1
    )


def generate_list(dim_list):
    """
    Function that returns a list of
    """
    # contar en binario de 0 hasta 2^(dim_list) -1
    for number in range(2**dim_list):  # EXPONENTIAL WARNING
        bin_str = bin(number)[2:].rjust(int(dim_list), "0")
        yield number, list(bin_str)


def generate_matrix(dim: float, tries_limit):
    """
    Function
    """
    # vector de dim 1+2+...+(dim-1) = (dim-1)*dim/2
    dim_list = int((dim - 1) * dim / 2)
    list_generator = generate_list(dim_list)
    tries = 0
    for id_list, filled_list in list_generator:
        counter = 0
        mat = np.zeros([dim, dim], dtype=int)
        for i in range(0, dim - 1):
            for j in range(i + 1, dim):
                mat[i, j] = filled_list[counter]
                counter += 1
        if is_valid(mat):
            tries += 1
            yield id_list, mat
        if tries >= tries_limit:
            break


def generate_random_matrix(dim: int):
    """
    Function
    """
    matrix = np.zeros([dim, dim], dtype=int)
    valid = False
    while not valid:
        for i in range(dim - 1):
            rnd_i = rd.sample(range(i + 1, dim), 1)
            matrix[i, rnd_i] = 1
        if is_valid(matrix):
            valid = True
    return matrix


def generate_trivial_matrix(dim: int):
    """
    Solo tendrá 1 predicado y los operadores serán unitarios y anidados
    """
    matrix = np.zeros([dim, dim], dtype=int)
    for i in range(dim - 1):
        matrix[i, i + 1] = 1
    return matrix


def matrix2graph(mat):
    """
    Function
    """
    nodes = [
        (0, 0),
    ]
    for j in range(1, mat.shape[1]):
        aux = np.argwhere(mat[:, j] == 1)
        if len(aux) == 0:
            nodes.append((0, 0))
        elif len(aux) == 1:
            nodes.append((0, *aux[0] + 1))
        elif len(aux) == 2:
            nodes.append((*aux[0] + 1, *aux[1] + 1))
    return nodes


def precompute_dags(max_nodes=10, tries_limit=500):
    """
    Function
    """
    valid_dags = dict()
    for n_nodes in range(2, max_nodes + 1):
        dags_generator = generate_dag(n_nodes, tries_limit)
        valid_dags[n_nodes] = dict()
        for dag_id, dag in dags_generator:
            print(f"Check {n_nodes} nodes, id: {dag_id}")
            valid_dags[n_nodes][dag_id] = dag
    return valid_dags


def generate_dag(dim: int, tries_limit=500):
    """
    Function
    """
    input(f"Generating dag: dim = {dim}")
    matrix_generator = generate_matrix(dim, tries_limit)
    for id_mat, mat in matrix_generator:
        input(f"Generating dag dim {dim} with id: {id_mat}")
        yield id_mat, matrix2graph(mat)


if __name__ == "__main__":
    L = 8  # -> va a estar haciendo 268.435.456 dags

    gen_mats = generate_dag(L)
    for m in gen_mats:
        print(m)

    # dags = precompute_dags(L)

    # with open(f"dags_to_{L}.pickle", "wb") as handle:
    #     pickle.dump(dags, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open(f"dags_to_{L}.pickle", "rb") as handle:
    #     print("cargado:\n", pickle.load(handle))
