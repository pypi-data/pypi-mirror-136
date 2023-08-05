import pprint
from colorama import Fore, Style, init
init()


def btprint(*values, sep: str=' ', end: str='\n', mode: str='print', color: str='default', style: str='default') -> None:
    """这是btprint函数，为您提供了一个美观打印功能。
       
       values、sep、end：同内置的print函数；

       mode：您希望打印的格式。可能的值为：

           print（使用print函数打印）

           list/list-item（按照顺序将列表中的每一个项目打印出来，如一个[0, 1, 2, 3]的列表，打印出来为：0 1 2 3

           dict/dict-item（按照顺序将字典中的每一个项目打印出来，如一个{0: 1, 2: 3, 4: 5}的字典，打印出来为：0->1 2->3 4->5

       color：您希望内容显示的颜色。可能的值为：

           default（系统默认）

           black（黑色）

           white（白色）

           red（红色）

           green（绿色）

           yellow（黄色）

           blue（蓝色）

           pink（梅红色）

           cyan（浅蓝色）
           
       style：您希望字体现实的格式。可能的值有：
       
           default（系统默认）
           
           dim（较暗文本）
           
           normal（正常显示）
           
           bold/bright（突出显示）"""

    if color == 'default':
        color = Fore.RESET
    elif color == 'black':
        color = Fore.BLACK
    elif color == 'white':
        color = Fore.WHITE
    elif color == 'red':
        color = Fore.RED
    elif color == 'green':
        color = Fore.RESET
    elif color == 'yellow':
        color = Fore.YELLOW
    elif color == 'blue':
        color = Fore.BLUE
    elif color == 'pink':
        color = Fore.MAGENTA
    elif color == 'cyan':
        color = Fore.CYAN
    else:
        color = ''

    if style == 'default':
        style = Style.RESET_ALL
    elif style == 'dim':
        style = Style.DIM
    elif style == 'normal':
        style = Style.NORMAL
    elif style == 'bright':
        style = Style.BRIGHT
    elif style == 'bold':
        style = Style.BRIGHT
    else:
        style = ''

    print(color, style, sep='', end='')

    if mode == 'print':
        print(*values, sep=sep, end=end)

    if mode == 'list':
        mode = 'list-item'
    if mode == 'list-item':
        for step in values:
            for item in step:
                print(item, end=' ')
            print()

    if mode == 'dict':
        mode = 'dict-item'
    if mode == 'dict-item':
        for step in values:
            for k, v in step.items():
                print(k, v, sep='->', end=' ')
            print()

    if mode == 'pprint':
        for step in values:
            pprint.pprint(step)
    
    print(Fore.RESET, Style.RESET_ALL, sep='', end='')