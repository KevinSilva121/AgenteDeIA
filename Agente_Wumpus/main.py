"""
Executa uma simulacao do Agente Wumpus.

Modos de uso:

  1) Mundo aleatorio reproduzivel (semente):
     python main.py --semente 42

  2) Mundo aleatorio com probabilidade de poco diferente:
     python main.py --semente 7 --prob-poco 0.15

  3) Mundo manual (voce escolhe as posicoes):
     python main.py --wumpus 3,3 --ouro 4,4 --pocos "2,1;3,2;4,3"

  4) Misto - posicoes fixas + sorteio dos pocos:
     python main.py --wumpus 2,3 --ouro 4,4 --semente 5

Coordenadas: x = coluna (1..4), y = linha (1..4). [1,1] e o canto inferior esquerdo.
"""

import argparse

from agente import AgenteWumpus
from mundo_wumpus import MundoWumpus


def parse_celula(texto):
    """Converte uma string 'x,y' em uma tupla (x,y)."""
    try:
        partes = texto.replace(" ", "").split(",")
        if len(partes) != 2:
            raise ValueError
        return (int(partes[0]), int(partes[1]))
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Formato invalido: {texto!r}. Use 'x,y' (ex: 3,2)."
        )


def parse_pocos(texto):
    """Converte 'x1,y1;x2,y2;...' em uma lista de tuplas."""
    if not texto:
        return []
    celulas = []
    for parte in texto.split(";"):
        parte = parte.strip()
        if parte:
            celulas.append(parse_celula(parte))
    return celulas


def main():
    parser = argparse.ArgumentParser(
        description="Agente Wumpus baseado em conhecimento.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--semente", type=int, default=42,
                        help="Semente para reproduzir o mundo aleatorio (default: 42).")
    parser.add_argument("--prob-poco", type=float, default=0.2,
                        help="Probabilidade de poco em cada celula (default: 0.2). "
                             "Ignorado se --pocos for usado.")
    parser.add_argument("--wumpus", type=parse_celula, default=None,
                        help="Posicao manual do Wumpus, formato 'x,y' (ex: 3,3).")
    parser.add_argument("--ouro", type=parse_celula, default=None,
                        help="Posicao manual do Ouro, formato 'x,y' (ex: 4,4).")
    parser.add_argument("--pocos", type=parse_pocos, default=None,
                        help='Posicoes manuais dos Pocos, separadas por ";". '
                             'Ex: "2,1;3,2;4,3". Use "" para mundo sem pocos.')
    parser.add_argument("--silencioso", action="store_true",
                        help="Nao imprime o raciocinio passo a passo.")
    args = parser.parse_args()

    mundo = MundoWumpus(
        semente=args.semente,
        prob_poco=args.prob_poco,
        wumpus=args.wumpus,
        ouro=args.ouro,
        pocos=args.pocos,
    )

    print(f"Mundo configurado:")
    print(f"  Wumpus em: {mundo.wumpus}"
          f"{'  (manual)' if args.wumpus is not None else '  (sorteado)'}")
    print(f"  Ouro em:   {mundo.ouro}"
          f"{'  (manual)' if args.ouro is not None else '  (sorteado)'}")
    print(f"  Pocos em:  {sorted(mundo.pocos)}"
          f"{'  (manual)' if args.pocos is not None else '  (sorteado)'}")
    mundo.imprimir_mapa(agente_pos=(1, 1), revelar=True)

    agente = AgenteWumpus(mundo, verbose=not args.silencioso)
    venceu = agente.jogar()

    print()
    print("=" * 50)
    if venceu:
        print(f"VITORIA! O agente saiu de [1,1] com o ouro em {agente.passos} passos.")
    elif not agente.vivo:
        print(f"DERROTA! O agente morreu em {agente.posicao} no passo {agente.passos}.")
    elif agente.tem_ouro:
        print("Agente pegou o ouro mas nao conseguiu provar caminho seguro de volta.")
    else:
        print("Agente parou sem encontrar caminho seguro para o ouro.")
    print("=" * 50)


if __name__ == "__main__":
    main()
