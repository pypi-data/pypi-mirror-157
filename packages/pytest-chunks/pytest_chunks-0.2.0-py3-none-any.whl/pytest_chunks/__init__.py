import math
import typing

import pytest


def chunks_validator(v: typing.Any) -> typing.Tuple[int, int]:
    if not isinstance(v, str):
        raise ValueError("chunks requires a string")

    n, _, m = v.partition("-")
    chunk, n_chunks = int(n), int(m)
    if n_chunks < 1:
        raise ValueError("The number of chunks must be > 1")
    if chunk < 1:
        raise ValueError("The chunk index must be > 1")
    if chunk > n_chunks:
        raise ValueError("The chunk index must be < of the number of chunks")
    return chunk, n_chunks


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--chunk",
        type=chunks_validator,
        help="Only run tests a chunk of tests (format: X-Y)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: typing.List[pytest.Item]
) -> None:
    chunks_config = config.getoption("--chunk")
    if not chunks_config:
        return

    chunk_index, chunks_total = chunks_config
    total = len(items)
    chunk_size = math.ceil(total / chunks_total)

    chunks = [items[i : i + chunk_size] for i in range(0, total, chunk_size)]

    # Remove the chunk to run
    del chunks[chunk_index - 1]

    # Mark other as skipped
    marker = pytest.mark.skip(
        reason=f"Not part of the selected chunk (eg: {chunk_index}-{chunks_total}"
    )
    for chunk in chunks:
        for test in chunk:
            test.add_marker(marker)
