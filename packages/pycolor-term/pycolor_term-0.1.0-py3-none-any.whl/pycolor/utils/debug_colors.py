import os

from ..pycolor import pyformat

def debug_colors() -> None:
    reset = pyformat.fmt_str('%Cz')

    print('styles:')
    for style in [
        'nor', 'bol', 'dim', 'ita', 'und', 'bli', 'inv', 'hid', 'str', 'ove'
    ]:
        print(pyformat.fmt_str('%%C(%s) %s %%Cz' % (style, style)), end='')
    print(reset)

    print('\nbold on and off:')
    print(pyformat.fmt_str('%C(bol) on '), end='')
    print(pyformat.fmt_str('%C(^bol) off '), end='')
    print(reset)

    def color_3bit(light: bool = False) -> None:
        colors = [
            'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'gray'
        ]

        for i in range(2):
            for color in colors:
                print(pyformat.fmt_str('%%C(%s%s%s) %s %%Cz' % (
                    '^' if i == 1 else '',
                    'light' if light else '',
                    color,
                    color[:3]
                )), end='')
        print(reset)

    print('\n3-bit color palette (normal and light):')
    color_3bit()
    color_3bit(light=True)

    def color_8bit() -> None:
        for row in range(32):
            for i in range(2):
                for col in range(8):
                    val = row * 8 + col
                    print(pyformat.fmt_str('%%C(%s%d) %3d ' % (
                        '^' if i == 1 else '',
                        val,
                        val
                    )), end='')
                print(reset, end='')
            print(reset)

    print('\n8-bit color palette:')
    color_8bit()

    def color_24bit(step: int, background: bool = False, col_limit: int = 10) -> None:
        range24 = range(0, 16, step)
        col = 0

        #pylint: disable=invalid-name

        for r in range24:
            rh = _hex(r + (r << 4))
            for g in range24:
                gh = _hex(g + (g << 4))
                for b in range24:
                    bh = _hex(b + (b << 4))
                    rgb = rh + gh + bh
                    print(pyformat.fmt_str('%%C(%s0x%s) %s ' % (
                        '^' if background else '',
                        rgb,
                        rgb
                    )), end='')

                    col += 1
                    if col == col_limit:
                        col = 0
                        print(reset)
        print(reset)

    try:
        col_limit = (os.get_terminal_size().columns // 8) // 8 * 8
    except OSError:
        col_limit = 8

    print('\n24-bit color palette sample:')
    color_24bit(2, col_limit=col_limit)
    color_24bit(2, background=True, col_limit=col_limit)

def _hex(val: int) -> str:
    charset = '0123456789abcdef'
    return charset[val >> 4] + charset[val & 15]
