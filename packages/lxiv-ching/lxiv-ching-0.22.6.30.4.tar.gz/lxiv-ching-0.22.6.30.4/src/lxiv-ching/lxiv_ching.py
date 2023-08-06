from datetime import datetime
from random import choice
import argparse
import textwrap
from db import hexes, comments_dict

# specify th e path here:
path = "lxivChing/history-lxiv.txt"


def __init__():
    query = wrap(input("Query: "), 71)
    if query == '':
        query = "..."
    coin_values = ''

    parser = argparse.ArgumentParser()  # description=''
    parser.add_argument('--nohistory', help="don't write to history.txt", action='store_true', default=False)
    parser.add_argument('--debug', help="enter debug mode", action='store_true', default=False)
    args = parser.parse_args()

    if args.debug:
        origin_hexagram = int(query[0] + query[1])
        trans_hexagram = int(query[2] + query[3])
        origin_hexagram_code = {value: key for (key, value) in hexes.items()}[origin_hexagram]
        trans_hexagram_code = {value: key for (key, value) in hexes.items()}[trans_hexagram]
        changing_lines = []
    else:
        for line in range(1, 7):
            coin_values += str(choice([3, 2]) + choice([3, 2]) + choice([3, 2]))
        origin_hexagram_code, trans_hexagram_code, changing_lines = lines_and_hex_decoder(coin_values)
        origin_hexagram = hexes[origin_hexagram_code]
        trans_hexagram = hexes[trans_hexagram_code]

    lines_to_read, comments = evaluation(changing_lines, origin_hexagram)

    lines_to_read_rep = ''
    for line in lines_to_read:
        lines_to_read_rep += f"{line}, "
    lines_to_read_rep = lines_to_read_rep[:-2]

    time = datetime.now().isoformat(timespec='minutes')
    result = f"{origin_hexagram}->{trans_hexagram}"

    output = f"\nTime:\n\t{time}\n" \
             f"Query: \n\t{query}\n" \
             f"Result:\n\t{result}\n" \
             f"Comments:\n\t{comments}"
    if len(lines_to_read) > 0:
        output += f"\n\tLines to read: {str(lines_to_read_rep)}"
    output += '\n'

    print(output)

    if not args.nohistory:
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(output)
        except FileNotFoundError:
            with open("../history-lxiv.txt", 'a', encoding='utf-8') as f:
                f.write(output)

    if args.debug:
        print(f"{origin_hexagram_code} -> {trans_hexagram_code}")


def wrap(string, max_width):
    return '\n\t'.join(textwrap.wrap(string, max_width))


def lines_and_hex_decoder(coins):
    origin_code = ''
    trans_code = ''
    changing_lines = []
    for i, v in enumerate(coins):
        match v:
            case '6':
                origin_code += '0'
                trans_code += '1'
                changing_lines.append(i + 1)
            case '7':
                origin_code += '1'
                trans_code += '1'
            case '8':
                origin_code += '0'
                trans_code += '0'
            case '9':
                origin_code += '1'
                trans_code += '0'
                changing_lines.append(i + 1)
    return origin_code, trans_code, changing_lines


def evaluation(changing_lines, origin_hexagram) -> (list, str):
    how_many_lines = len(changing_lines)

    match how_many_lines:
        case 4:
            lines_to_read = min(list({1, 2, 3, 4, 5, 6} - set(changing_lines)))
            comments = comments_dict[4]
        case 5:
            lines_to_read = list({1, 2, 3, 4, 5, 6} - set(changing_lines))
            comments = comments_dict[5]
        case 6:
            if origin_hexagram == 1 or origin_hexagram == 2:
                lines_to_read = None
                comments = comments_dict["special"]
            else:
                lines_to_read = None
                comments = comments_dict[6]

        case _:
            lines_to_read = changing_lines
            comments = comments_dict[how_many_lines]
    return lines_to_read, comments


if __name__ == '__main__':
    __main__()
