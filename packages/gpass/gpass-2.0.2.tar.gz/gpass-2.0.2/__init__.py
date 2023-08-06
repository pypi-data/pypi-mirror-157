import sys, os
import enum
import termcolor 

"""Just checking differences"""

__version__ = '2.0.2'
    
class SPECIAL_MASKS(enum.Enum):

    NO_MASK = False
    BLIND_MASK = None
    DEFAULT_MASK = "*"
    ONE_REVERSE = 0xfff
    MIMI_REVERSE = 0x1ff

##GP_DEFAULT_MASK = SPECIAL_MASKS.get(os.environ.get("GETPASS_MASK" , None) , "DEFAULT_MASK")
GP_DEFAULT_MASK = getattr(SPECIAL_MASKS , os.environ.get("GETPASS_MASK" , '')  , SPECIAL_MASKS.DEFAULT_MASK  )
class OneReverse():

    def __init__(self, colored , colorset):

        if colored:
            import termcolor
            self.colored = lambda x : termcolor.colored(x , colorset[-1])

        else :
            self.colored = lambda x : x

    def mask(self):
        global password

        if len(password) == 1 :
            return self.colored(password[0])


        return self.colored(f'\b{SPECIAL_MASKS.DEFAULT_MASK.value}{password[-1]}')

    def blank(self):

        return '\b \b'

    def enter(self):
        return self.colored(f'\b{SPECIAL_MASKS.DEFAULT_MASK.value}\n')
        pass

class MimiReverse(OneReverse):

    def blank(self):

        global password

        if len(password) == 1 :
            return '\b \b'

        return self.colored(f'\b\b{password[-2]} \b')

standardize_to_str = lambda x : x if (isinstance(x , str)) else ((x.decode('utf8')) if isinstance(x , bytes) else str(x))

password = ""

class _GetchUnix:

    def call(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt
        self.func = msvcrt.getch 
        
    def call(self):
        return self.func()
    
def _Getch():
    """Gets a single character from standard input.  Does not echo to the
    screen."""
    
    if os.name == 'nt':
        return  _GetchWindows()
    
    elif os.name == 'posix':
        
        return   _GetchUnix()
    
    else:
        raise SystemError(f'Getch can only be conducted on POSIX/NT systems. For other systems please monkey-patch _Getch in source code with the appropriate Get character system call')
    
getch = _Getch()

regular_blank = lambda : '\b \b'
regular_enter = lambda : '\n'

def blind_mask(): 

    mask = lambda : '' 
 
    return mask
 
def char_mask(repl , colored : bool = False, colorset : list = None ):
    
    if not colored:
        mask = lambda : repl 

    else:
        mask = lambda : termcolor.colored(repl , colorset[-1])
    
    return mask

def no_mask(colored, colorset):
    
    global password 
    
    if colored:
        return lambda : termcolor.colored(password[-1] , colorset[-1])
    
    return lambda : password[-1]
    
def getpass(	prompt : str = "Enter Password: " , mask : str = GP_DEFAULT_MASK ,
                colored : bool = False , colorset : list = ('yellow' , 'green') , stream = sys.stderr ,
                on_error : bool = True):

    global password, getch 
    password = '' 							##Refreshing to make sure last remnants dont remain

    if colored:
        
        import colorama 
        colorama.init(autoreset = True)
        prompt = termcolor.colored(prompt , colorset[0])
        
    blank = regular_blank 
    enter = regular_enter 

    if (mask == None) or (mask == '') or (mask == b'') or (mask == SPECIAL_MASKS.BLIND_MASK):

        mask = blind_mask()
  
    elif (mask == True)  or (mask == SPECIAL_MASKS.DEFAULT_MASK):

        mask = char_mask(SPECIAL_MASKS.DEFAULT_MASK.value, colored , colorset)
        
    elif (mask == False ) or (mask == SPECIAL_MASKS.NO_MASK):

        mask = no_mask(colored, colorset)

    elif (mask == SPECIAL_MASKS.ONE_REVERSE):

        one_reverse = OneReverse(colored , colorset)

        mask = one_reverse.mask
        blank = one_reverse.blank
        enter = one_reverse.enter

    elif (mask == SPECIAL_MASKS.MIMI_REVERSE):

        mimi_reverse = MimiReverse(colored , colorset)

        mask = mimi_reverse.mask
        blank = mimi_reverse.blank
        enter = mimi_reverse.enter

    elif isinstance(mask , str):
        mask = char_mask(mask , colored, colorset)

    else:
     
        raise TypeError(f'Only strings and SPECIAL_MASKS can be used as masks, not {type(mask).__name__}')

    print(prompt , end = '' , file = stream)
    stream.flush()

    while True :

        try:
            
            character = standardize_to_str(getch.call())
            key = ord(character)

        except:
            
            continue

        if key == 13:

            stream.write(enter())
            stream.flush()

            return password

        elif key == 27 :
            #Escape Key 
            continue
        
        elif key in (8,127):

                if len(password) > 0:

                    stream.write(blank())
                    stream.flush()
                    
                    password = password[:-1]

        elif key == 3 : #Ctrl C

            if on_error:
                raise KeyboardInterrupt(f'Password Input has been interrupted by user')

            return None

        elif -1 < key < 32 :
            #System Keys
            continue

        else :

            password += character
            stream.write(mask())
            stream.flush()