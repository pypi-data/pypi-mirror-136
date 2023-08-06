import logging
import pathlib
import random
import sys
from ast import parse

import pkg_resources


def parse_flist(path):
    package = __name__.split(".")[0]
    TEMPLATES_PATH = pathlib.Path(
        pkg_resources.resource_filename(package, "wordlists/")
    )
    path = TEMPLATES_PATH / "words3.txt"
    words = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        clean = line.strip()
        words.append(clean)
    return words


def get_words(count=2):
    words = parse_flist("clinepunk/wordlists/words.txt")
    words = list(filter(lambda x: len(x) >= 2, words))
    remove = ["-", "sex", " "]
    sample = random.sample(words, count)
    for word in remove:
        if word in "".join(sample):
            sample = random.sample(words, count)

    logging.debug(f"sample words is {sample}")

    return [x.lower() for x in sample]


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    lst = get_words(count=2)
    out = "".join(lst)
    logging.debug(out)
    return out


if __name__ == "__main__":
    main()
