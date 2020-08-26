from ..util import module_available

if not module_available("torch"):
    raise RuntimeError("Tried importing VampNets; this only works with a PyTorch installation!")
del module_available

import torch
import sktime.decomposition.vampnet as vnet


def gramian_gauss(Y, sigma=1.):
    differences = torch.unsqueeze(Y, -2) - torch.unsqueeze(Y, -3)
    D = torch.sum(torch.pow(differences, 2), dim=-1)
    return torch.exp(-D / (2. * sigma ** 2))


def whiten(X, epsilon=1e-6, mode='clamp'):
    X_meanfree = X - X.mean(dim=0, keepdim=True)
    cov = 1 / (X.shape[0] - 1) * (X_meanfree.t() @ X_meanfree)
    cov_sqrt_inv = vnet.sym_inverse(cov, epsilon=epsilon, mode=mode, return_sqrt=True)
    return X_meanfree @ cov_sqrt_inv


def kvad_score(chi_X, Y, bandwidth=1., epsilon=1e-6, mode='regularize'):
    N = Y.shape[0]

    Gyy = gramian_gauss(Y, bandwidth)
    chi_X_w = whiten(chi_X)
    xGx = torch.chain_matmul(chi_X_w.t(), Gyy, chi_X_w)

    evals, _ = vnet.symeig_reg(xGx, epsilon=epsilon, mode=mode, eigenvectors=False)
    score = 1 / (N * N) * (torch.sum(evals) + torch.sum(Gyy))
    return score
