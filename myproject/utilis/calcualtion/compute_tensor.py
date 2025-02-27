import sympy as sp
from ..simplification import custom_simplify
from .indexes import lower_indices
import logging

def oblicz_tensory(wspolrzedne, metryka):
    n = len(wspolrzedne)

    # Tworzenie tensora metrycznego
    g = sp.Matrix(n, n, lambda i, j: metryka.get((i, j), metryka.get((j, i), 0)))
    g_inv = g.inv()

    # Obliczanie symboli Christoffela
    Gamma = [[[0 for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for sigma in range(n):
        for mu in range(n):
            for nu in range(n):
                Gamma_sum = 0
                for lam in range(n):
                    partial_mu  = sp.diff(g[nu, lam], wspolrzedne[mu])
                    partial_nu  = sp.diff(g[mu, lam], wspolrzedne[nu])
                    partial_lam = sp.diff(g[mu, nu], wspolrzedne[lam])
                    Gamma_sum += g_inv[sigma, lam] * (partial_mu + partial_nu - partial_lam)
                Gamma[sigma][mu][nu] = custom_simplify(sp.Rational(1, 2) * Gamma_sum)

    # Obliczanie tensora Riemanna
    Riemann = [[[[0 for _ in range(n)] for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for rho in range(n):
        for sigma in range(n):
            for mu in range(n):
                for nu in range(n):
                    term1 = sp.diff(Gamma[rho][nu][sigma], wspolrzedne[mu])
                    term2 = sp.diff(Gamma[rho][mu][sigma], wspolrzedne[nu])
                    sum_term = 0
                    for lam in range(n):
                        sum_term += (Gamma[rho][mu][lam] * Gamma[lam][nu][sigma]
                                     - Gamma[rho][nu][lam] * Gamma[lam][mu][sigma])
                    Riemann[rho][sigma][mu][nu] = custom_simplify(term1 - term2 + sum_term)

    # Obniżanie indeksów tensora Riemanna
    R_abcd = lower_indices(Riemann, g, n)

    # Obliczanie tensora Ricciego
    Ricci = sp.zeros(n, n)
    for mu in range(n):
        for nu in range(n):
            Ricci[mu, nu] = custom_simplify(sum(Riemann[rho][mu][rho][nu] for rho in range(n)))
            Ricci[mu, nu] = custom_simplify(Ricci[mu, nu])

    # Obliczanie skalarnej krzywizny
    Scalar_Curvature = custom_simplify(sum(g_inv[mu, nu] * Ricci[mu, nu] for mu in range(n) for nu in range(n)))
    Scalar_Curvature = custom_simplify(Scalar_Curvature)

    return g, Gamma, R_abcd, Ricci, Scalar_Curvature

def compute_einstein_tensor(Ricci, Scalar_Curvature, g, g_inv, n):
    G_lower = sp.zeros(n, n)  
    G_upper = sp.zeros(n, n) 
    
    for mu in range(n):
        for nu in range(n):
            G_lower[mu, nu] = custom_simplify(Ricci[mu, nu] - sp.Rational(1, 2) * g[mu, nu] * Scalar_Curvature)

    for mu in range(n):
        for nu in range(n):
            sum_term = 0
            for alpha in range(n):
                sum_term += g_inv[mu, alpha] * G_lower[alpha, nu]
            G_upper[mu, nu] = custom_simplify(sum_term)

    return G_upper, G_lower

def compute_weyl_tensor(R_abcd, Ricci, Scalar_Curvature, g, n):
    """
    Oblicza tensor Weyla C_{rho,sigma,mu,nu} w wymiarze n 
    z danych: R_abcd (Riemann), Ricci (tensor Ricciego),
    Scalar_Curvature (skalar krzywizny) i g (metryka).
    
    Zwraca 4-wymiarową listę C[rho][sigma][mu][nu].
    """
    # Inicjalizacja
    C_abcd = [[[[0 for _ in range(n)] for _ in range(n)] 
                              for _ in range(n)] for _ in range(n)]
    
    # Dla n < 3 tensor Weyla znika
    if n < 3:
        return C_abcd  # same zera

    # Współczynniki z definicji
    factor_1 = 1 / (n - 2)
    factor_2 = 1 / ((n - 1) * (n - 2))

    # Pętla po wszystkich indeksach
    for rho in range(n):
        for sigma in range(n):
            for mu in range(n):
                for nu in range(n):
                    # --- Pierwsza część: Riemann ---
                    term_riemann = R_abcd[rho][sigma][mu][nu]
                    
                    
                    term_2 = factor_1 * (
                        g[rho, mu] * Ricci[nu, sigma]
                        - g[rho, nu] * Ricci[mu, sigma]
                        - g[sigma, mu] * Ricci[nu, rho]
                        + g[sigma, nu] * Ricci[mu, rho]
                    )
                    
                 
                    term_3 = factor_2 * Scalar_Curvature * (
                        g[rho, mu] * g[nu, sigma]
                        - g[rho, nu] * g[mu, sigma]
                        - g[sigma, mu] * g[nu, rho]
                        + g[sigma, nu] * g[mu, rho]
                    ) / 2  # bo w definicji jest [mu nu], czyli 1/2

                    C_val = term_riemann - term_2 + term_3
                    C_abcd[rho][sigma][mu][nu] = custom_simplify(C_val)

    return C_abcd