#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 13:26:41 2019
Copyright (C) 2019  Yurij Timofeev <hoaryhedgenhog(at)gmail(dot)com>

"simple_config" is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import sys

help_text = """
Here you need to put the text hint
"""

# foregrounds colors
BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, WHITE = range(30, 38)
# high intensity foregrounds colors
HI_BLACK, HI_RED, HI_GREEN, HI_YELLOW, HI_BLUE, HI_PURPLE, HI_CYAN, HI_WHITE = range(90, 98)
# background colors
BLACK_BG, RED_BG, GREEN_BG, YELLOW_BG, BLUE_BG, PURPLE_BG, CYAN_BG, WHITE_BG = range(40, 48)
# high intensity background colors
HI_BLACK_BG, HI_RED_BG, HI_GREEN_BG, HI_YELLOW_BG, HI_BLUE_BG, HI_PURPLE_BG, HI_CYAN_BG, HI_WHITE_BG = range(100, 108)
# other codes of SGR parameters
RESET, BOLD, FAINT, ITALIC, UNDERLINE, SLOW_BLINK, RAPID_BLINK, INVERSE, \
CONCEAL, CROSSED_OUT, DEF_FONT = range(0, 11)
FONT1, FONT2, FONT3, FONT4, FONT5, FONT6, FONT7, FONT8, FONT9 = range(11, 20)


def ansi_sgr(text, *sgr_seq, fg=None, bg=None):
    '''
    :param text: string for wrapping in ESC escape sequences
    :param sgr_seq: single or sequences of enumerated constant or <int> values ANSI SGR parameters
                    https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
    :param fg: Select foreground color as value in range 0-255 for 256-color lookup tables:
                   ESC[38;5;{n}m , for {n}
                       0-7:  standard colors (as in ESC [ 30–37 m)
                      8-15:  high intensity colors (as in ESC [ 90–97 m)
                    16-231:  6 × 6 × 6 cube (216 colors): 16 + (36 × r + 6 × g + b) (0 ≤ r, g, b ≤ 5)
                   232-255:  grayscale from black to white in 24 steps
               or tuple (r, g, b) values in range 0-255, 0-255, 0-255 for "true color" graphic cards with 16 to 24 bits:
                   ESC[38;2;{r};{g};{b}m
    :param bg: Select background color some as foreground
                   ESC[88;5;{n}m or ESC[48;2;{r};{g};{b}m
    :return: text wrapped in ANSI escape sequences
    '''

    esc_str = '\033[{}m'
    reset = '\033[0m'

    sgr_seq = list(sgr_seq)
    sgr_list = []
    while sgr_seq:
        param = sgr_seq.pop(0)
        if isinstance(param, (tuple, list)):
            sgr_seq[:0] = list(param)
        elif isinstance(param, int):
            sgr_list.append(str(param))
        else:
            raise Exception('bad parameter {}'.format(param))

    for param, x in zip((fg, bg), ('38', '48')):
        if param:
            sgr_list.append(x)
            if isinstance(param, (tuple, list)) and len(param) == 3:
                sgr_list.append('2')
                for p in param:
                    if isinstance(p, int) and 0 <= p <= 255:
                        sgr_list.append(str(p))
                    else:
                        raise Exception('bad parameter {}'.format(p))
            elif isinstance(param, int) and 0 <= param <= 255:
                sgr_list.append('5')
                sgr_list.append(str(param))
            else:
                raise Exception('bad parameter {}'.format(param))

    if not isinstance(text, str):
        text = str(text)

    mod_str = esc_str.format(';'.join(sgr_list))
    return mod_str + text + reset


class ConfigError(Exception):
    pass


