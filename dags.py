import random as rd
import numpy as np
import pickle

def is_valid(mat):
    return (
        np.count_nonzero(mat, axis=0).max() <= 2
        and np.count_nonzero(mat, axis=1)[:-1].min() >= 1
    )


def generate_list(dim_list, tries_limit):
    # contar en binario de 0 hasta 2^(dim_list) -1
    for n in range(2**dim_list):
        bin_str = bin(n)[2:]
        bin_str = bin_str.rjust(int(dim_list), "0")
        yield n, list(bin_str)



def generate_matrix(d: float, tries_limit):
    # vector de dim 1+2+...+(d-1) = (d-1)*d/2
    dim_list = int((d - 1) * d / 2)
    list_generator = generate_list(dim_list, tries_limit)
    tries = 0
    for id_list, filled_list in list_generator:
        c = 0
        mat = np.zeros([d, d], dtype=int)
        for i in range(0, d - 1):
            for j in range(i + 1, d):
                mat[i, j] = filled_list[c]
                c += 1
        if is_valid(mat):
            tries += 1
            print(f"van {tries} intentos validos de {min(tries_limit, 2**dim_list)} para {d} nodos")
            yield id_list, mat
        if tries >= tries_limit:
            break


def generate_random_matrix(d: int):
    m = np.zeros([d, d], dtype=int)
    valid = False
    while not valid:
        for i in range(d - 1):
            rnd_i = rd.sample(range(i + 1, d), 1)
            m[i, rnd_i] = 1
        if is_valid(m):
            valid = True
    return m


def generate_trivial_matrix(d: int):
    """
    Solo tendrá 1 predicado y los operadores serán unitarios y anidados
    """
    m = np.zeros([d, d], dtype=int)
    for i in range(d - 1):
        m[i, i + 1] = 1
    return m


def matrix2graph(mat):
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


def generate_dag(d: int, tries_limit = 500):
    matrix_generator = generate_matrix(d, tries_limit)
    for id_mat, mat in matrix_generator:
        yield id_mat, matrix2graph(mat)

def precompute_dags(max_nodes = 10, tries_limit = 500):
    valid_dags = dict()
    for n_nodes in range(2, max_nodes+1):
        dags_generator = generate_dag(n_nodes, tries_limit)
        valid_dags[n_nodes] = dict()
        for dag_id, dag in dags_generator:
            print(f"Check {n_nodes} nodes, id: {dag_id}")
            valid_dags[n_nodes][dag_id] = dag
    return valid_dags


if __name__ == "__main__":
    L = 8 # -> va a estar haciendo 268.435.456 dags 

    gen_mats = generate_dag(L)
    for m in gen_mats:
        print(m)

    # dags = precompute_dags(L)

    # with open(f"dags_to_{L}.pickle", "wb") as handle:
    #     pickle.dump(dags, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open(f"dags_to_{L}.pickle", "rb") as handle:
    #     print("cargado:\n", pickle.load(handle)) 