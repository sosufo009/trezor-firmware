from trezor.ui.widgets import confirm_path_warning, require

from . import HARDENED
from .layout import address_n_to_str

if False:
    from typing import Any, Callable, List, Sequence, TypeVar
    from trezor import wire

    # XXX this is a circular import, but it's only for typing
    from .keychain import Keychain

    Bip32Path = Sequence[int]
    Slip21Path = Sequence[bytes]
    PathType = TypeVar("PathType", Bip32Path, Slip21Path)


async def validate_path(
    ctx: wire.Context,
    validate_func: Callable[..., bool],
    keychain: Keychain,
    path: List[int],
    curve: str,
    **kwargs: Any,
) -> None:
    keychain.verify_path(path)
    if not validate_func(path, **kwargs):
        await show_path_warning(ctx, path)


async def show_path_warning(ctx: wire.Context, path: Bip32Path) -> None:
    await require(confirm_path_warning(ctx, address_n_to_str(path)))


def validate_path_for_get_public_key(path: Bip32Path, slip44_id: int) -> bool:
    """
    Checks if path has at least three hardened items and slip44 id matches.
    The path is allowed to have more than three items, but all the following
    items have to be non-hardened.
    """
    length = len(path)
    if length < 3 or length > 5:
        return False
    if path[0] != 44 | HARDENED:
        return False
    if path[1] != slip44_id | HARDENED:
        return False
    if path[2] < HARDENED or path[2] > 20 | HARDENED:
        return False
    if length > 3 and is_hardened(path[3]):
        return False
    if length > 4 and is_hardened(path[4]):
        return False
    return True


def is_hardened(i: int) -> bool:
    return bool(i & HARDENED)


def path_is_hardened(address_n: Bip32Path) -> bool:
    return all(is_hardened(n) for n in address_n)
