'''
Compressão e descompressão utilizando o algoritmo LZW.
'''

from utils.lzw_utils import write_compressed, read_compressed


def compress(file_path: str, k: int, dictionary: dict, out_path=None,
             is_training=False, is_testing=False, is_PGM=False) -> dict:
    """
    Comprime um arquivo utilizando o algoritmo LZW. K é utilizado
    para especificar o tamanho máximo do dicionário. A saída é um arquivo com
    a mensagem comprimida.

    O dicionário segue o seguinte formato:
    - key: tupla de símbolos
    - value: índice do dicionário

    Como a saída do compressor deve ser apenas os índices do dicionário,
    foi escolhido o formato acima para facilitar o acesso aos índices.
    Isso porque dicionários em Python permitem acessar um value através de uma
    key, mas não permitem acessar uma key através de um value.

    A conversão de lista para tupla foi feita unicamente com propósitos de
    indexação, pois o Python não permite passar uma lista como key de um dicionário.
    """

    if is_training and is_testing:
        raise Exception("Não é possível treinar e testar o modelo ao mesmo tempo.")

    with open(file_path, mode="rb") as file:
        if is_PGM:
            for i in range(3): next(file)
        msg = file.read()

    if len(dictionary) == 0:
        dictionary = {tuple([i]): i for i in range(256)}

    max_dict_size = 2 ** k

    seq = []  # Sequência atual
    compressed = []  # Mensagem comprimida

    for byte in msg:
        pair = seq.copy()
        pair.append(byte)  # Par sequência atual + próximo símbolo

        # Caso o par já exista no dicionário, adiciona o byte
        # lido à sequência atual e vai para a próxima iteração
        if tuple(pair) in dictionary:
            seq = pair.copy()
        else:
            compressed.append(dictionary[tuple(seq)])

            # Adiciona o par sequência atual + símbolo seguinte
            # no dicionário caso o tamanho máximo não tenha sido atingido
            if len(dictionary) < max_dict_size and not is_testing:
                dictionary[tuple(pair)] = len(dictionary)

            # Como o índice da sequência atual já foi colocado na saída,
            # atualiza ela para ser apenas o byte lido
            seq = [byte]

    # Se ao final das iterações ainda houver itens na sequência atual,
    # adiciona o índice a saída
    if seq:
        compressed.append(dictionary[tuple(seq)])

    if is_training:
        return dictionary

    write_compressed(compressed, k, out_path)


def decompress(compressed_path: str, k: int, out_path: str):
    """
    Descomprime um arquivo utilizando o algoritmo LZW. K é utilizado
    para especificar o tamanho máximo do dicionário. A saída é um arquivo com
    a mensagem descomprimida.

    O dicionário segue o seguinte formato:
    - key: índice do dicionário
    - value: lista de símbolos

    O dicionário segue um formato inverso ao do compressor, pois agora queremos
    descobrir os símbolos através de um índice do dicionário, e não o contrário.
    """
    print("Lendo arquivo comprimido...")
    compressed = read_compressed(compressed_path, k)
    print("Arquivo comprimido lido com sucesso!")
    print("Descomprimindo a mensagem...")

    # Dicionário inicial
    dictionary = {i: [i] for i in range(256)}
    max_dict_size = 2 ** k

    seq = []  # Sequência atual

    # Lê o primeiro simbolo e adiciona à mensagem descomprimida
    seq.append(compressed.pop(0))
    decompressed = seq.copy()

    for byte in compressed:
        # Próximo byte já estará no dicionário ou é o próximo
        # a ser adicionado
        if byte in dictionary:
            entry = dictionary[byte]
        elif byte == len(dictionary):
            entry = seq.copy()
            entry.append(seq[0])
        else:
            raise ValueError(f"Erro na compressão do byte: {byte}")

        # Adiciona sequência de símbolos referentes ao índice na saída
        decompressed.extend(entry)

        # Adiciona sequência atual + símbolo seguinte ao dicionário
        # se não tiver atingido o tamanho máximo
        if len(dictionary) < max_dict_size:
            aux = seq.copy()
            aux.append(entry[0])
            dictionary[len(dictionary)] = aux

        seq = entry.copy()

    # Escreve mensagem descomprimida
    with open(out_path, mode="wb") as file:
        file.write(bytes(decompressed))

    print("Mensagem descomprimida com sucesso!")