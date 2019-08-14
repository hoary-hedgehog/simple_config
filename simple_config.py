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


class ConfigError(Exception):
    pass

class SimpleConfig():
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
                elif key in ('save_conf', 'load_conf'):
                    if args_list and not args_list[0].startswith('-'):
                        if key == 'save_conf':
                            self.save(args_list.pop(0))
                        elif key == 'load_conf':
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
            self._set_val(key, val = val, args_list = args_list)
    
    
    def _set_val(self, key, val = None, args_list = None):
        def get_val(error = True):
            if args_list and not args_list[0].startswith('-'):
                return args_list.pop(0)
            elif error:
                self.show_help('missing value({})'.format(key))
            else:
                return None
        result = None
        try:
            if not key in self._defaults.keys():
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
                    val = get_val(error = False)
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
        for k in (x for x in self._defaults.keys() if not (x.startswith('_') or self._defaults[x] is None)):
            text_rows.append('{}{}{}'.format(k, self._separator, getattr(self, k)))
        with open(conf_file, 'w') as cf:
            cf.write('\n'.join(text_rows))
    
    
    def load(self, conf_file):
        with open(conf_file, 'r') as cf:
            for s in cf.readlines():
                if self._separator in s:
                    k, v = (z.strip() for z in s.split(sep=self._separator, maxsplit=1))
                else:
                    k = s.strip(); v = None
                self._set_val(k, v)
    
    
    def show_help(self, err = None):
        message = []
        if err:
            message.append('Error: {}'.format(err))
        conf = ['current config:', ]
        for x in (k for k in self._defaults.keys() if not k.startswith('_')):
            conf.append('\tvar {} = {}'.format(x, getattr(self, x)))
        message.append(self._help_text or __doc__ or '\n'.join(conf))
        raise ConfigError('\n'.join(message)) #



if __name__ == '__main__':
    try: 
        my_conf = SimpleConfig(
#                _ = 'test_data',
#                _help_text = help_text, 
#                _separator = '::',
                line_count =  10,
                t =  None,
                out_file = '',
                float_value = 6.6,
                in_file = '',
                bool_val = True,
                                )
        
#        my_conf.save('simple.conf')
#        my_conf.load('simple.conf')
        if my_conf.t:
            [print('{} * {} = {}'.format(x, y, x*y)) if y else print()
            for x in range(1, my_conf.line_count) for y in range(my_conf.line_count)]
        my_conf.show_help('no error!')
    except ConfigError as em:
        print(em)
    
