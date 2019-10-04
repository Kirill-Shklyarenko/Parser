from struct import *
import psycopg2

planner = r'Planner'
planner_RSF = r'Planner.rsf'
"""
def access_bit(data, num):
    base = int(num // 8)
    shift = int(num % 8)
    return (data[base] & (1 << shift)) >> shift

    qwe = [access_bit(word, i) for i in range(len(word) * 8)]
    res = functools.reduce(lambda total, d: 10 * total + d, qwe, 0)
    asd = bin(word)
    byte_shift = bin(res) >> 2
"""


def line_parser(number_of_line):
    with open(planner) as file:
        line = file.readlines()[number_of_line - 1: number_of_line]
        line = line[0].split()
        return line


def value_of_lines():
    with open(planner) as file:
        lines = file.readlines()
        return int(len(lines))

def byte_reader(type_w, size, wib):
    with open(planner_RSF, 'rb') as file:
        header = file.read(14).decode('cp1252')  # Имя файла заголовка [0 - 14]
        wib *= 2  # Номер слова в блоке умножаем на размер слова (2 байта)
        file.seek(wib + 14)  # Прибавляем 14 байт, чтобы отсечь Имя файла заголовка
        word = file.read(size)

        value = unpack(type_w, word)[0]
        print('BYTES: ' + str(word))
        print('VALUE: ' + str(value))
        return value


def parse_planner_rsf():
    number_of_line = 3
    vol = value_of_lines()
    info = {
        # 'block_size': None,
        # 'freq_rate': None,
        'var_description': None,
        'params':
            {
                'name': None,
                'word_in_block': None,
                'mask': None,
                'shift': None,
                'scale': None,
                'type': None,
                'dimension': None,
                'value': None,
            }
    }

    while number_of_line < vol:
        line = line_parser(number_of_line)
        if ';' in line[0]:
            info['var_description'] = line[1]
            number_of_line += 1
        elif len(line) > 3:
            info['params']['name'] = line[0]
            info['params']['word_in_block'] = int(line[1])
            info['params']['mask'] = line[2]
            info['params']['shift'] = int(line[3])
            info['params']['scale'] = float(line[4])
            info['params']['type'] = line[5]
            info['params']['dimension'] = None
            if len(line) > 6:
                info['params']['dimension'] = line[6]

            if 'W' in line[5]:
                type_w = 'I'  # UINT_2t
                size = 2
            if 'S' in line[5]:
                type_w = 'i'  # INT_2t
                size = 2
            if 'U' in line[5]:
                type_w = '<i'
                size = 4  #
                next_line = line_parser(number_of_line + 1)

                prev_wib = info['params']['word_in_block']
                curr_wib = int(next_line[0])

                info['params']['word_in_block'] = [curr_wib, prev_wib]
                info['params']['mask'] = next_line[1]
                info['params']['shift'] = int(next_line[2])

                info['params']['value'] = byte_reader(type_w, size, curr_wib)
                print(info, '\r\n')
                number_of_line += 2
            if 'L' in line[5]:
                type_w = ''
                size = 4
            if 'R' in line[5]:
                type_w = ''
                size = 1
            if 'F' in line[5]:
                type_w = 'f'
                size = 4  # 2 слова х 2 байта(размер слова)
                wib = info['params']['word_in_block']
                info['params']['value'] = byte_reader(type_w, size, wib)
                number_of_line += 1
                print(info, '\r\n')


if __name__ == "__main__":
    parse_planner_rsf()
