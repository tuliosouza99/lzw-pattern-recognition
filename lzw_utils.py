'''
Funções auxiliares para escrita e leitura dos arquivos binários comprimidos.
'''

import numpy as np
import os


def write_compressed(compressed: list, k: int, out_path: str):
    bin_format = {
        9: "{i:09b}",
        10: "{i:010b}",
        11: "{i:011b}",
        12: "{i:012b}",
        13: "{i:013b}",
        14: "{i:014b}",
        15: "{i:015b}",
        16: "{i:016b}",
    }
    # Conversão de int para bin de tamanho k
    compressed_bin = [bin_format[k].format(i=i) for i in compressed]
    len_compressed_bin = k * len(compressed_bin)

    # Na conversão de K bits para 1 byte, pode ser necessário
    # preencher com zeros o último byte da mensagem
    pad_size = 0
    pad = len_compressed_bin % 8
    if pad:
        # Calcula o tamanho correto da bitstring
        # e preenche a diferença com zeros
        possible_len = list(range(len_compressed_bin - 8, len_compressed_bin + 8))
        len_bitstring = max(list(filter(lambda x: (x % 8 == 0), possible_len)))
        pad_size = len_bitstring - len_compressed_bin
        compressed_bin.append("0" * pad_size)

    compressed_bitstring = "".join(compressed_bin)  # converte de list para string

    # Transforma de bitstring para sequência de bytes
    compressed_bytes = [
        int(compressed_bitstring[i : i + 8], 2)
        for i in range(0, len(compressed_bitstring), 8)
    ]
    # Primeiro byte informa a quantidade de bits preenchidos
    compressed_bytes.insert(0, pad_size)

    out_dir = out_path.rsplit("/", maxsplit=1)[0]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(out_path, mode="wb") as output:
        output.write(bytes(compressed_bytes))


def read_compressed(compressed_path: str, k: int):
    with open(compressed_path, mode="rb") as file:
        compressed = file.read()

    # Conversão de bytes para lista de ints
    compressed = list(np.frombuffer(compressed, dtype=np.uint8))
    # Retorna o tamanho do preenchimento no primeiro byte
    pad_size = compressed.pop(0)
    # Conversão de int para binário de tamanho 8
    compressed_8bin = ["{i:08b}".format(i=i) for i in compressed]
    # Conversão para bitstring
    compressed_bitstring = "".join(compressed_8bin)
    # Remove os bits de preenchimento
    if pad_size:
        compressed_bitstring = compressed_bitstring[: -int(pad_size)]
    # Conversão de bitstring para lista de
    # binários de tamanho K para lista de ints
    compressed_Kbin = [
        int(compressed_bitstring[i : i + k], 2)
        for i in range(0, len(compressed_bitstring), k)
    ]

    return compressed_Kbin