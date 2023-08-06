import numpy as np

def col_norm_eigh(S):
    """
    Calculate the eigenvalues, eigenvectors, and inverse eigenvectors of a column-normalized matrix, pre-normalization.
    :param S: A symmetric matrix, pre-normalization.
    :return: The eigenvalues, eigenvectors, and inverse eigenvectors of the post-normalized matrix.
    """
    D = 1 / S.sum(axis=0)
    D_sqrt = np.sqrt(D)

    # Q is similar to S*D, and symmetric
    Q = D_sqrt[:,np.newaxis] * S * D_sqrt
    q_eigs, q_vecs = np.linalg.eigh(Q)
    
    P = 1 / D_sqrt
    return q_eigs, P[:,np.newaxis] * q_vecs, q_vecs.T * D_sqrt


def compute_similarities(f_adj, g_adj, sim_matrix, add_self_loops=True, decay=0.6):
    """
    Compute the similarities between the nodes of two undirected graphs using vanilla SimRank.
    :param f_adj: The adjacency matrix of the first graph.
    :param g_adj: The adjacency matrix of the second graph.
    :param sim_matrix: The initial similarity matrix.
    :param add_self_loops: Whether self-loops should be added to the adjacency matrices.
    :param decay: The decay factor.
    """
    if add_self_loops:
        np.fill_diagonal(f_adj, 1)
        np.fill_diagonal(g_adj, 1)
    
    # make sure the graphs are undirected
    f_adj = np.clip(f_adj + f_adj.T, 0, 1)
    g_adj = np.clip(g_adj + g_adj.T, 0, 1)

    f_eigs, f_vecs, f_vecs_inv = col_norm_eigh(f_adj.T)
    g_eigs, g_vecs, g_vecs_inv = col_norm_eigh(g_adj)

    R = decay * (f_eigs[:,np.newaxis] @ g_eigs[np.newaxis,:]) 
    A = f_vecs_inv @ sim_matrix @ g_vecs

    result = f_vecs @ (A / (1 - R)) @ g_vecs_inv
    return result.real
