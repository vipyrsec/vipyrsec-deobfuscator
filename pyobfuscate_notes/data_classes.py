import sys
sys.exit()

class set:
    getattr = 2
    empty_dict = 1
    new_maptype = 0
new_maptype=[]
maptype=maptype([str(),(),_(
    chr=chr, #_________
    reversed=lambda:reversed, #________
    name=lambda _:_.__name__, #________________
    iter=lambda:iter, #_______________
    true=lambda:maptype.__eq__(maptype, maptype), # _________________________
    builtins_get=lambda _0:getattr(__builtins__, _0), # ___________________
    getattr=getattr, #_
    complex=lambda:complex, #________________________
    maptype=lambda:float, #maptype
    str=lambda:str, #__________ and _____
    __eq__=lambda _0, __0: _0 == __0, #__________________
    empty_list=lambda:[], #____________________
    pow=lambda:pow, #____
    __file__=lambda:__file__, #_______________________
    __ge__=lambda _:_.__ge__, #___________
    ord=lambda:ord, #_____________________
    empty_dict=lambda:{}, #__
    globals=lambda:globals, #______________________
    int=lambda:int, #_____________
    __class__=lambda _:_.__class__, #_________________
    new_maptype=lambda _0:type(*_0), #___
    __dir__=lambda _:_.__dir__, #____________
    hex=lambda:hex, #______________
    set=lambda:set, #______

)])

maptype_dict = {'_________': 'chr', '________': 'reversed', '________________': 'name', '_______________': 'iter', '_________________________': 'true', '___________________': 'builtins_get', '_': 'getattr', '________________________': 'complex', '__________': 'str_', '__________________': '__eq__', '____________________': 'empty_list', '____': 'pow', '_______________________': '__file__', '___________': '__ge__', '_____________________': 'ord', '__': 'empty_dict', '______________________': 'globals', '_____________': 'int', '_________________': '__class__', '___': 'new_maptype', '____________': '__dir__', '______________': 'hex', '______': 'set', 'maptype': 'maptype', '_____': 'str'}

import pickle
reversed=maptype.new_maptype([maptype.str_(),(),maptype.set()()])


empty_dict=maptype.new_maptype([maptype.str_(),(),maptype.set()(
    str=lambda _0,__0:exec(_0),
    chr=lambda:'=pickle.loads',
    str_=lambda _0:_0.encode('ISO-8859-1'),
    set=lambda:''.join,
    maptype=lambda _0:'____'+''.join(('['+str(__0)+']')
                                     if(type(__0) == int)
                                     else('.'+__0
                                          if isinstance(__0, str)
                                          else '')
                                     for __0 in _0),
    iter=lambda:'global ____;',
    pow=lambda:[empty_dict.new_maptype(_0,empty_dict.str_(__0))for(_0,__0)in reversed(new_maptype) ],
    new_maptype=lambda _0,__0:exec('global ____;'+empty_dict.maptype(_0)+'=pickle.loads(__0)'),
    hex=lambda:';',
    __dir__=lambda:'_',
    empty_dict=lambda:'"',
    __class__=lambda:'(',
    getattr=lambda:')',
    int=lambda:'[',
    reversed=lambda:']',
    __ge__=lambda:'.',
    name=lambda:'-',

)])

