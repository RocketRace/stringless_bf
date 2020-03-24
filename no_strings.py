'''
This module is dedicated to parsers and interpreters that don't input source code as strings, 
but rather valid Python source code. For instance: 

Instead of passing `"+"` to a parser, one would pass `+_`, given that `_` is an instance
of the appropriate interpreter. 
'''
import sys

class BFInterpreter:
    '''
    Interprets Brainfuck code, given source code as Python.
    '''
    default_string = "_"

    def __class_getitem__(cls, depth):
        '''
        Syntactic sugar to return multiple distinct instances of `BFInterpreter`.

        Multiple initial instances are necessary due to limitations of the Python AST.
        '''
        if isinstance(depth, int):
            if depth == 1:
                return cls()
            else:
                return [cls("_" * (i + 1)) for i in range(depth)]
        else:
            return NotImplemented

    def __init__(self, string = None, *, parent = None):
        '''
        Returns a new isntance of `BFInterpreter`. 
        
        `parent` is a reference to the original instance of `BFInterpreter` from which
        children (new intances) are initialized

        '''
        self.string = string if string else self.default_string
        if parent is not None:
            self.parent = parent
        else:
            self.parent = self
            self.stored = None
            self.chains = None

    def __repr__(self):
        return self.string

    def __pos__(self):
        return BFInterpreter("+" + self.string, parent=self.parent)

    def __neg__(self):
        return BFInterpreter("-" + self.string, parent=self.parent)

    def __add__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(self.string + "+" + item.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter(self.string + "+[" + self._unpack(*item) + "]", parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter(self.string + "+...", parent=self.parent)
        else:
            return NotImplemented

    def __sub__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(self.string + "-" + item.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter(self.string + "-[" + self._unpack(*item) + "]", parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter(self.string + "-...", parent=self.parent)
        else:
            return NotImplemented

    def __radd__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(item.string + "+" + self.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter("[" + self._unpack(*item) + "]+" + self.string, parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter("...+" + self.string, parent=self.parent)
        else:
            return NotImplemented
    
    def __rsub__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(item.string + "-" + self.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter("[" + self._unpack(*item) + "]-" + self.string, parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter("...-" + self.string, parent=self.parent)
        else:
            return NotImplemented
    
    def __bool__(self):
        # This is overridden to prevent information being lost in 
        # comparison chains (`a<b<c`), as __bool__ must return True/False.
        if self.string != self.default_string:
            self.parent.stored = self.string
        return True

    def __lt__(self, item):
        if self.parent.stored:
            if isinstance(item, BFInterpreter):
                new = BFInterpreter(self.parent.stored + "<" + item.string, parent=self.parent)
                self.parent.stored = None
                item.chained = True
                return new
            else:
                return NotImplemented
        else:
            if isinstance(item, BFInterpreter):
                item.chained = True
                return BFInterpreter(self.string + "<" + item.string, parent=self.parent)
            else:
                return NotImplemented

    
    def __gt__(self, item):
        if self.parent.stored:
            if isinstance(item, BFInterpreter):
                new = BFInterpreter(self.parent.stored + ">" + item.string, parent=self.parent)
                self.parent.stored = None
                item.chained = True
                return new
            else:
                return NotImplemented
        else:
            if isinstance(item, BFInterpreter):
                item.chained = True
                return BFInterpreter(self.string + ">" + item.string, parent=self.parent)
            else:
                return NotImplemented
    
    def __lshift__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(self.string + "<<" + item.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter(self.string + "<<[" + self._unpack(*item) + "]", parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter(self.string + "<<...", parent=self.parent)
        else:
            return NotImplemented
    
    def __rshift__(self, item):
        if isinstance(item, BFInterpreter):
            return BFInterpreter(self.string + ">>" + item.string, parent=self.parent)
        elif isinstance(item, list):
            return BFInterpreter(self.string + ">>[" + self._unpack(*item) + "]", parent=self.parent)
        elif isinstance(item, type(...)):
            return BFInterpreter(self.string + ">>...", parent=self.parent)
        else:
            return NotImplemented

    def __getattr__(self, attr):
        if attr not in ("chained", "string", "parent", "stored"):
            return BFInterpreter(self.string + "." + attr, parent=self.parent)

    def __getitem__(self, arg):
        if isinstance(arg, BFInterpreter):
            return BFInterpreter(self.string + "[" + arg.string + "]", parent=self.parent)
        elif isinstance(arg, (list, tuple)):
            x = self._unpack(*arg)
            return BFInterpreter(self.string + "[" + x + "]", parent=self.parent)
        elif isinstance(arg, type(...)):
            return BFInterpreter(self.string + "[...]", parent=self.parent)
        else:
            return NotImplemented

    def _unpack(self, *args):
        items = []
        for arg in args:
            if isinstance(arg, BFInterpreter):
                items.append(arg.string)
            elif isinstance(arg, list):
                items.append("[" + self._unpack(*arg) + "]")
            elif isinstance(arg, type(...)):
                items.append("...")
        return ",".join(items)

    def interpret(self, *args):
        '''
        Interprets Brainfuck code, given source code as Python.

        Each element in `*args` must be an instance of `BFInterpreter`.
        '''
        source = self._unpack(*args).replace("_", "")

        print(f"Source code: {source}")
        print(f"Output: ", end="")

        prg_ptr = 0
        tape_ptr = 0
        tape = [0] * 30000
        stack = []
        i = 0
        while prg_ptr < len(source):
            instr = source[prg_ptr]
            cell = tape[tape_ptr]
            
            # Side-effects
            if instr == "+":
                tape[tape_ptr] += 1
                tape[tape_ptr] %= 256
            elif instr == "-": 
                tape[tape_ptr] -= 1
                tape[tape_ptr] %= 256
            elif instr == ">":
                tape_ptr += 1
                tape_ptr %= 30000
            elif instr == "<":
                tape_ptr -= 1
                tape_ptr %= 30000
            elif instr == ".":
                print(chr(cell % 256), end="")
            elif instr == ",":
                tape[tape_ptr] = ord(sys.stdin.read(1))
            elif instr == "[":
                stack.insert(0, prg_ptr)
            elif instr == "]":
                if cell == 0:
                    stack.pop(0)
                else:
                    prg_ptr = stack[0]

            prg_ptr += 1
            i += 1

        print()

if __name__== "__main__":
    # This program has 3 distinct layers of execution
    _,__,___ = BFInterpreter[3]
    # Prints "Hello, world!"
    _.interpret(
        +_[+__[___<<___<+___>>___>>___]+__<-__<-__<<__<+__<++__]<<_._<++_._<++_._._+++_._<<++_._<---_._>>_._>_._+++_._------_._>-_._>>--_._
    )