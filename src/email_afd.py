# email_afd.py
# Tema 6 - E-mail simplificado
#
# Regras do enunciado:
#   - formato usuario@dominio, com exatamente um @
#   - usuário: um ou mais símbolos entre letras, dígitos, ponto e _,
#     sem começar nem terminar com ponto e sem dois pontos seguidos
#   - domínio: dois ou mais rótulos (letras e dígitos) separados por ponto, sem rótulo vazio
#   - o último rótulo tem só letras, com 2 ou 3 letras
#
# O autômato está todo neste arquivo: estados, alfabeto, tabela de transição,
# estado inicial, estados finais e o poço.

from afd import AFD

# Alfabeto (escrito letra por letra)
LETRAS = "abcdefghijklmnopqrstuvwxyz"
DIGITOS = "0123456789"
SIGMA = LETRAS + DIGITOS + "._@"

# Os símbolos de cada grupo fazem a mesma coisa em todos os estados,
# então a tabela é escrita por grupo (igual às setas do diagrama).
GRUPOS = {
    "a-z": LETRAS,
    "0-9": DIGITOS,
    ".": ".",
    "_": "_",
    "@": "@",
}

# Estados e o que cada um significa
ESTADOS = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "qp"]
SIGNIFICADO = {
    "q0": "início, ainda não leu nada",
    "q1": "no usuário, o último símbolo foi letra, dígito ou _ (aqui já pode vir o @)",
    "q2": "no usuário, acabou de ler um ponto (não pode vir ponto nem @)",
    "q3": "acabou de ler o @, domínio ainda vazio",
    "q4": "dentro do 1º rótulo do domínio (ainda não leu ponto no domínio)",
    "q5": "acabou de ler um ponto no domínio, rótulo atual vazio",
    "q6": "rótulo atual (do 2º em diante) com 1 letra",
    "q7": "rótulo atual com 2 letras, pode ser o último (final)",
    "q8": "rótulo atual com 3 letras, pode ser o último (final)",
    "q9": "rótulo atual (do 2º em diante) não pode ser o último: tem dígito ou 4 letras ou mais",
    "qp": "poço (erro), não sai mais daqui",
}
INICIAL = "q0"
FINAIS = {"q7", "q8"}
POCO = "qp"