class SimpleConfig:
    _ = ''
    _separator = '='
    _help_text = ''
    _defaults = ''

    def __init__(self, **_defaults):
        self._defaults = _defaults
        for k in _defaults.keys():
            setattr(self, k, _defaults[k])
        args_list = sys.argv[1:]

        while args_list:
            val = None
            key = args_list.pop(0)
            if key.startswith('--'):
                key = key[2:]
                if key == 'help':
                    self.show_help()
                    continue
                elif key in ('save_config', 'load_config'):
                    if args_list and not args_list[0].startswith('-'):
                        if key == 'save_config':
                            self.save(args_list.pop(0))
                        elif key == 'load_config':
                            self.load(args_list.pop(0))
                        continue
                    else:
                        self.show_help('missing value({})'.format(key))
            elif key.startswith('-'):
                if len(key) > 2:
                    val = key[2:]
                key = key[1:2]
            else:
                self._ = key
                continue
            self._set_val(key, val=val, args_list=args_list)

    def _set_val(self, key, val=None, args_list=None):
        def get_val(error=True):
            if args_list and not args_list[0].startswith('-'):
                return args_list.pop(0)
            elif error:
                self.show_help('missing value({})'.format(key))
            else:
                return None

        result = None
        try:
            if key not in self._defaults.keys():
                kl = [x for x in self._defaults.keys() if x.startswith(key)]
                if len(kl) == 1:
                    key = kl[0]
                elif len(kl) > 1:
                    self.show_help('ambiguous key({})'.format(' | '.join(kl)))
                else:
                    self.show_help('undefined key({})'.format(key))
            if self._defaults[key] is None:
                result = True
            elif isinstance(self._defaults[key], bool):
                if val is None:
                    result = False if getattr(self, key) else True
                elif val.upper() == "FALSE":
                    result = False
                elif val.upper() == "TRUE":
                    result = True
                else:
                    self.show_help('wrong value({}: {})'.format(key, val))
            elif isinstance(self._defaults[key], str):
                if val is None:
                    val = get_val()
                result = val
            elif isinstance(self._defaults[key], int):
                result = 1
                if val is None:
                    val = get_val(error=False)
                if val.isdecimal():
                    result = int(val)
                elif val and val.count(key[0]) == len(val):
                    result += len(val)
            elif isinstance(self._defaults[key], float):
                if val is None:
                    val = get_val()
                result = float(val)
            else:
                self.show_help('undefined key({})'.format(key))
            setattr(self, key, result)
        except ValueError:
            self.show_help('wrong value({}: {})'.format(key, val))

    def save(self, conf_file):
        text_rows = []
        for k in (x for x in self._defaults.keys()
                  if not (x.startswith('_') or self._defaults[x] is None)):
            text_rows.append('{}{}{}'.format(k, self._separator, getattr(self, k)))
        with open(conf_file, 'w') as cf:
            cf.write('\n'.join(text_rows))

    def load(self, conf_file):
        with open(conf_file, 'r') as cf:
            for s in cf.readlines():
                if self._separator in s:
                    k, v = (z.strip() for z in s.split(sep=self._separator, maxsplit=1))
                else:
                    k = s.strip()
                    v = None
                if k:
                    self._set_val(k, v)

    def show_help(self, err=None):
        message = []
        if err:
            message.append(ansi_sgr('Error: {}'.format(err), RED))
        conf = ['current config:', ]
        for x in (k for k in self._defaults.keys() if not k.startswith('_')):
            conf.append('\t{} = {}'.format(ansi_sgr(x, HI_BLUE), ansi_sgr(getattr(self, x), HI_YELLOW)))
        message.append(self._help_text or sys.modules['__main__'].__doc__)
        message.append(ansi_sgr('\n'.join(conf), CYAN))
        raise ConfigError('\n'.join(message))  #


if __name__ == '__main__':
    try:
        my_conf = SimpleConfig(
            # _='test_data',
            # _help_text=help_text,
            # _separator='::',
            line_count=10,
            hello=None,
            out_file='file.name',
            float_value=6.6,
            in_file='',
            bool_val=True,
        )

        # my_conf.save('simple.conf')
        # my_conf.load('simple.conf')

        if my_conf.line_count:
            [print(ansi_sgr('{} * {} = {}'.format(
                x, y, ansi_sgr(x * y, fg=(255 - (x * y * 3), 28 * x, 28 * y))), fg=28 * x)) if y else print()
             for x in range(1, my_conf.line_count)
             for y in range(my_conf.line_count)]
            print()

        if my_conf.hello:
            print(ansi_sgr('Hello from SimpleConfig', (BOLD, ITALIC), fg=(240, 0, 10), bg=150))

        my_conf.show_help('no error!')

    except (ConfigError, KeyboardInterrupt) as em:
        print(em)
