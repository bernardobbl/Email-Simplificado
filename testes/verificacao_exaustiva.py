# verificacao_exaustiva.py - teste a mais (não é pedido no enunciado)
#
# Compara o AFD com outra implementação das mesmas regras, feita de um jeito
# diferente (com if e fatiamento de string). Essa segunda versão só existe aqui
# nos testes para conferir o autômato; o programa de verdade (src/) só usa o AFD.
#
# 1) testa TODAS as palavras de tamanho 0 a N com os símbolos a, 1, ., _, @ e A
#    (o A representa um símbolo fora do alfabeto)
# 2) testa 200 mil palavras aleatórias, várias delas parecidas com e-mail
#
#   python testes/verificacao_exaustiva.py       (N = 7, umas 330 mil palavras)
#   python testes/verificacao_exaustiva.py 8     (N = 8, uns 2 milhões, demora mais)

import itertools
import os
import random
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PASTA, "..", "src"))
from email_afd import AFD_EMAIL, LETRAS, DIGITOS

USUARIO_OK = set(LETRAS + DIGITOS + "._")
ROTULO_OK = set(LETRAS + DIGITOS)


def regras(w):
    # as regras do enunciado escritas direto, sem autômato
    if w.count("@") != 1:
        return False
    k = w.index("@")
    usuario = w[:k]
    dominio = w[k + 1:]
    if usuario == "":
        return False
    for c in usuario:
        if c not in USUARIO_OK:
            return False
    if usuario[0] == "." or usuario[-1] == "." or ".." in usuario:
        return False
    rotulos = [""]
    for c in dominio:
        if c == ".":
            rotulos.append("")
        else:
            rotulos[-1] += c
    if len(rotulos) < 2:
        return False
    for r in rotulos:
        if r == "":
            return False
        for c in r:
            if c not in ROTULO_OK:
                return False
    ultimo = rotulos[-1]
    if len(ultimo) < 2 or len(ultimo) > 3:
        return False
    for c in ultimo:
        if c not in LETRAS:
            return False
    return True


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    minimo = AFD_EMAIL.minimizar()[0]

    total = aceitas = 0
    for tam in range(n + 1):
        for t in itertools.product("a1._@A", repeat=tam):
            w = "".join(t)
            esperado = regras(w)
            if AFD_EMAIL.aceita(w) != esperado or minimo.aceita(w) != esperado:
                print("DIFERENÇA em %r: regras=%s, AFD=%s" % (w, esperado, AFD_EMAIL.aceita(w)))
                sys.exit(1)
            total += 1
            if esperado:
                aceitas += 1
    print("Todas as palavras de tamanho 0 a %d: %d testadas, %d aceitas, nenhuma diferença."
          % (n, total, aceitas))

    rnd = random.Random(2026)
    simbolos = list(LETRAS) * 3 + list(DIGITOS) + [".", ".", "_", "@", "@", "-", "A", " "]
    total = aceitas = 0
    for _ in range(200000):
        if rnd.random() < 0.5:
            w = "".join(rnd.choice(simbolos) for _ in range(rnd.randint(0, 30)))
        else:
            w = (rnd.choice(["joao", "a.b", "_x", "a..b", ".a", ""]) + "@" +
                 rnd.choice(["mail", "uni.edu", "x1", "", "a."]) + "." +
                 rnd.choice(["br", "com", "c", "info", "c0m", "io", ""]))
        esperado = regras(w)
        if AFD_EMAIL.aceita(w) != esperado or minimo.aceita(w) != esperado:
            print("DIFERENÇA em %r" % w)
            sys.exit(1)
        total += 1
        if esperado:
            aceitas += 1
    print("Palavras aleatórias: %d testadas, %d aceitas, nenhuma diferença." % (total, aceitas))


if __name__ == "__main__":
    main()