mov = {('chr', 'reversed'): r'\x9c',
       ('chr', 'str'): '(',
       ('chr', 'empty_dict'): 'f',
       ('chr', 'pow'): 'm',
       ('chr', 'maptype'): 'S',
       ('chr', 'getattr'): 'F',
       ('chr', 'new_maptype'): r'\x00',
       ('chr', 'set'): ':',
       ('__dir__', 'getattr'): 'p',
       ('__dir__', 'empty_dict'): r'\x14',
       ('__dir__', 'str'): r'\x8b',
       ('__dir__', 'new_maptype'): r'\x86',
       ('__dir__', 'pow'): r'\x0f',
       ('__dir__', 'reversed'): r'\x0e',
       ('__dir__', 'maptype'): '¡',
       ('__dir__', 'set'): r'\x1f',
       ('name', 'str'): 'L',
       ('name', 'set'): '§',
       ('name', 'maptype'): r'\x16',
       ('name', 'getattr'): r'\x93',
       ('name', 'empty_dict'): 'ñ',
       ('name', 'pow'): 'v',
       ('name', 'reversed'): 'y',
       ('name', 'new_maptype'): 'D',
       ('__class__', 'new_maptype'): '¯',
       ('__class__', 'reversed'): r'\x84',
       ('__class__', 'getattr'): '¶',
       ('__class__', 'pow'): '.',
       ('__class__', 'str'): 'o',
       ('__class__', 'maptype'): ' ',
       ('__class__', 'empty_dict'): '&',
       ('__class__', 'set'): '¨',
       ('getattr', 'maptype'): 'z',
       ('getattr', 'new_maptype'): r'\xad',
       ('getattr', 'reversed'): 'j',
       ('getattr', 'getattr'): r'\xa0',
       ('getattr', 'chr'): '=',
       ('getattr', 'pow'): 'Ä',
       ('getattr', 'set'): r'\x1d',
       ('getattr', 'str'): ')',
       ('getattr', 'empty_dict'): 'Ú',
       ('__ge__', 'maptype'): 'Õ',
       ('__ge__', 'set'): 'à',
       ('__ge__', 'pow'): r'\x8c',
       ('__ge__', 'str'): ',',
       ('__ge__', 'reversed'): '5',
       ('__ge__', 'getattr'): 'K',
       ('__ge__', 'new_maptype'): r'\x17',
       ('__ge__', 'empty_dict'): 'U',
       ('builtins_get', 'empty_dict'): r'\x1e',
       ('builtins_get', 'getattr'): r'\n',
       ('builtins_get', 'reversed'): 'H',
       ('builtins_get', 'set'): r'\x95',
       ('builtins_get', 'pow'): '{',
       ('builtins_get', 'str'): '<',
       ('builtins_get', 'new_maptype'): r'\x07',
       ('builtins_get', 'maptype'): 'd',
       ('int', 'reversed'): 'B',
       ('int', 'pow'): r'\x03',
       ('int', 'maptype'): r'\x12',
       ('int', 'empty_dict'): r'\x04',
       ('int', 'str'): r'\x85',
       ('int', 'getattr'): r'\x01',
       ('int', 'new_maptype'): 'E',
       ('int', 'set'): r'\x18',
       ('reversed', 'str'): '}',
       ('reversed', 'pow'): '°',
       ('reversed', 'empty_dict'): 'k',
       ('reversed', 'getattr'): 'T',
       ('reversed', 'maptype'): 'C',
       ('reversed', 'reversed'): r'\x87',
       ('reversed', 'set'): r'\x02',
       ('reversed', 'new_maptype'): '-',
       ('iter', 'empty_dict'): r'\t',
       ('iter', 'maptype'): '4',
       ('iter', 'pow'): r'\x0c',
       ('iter', 'reversed'): r'\x1c',
       ('iter', 'set'): 'b',
       ('iter', 'str'): '"',
       ('iter', 'getattr'): '6',
       ('iter', 'new_maptype'): '!',
       ('empty_list', 'set'): r'\x92',
       ('empty_list', 'getattr'): '#',
       ('empty_list', 'new_maptype'): 'a',
       ('empty_list', 'pow'): '?',
       ('empty_list', 'maptype'): '·',
       ('empty_list', 'chr'): r'\x88',
       ('empty_list', 'str'): 'å',
       ('empty_list', 'empty_dict'): r'\x89',
       ('empty_list', 'reversed'): 'R',
       ('str_', 'empty_dict'): 'h',
       ('str_', 'set'): r'\x05',
       ('str_', 'str'): r'\x10',
       ('str_', 'reversed'): r'\x83',
       ('str_', 'getattr'): 'Ð',
       ('str_', 'new_maptype'): 'g',
       ('str_', 'pow'): 'l',
       ('str_', 'chr'): r'\x13',
       ('str_', 'maptype'): 'Q',
       ('new_maptype', 'maptype'): '»',
       ('new_maptype', 'new_maptype'): "'",
       ('new_maptype', 'str'): 'e',
       ('new_maptype', 'getattr'): '%',
       ('new_maptype', 'set'): 'M',
       ('new_maptype', 'reversed'): '1',
       ('new_maptype', 'pow'): r'\x0b',
       ('new_maptype', 'empty_dict'): r'\r',
       ('set', 'set'): 'n',
       ('set', 'str'): 't',
       ('set', 'empty_dict'): r'\x82',
       ('set', 'maptype'): r'\x80',
       ('set', 'pow'): 'Ë',
       ('set', 'getattr'): '$',
       ('set', 'new_maptype'): 's',
       ('set', 'reversed'): '>',
       ('empty_dict', 'pow'): r'\x8d',
       ('empty_dict', 'empty_dict'): r'\x06',
       ('empty_dict', 'maptype'): 'I',
       ('empty_dict', 'reversed'): 'q',
       ('empty_dict', 'set'): 'N',
       ('empty_dict', 'new_maptype'): '8',
       ('empty_dict', 'getattr'): r'\x1b',
       ('empty_dict', 'str'): 'Æ',
       ('maptype', 'empty_dict'): '+',
       ('maptype', 'maptype'): '7',
       ('maptype', 'pow'): r'\x8e',
       ('maptype', 'getattr'): ']',
       ('maptype', 'set'): r'\x15',
       ('maptype', 'str'): r'\x7f',
       ('maptype', 'reversed'): '*',
       ('maptype', 'new_maptype'): r'\x9b',
       ('pow', 'str'): r'\x11',
       ('pow', 'pow'): '/',
       ('pow', 'reversed'): '9',
       ('pow', 'set'): r'\x8a',
       ('pow', 'maptype'): '|',
       ('pow', 'empty_dict'): ';',
       ('pow', 'new_maptype'): 'O',
       ('pow', 'getattr'): '0',
       ('__eq__', 'pow'): '@',
       ('__eq__', 'new_maptype'): 'ð',
       ('__eq__', 'reversed'): 'A',
       ('__eq__', 'maptype'): 'P',
       ('__eq__', 'getattr'): 'w',
       ('__eq__', 'empty_dict'): r'\x1a',
       ('__eq__', 'set'): '~',
       ('__eq__', 'str'): 'c',
       ('hex', 'str'): '_',
       ('hex', 'reversed'): '2',
       ('hex', 'new_maptype'): r'\x19',
       ('hex', 'pow'): 'x',
       ('hex', 'getattr'): 'º',
       ('hex', 'empty_dict'): r'\x08',
       ('hex', 'set'): 'r',
       ('hex', 'maptype'): 'G',
       ('str', 'empty_dict'): 'i',
       ('str', 'getattr'): r'\x81',
       ('str', 'new_maptype'): r'\x94',
       ('str', 'reversed'): '3',
       ('str', 'maptype'): 'J',
       ('str', 'set'): 'u',
       ('str', 'str'): '´',
       ('str', 'pow'): 'Ã'
       }



