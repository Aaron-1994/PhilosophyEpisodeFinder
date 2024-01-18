from prettytable import PrettyTable, ALL
from typing import List, Tuple


def add_to_table(
    table: PrettyTable, L1: List[Tuple[int, str]], L2: List[Tuple[int, str]]
) -> PrettyTable:
    for i, item in enumerate(L1):
        if L1[i][0] == "":
            table.add_row([f"{L1[i][0]}\n{L1[i][1]}", f"EP:{L2[i][0]}\n{L2[i][1]}"])
        elif L2[i][0] == "":
            table.add_row([f"EP:{L1[i][0]}\n{L1[i][1]}", f"{L2[i][0]}\n{L2[i][1]}"])
        else:
            table.add_row([f"EP:{L1[i][0]}\n{L1[i][1]}", f"EP:{L2[i][0]}\n{L2[i][1]}"])


def extend_list(l: List[Tuple[int, str]], number: int) -> None:
    l.extend([("", "") for _ in range(number)])


def table_print(
    L1: List[Tuple[int, str]],
    L2: List[Tuple[int, str]],
    L1_name: str = "List 1",
    L2_name: str = "List 2",
) -> None:
    table = PrettyTable([L1_name, L2_name])

    table.horizontal_char = "="
    table.hrules = ALL
    table.header = False
    table.max_width = 70
    table.padding_width = 2

    if len(L1) > len(L2):
        extend_list(L2, len(L1) - len(L2))
    elif len(L1) < len(L2):
        extend_list(L1, len(L2) - len(L1))

    add_to_table(table, L1, L2)
    print(table)