# Tabela de transição (todas as células preenchidas)
TRANSICOES = {
    #      a-z          0-9          .          _          @
    "q0": {"a-z": "q1", "0-9": "q1", ".": "qp", "_": "q1", "@": "qp"},
    "q1": {"a-z": "q1", "0-9": "q1", ".": "q2", "_": "q1", "@": "q3"},
    "q2": {"a-z": "q1", "0-9": "q1", ".": "qp", "_": "q1", "@": "qp"},
    "q3": {"a-z": "q4", "0-9": "q4", ".": "qp", "_": "qp", "@": "qp"},
    "q4": {"a-z": "q4", "0-9": "q4", ".": "q5", "_": "qp", "@": "qp"},
    "q5": {"a-z": "q6", "0-9": "q9", ".": "qp", "_": "qp", "@": "qp"},
    "q6": {"a-z": "q7", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp"},
    "q7": {"a-z": "q8", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp"},
    "q8": {"a-z": "q9", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp"},
    "q9": {"a-z": "q9", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp"},
    "qp": {"a-z": "qp", "0-9": "qp", ".": "qp", "_": "qp", "@": "qp"},
}

AFD_EMAIL = AFD("e-mail simplificado", ESTADOS, SIGMA, GRUPOS, TRANSICOES,
                INICIAL, FINAIS, POCO, SIGNIFICADO)


# Variante do "para ir além": hífen nos rótulos do domínio, mas nunca no
# começo nem no fim de um rótulo. O que muda em relação ao AFD de cima:
#   - o alfabeto ganha '-' (uma coluna nova)
#   - dois estados novos, q10 e q11 (o rótulo terminou em hífen até agora)
#   - q4 vai para q10 com '-'; q6, q7, q8 e q9 vão para q11 com '-'
# Um rótulo com hífen nunca pode ser o último (o último só tem letras),
# por isso q11 volta para q9.
SIGMA_HIFEN = SIGMA + "-"
GRUPOS_HIFEN = dict(GRUPOS)
GRUPOS_HIFEN["-"] = "-"
ESTADOS_HIFEN = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "qp"]
SIGNIFICADO_HIFEN = dict(SIGNIFICADO)
SIGNIFICADO_HIFEN["q10"] = "no 1º rótulo do domínio, o último símbolo foi hífen"
SIGNIFICADO_HIFEN["q11"] = "num rótulo do 2º em diante, o último símbolo foi hífen"

TRANSICOES_HIFEN = {
    #       a-z          0-9          .          _          @          -
    "q0":  {"a-z": "q1", "0-9": "q1", ".": "qp", "_": "q1", "@": "qp", "-": "qp"},
    "q1":  {"a-z": "q1", "0-9": "q1", ".": "q2", "_": "q1", "@": "q3", "-": "qp"},
    "q2":  {"a-z": "q1", "0-9": "q1", ".": "qp", "_": "q1", "@": "qp", "-": "qp"},
    "q3":  {"a-z": "q4", "0-9": "q4", ".": "qp", "_": "qp", "@": "qp", "-": "qp"},
    "q4":  {"a-z": "q4", "0-9": "q4", ".": "q5", "_": "qp", "@": "qp", "-": "q10"},  # mudou
    "q5":  {"a-z": "q6", "0-9": "q9", ".": "qp", "_": "qp", "@": "qp", "-": "qp"},
    "q6":  {"a-z": "q7", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp", "-": "q11"},  # mudou
    "q7":  {"a-z": "q8", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp", "-": "q11"},  # mudou
    "q8":  {"a-z": "q9", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp", "-": "q11"},  # mudou
    "q9":  {"a-z": "q9", "0-9": "q9", ".": "q5", "_": "qp", "@": "qp", "-": "q11"},  # mudou
    "q10": {"a-z": "q4", "0-9": "q4", ".": "qp", "_": "qp", "@": "qp", "-": "q10"},  # novo
    "q11": {"a-z": "q9", "0-9": "q9", ".": "qp", "_": "qp", "@": "qp", "-": "q11"},  # novo
    "qp":  {"a-z": "qp", "0-9": "qp", ".": "qp", "_": "qp", "@": "qp", "-": "qp"},
}

AFD_EMAIL_HIFEN = AFD("e-mail com hífen", ESTADOS_HIFEN, SIGMA_HIFEN, GRUPOS_HIFEN,
                      TRANSICOES_HIFEN, INICIAL, FINAIS, POCO, SIGNIFICADO_HIFEN)


# Motivo da rejeição. Quem decide aceitar ou rejeitar é o autômato; isto aqui
# só olha em que estado ele parou (ou de onde caiu no poço) e escreve o porquê.

# (estado de onde saiu, grupo do símbolo) -> motivo de ter ido para o poço
MOTIVO_POCO = {
    ("q0", "."): "o usuário não pode começar com ponto",
    ("q0", "@"): "o usuário não pode ser vazio",
    ("q2", "."): "o usuário não pode ter dois pontos seguidos",
    ("q2", "@"): "o usuário não pode terminar com ponto",
    ("q3", "."): "o domínio não pode começar com ponto",
    ("q5", "."): "dois pontos seguidos no domínio (rótulo vazio)",
    ("q3", "-"): "rótulo do domínio não pode começar com hífen",
    ("q5", "-"): "rótulo do domínio não pode começar com hífen",
    ("q10", "."): "rótulo do domínio não pode terminar com hífen",
    ("q11", "."): "rótulo do domínio não pode terminar com hífen",
}

# estado não final onde a palavra acabou -> motivo
MOTIVO_FIM = {
    "q0": "palavra vazia",
    "q1": "falta o @ e o domínio",
    "q2": "falta o @ e o domínio, e o usuário não pode terminar com ponto",
    "q3": "domínio vazio",
    "q4": "o domínio precisa ter pelo menos dois rótulos separados por ponto",
    "q5": "não pode terminar com ponto (último rótulo vazio)",
    "q6": "o último rótulo tem só 1 letra (precisa de 2 ou 3)",
    "q9": "o último rótulo precisa ter só letras, 2 ou 3",
    "q10": "rótulo do domínio não pode terminar com hífen",
    "q11": "rótulo do domínio não pode terminar com hífen",
}


def explicar(afd, r):
    if r.aceita:
        return ""
    if r.pos_poco is None:
        return MOTIVO_FIM.get(r.estado_final(), "terminou num estado que não é final")

    i = r.pos_poco
    s = r.palavra[i]
    q = r.caminho[i]   # estado antes de ler o símbolo que levou ao poço
    onde = " (símbolo %r na posição %d, saindo de %s)" % (s, i + 1, q)
    grupo = afd.grupo_do_simbolo(s)
    if grupo is None:
        return "o símbolo %r não está no alfabeto (posição %d)" % (s, i + 1)
    if (q, grupo) in MOTIVO_POCO:
        return MOTIVO_POCO[(q, grupo)] + onde
    if grupo == "@":
        return "o e-mail tem que ter exatamente um @" + onde
    if grupo == "_":
        return "não pode ter _ no domínio" + onde
    if grupo == "-":
        return "hífen só é permitido no domínio" + onde
    return "transição para o poço" + onde
