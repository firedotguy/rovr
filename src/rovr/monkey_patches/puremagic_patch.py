import json
from binascii import unhexlify
from importlib import resources

import puremagic

try:
    if puremagic.__version__ != "1.30":
        raise RuntimeError(
            f"Expected puremagic version 1.30, but found {puremagic.__version__}"
        )
except RuntimeError:
    from rich.console import Console

    Console().print_exception()
    raise SystemExit(1)
    # this is kind of a stupid thing to do
    # but essentially I want a rich render of the traceback
    # but normal console printing is so simple
    # and non-rich traceback is too hard to read


def _magic_data() -> tuple[
    list[puremagic.PureMagic],
    list[puremagic.PureMagic],
    list[puremagic.PureMagic],
    dict[bytes, list[puremagic.PureMagic]],
]:
    """Read the magic file"""  # noqa: DOC201
    data = json.loads(
        resources
        .files("rovr.monkey_patches")
        .joinpath("magic_data.json")
        .read_text("utf-8")
    )
    headers = sorted(
        (puremagic.main._create_puremagic(x) for x in data["headers"]),
        key=lambda x: x.byte_match,
    )
    footers = sorted(
        (puremagic.main._create_puremagic(x) for x in data["footers"]),
        key=lambda x: x.byte_match,
    )
    extensions = [puremagic.main._create_puremagic(x) for x in data["extension_only"]]
    multi_part_extensions = {}
    for file_match, option_list in data["multi-part"].items():
        multi_part_extensions[unhexlify(file_match.encode("ascii"))] = [
            puremagic.main._create_puremagic(x) for x in option_list
        ]
    return headers, footers, extensions, multi_part_extensions


(
    puremagic.main.magic_header_array,
    puremagic.main.magic_footer_array,
    puremagic.main.extension_only_array,
    puremagic.main.multi_part_dict,
) = _magic_data()
