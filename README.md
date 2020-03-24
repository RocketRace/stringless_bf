# stringless_bf

`no_strings.py` is a proof-of-concept Python module dedicated to parsing and interpreting languages without taking strings as "source code" for
the interpreter. It currently features an interpreter for stringless Brainf*ck (BF). An example is shown below:

```py
# Raw source code: "+[+[<<<+>>>>]+<-<-<<<+<++]<<.<++.<++..+++.<<++.<---.>>.>.+++.------.>-.>>--."
# Stringless version: +_[+__[___<<___<+___>>___>>___]+__<-__<-__<<__<+__<++__]<<_._<++_._<++_._._+++_._<<++_._<---_._>>_._>_._+++_._------_._>-_._>>--_._
# Three objects are required due to implementation details, as the program has three layers of loops 
_,__,___ = BFInterpreter[3]
# Prints "Hello, world!"
_.interpret(
    +_[+__[___<<___<+___>>___>>___]+__<-__<-__<<__<+__<++__]<<_._<++_._<++_._._+++_._<<++_._<---_._>>_._>_._+++_._------_._>-_._>>--_._
)
```

*Note that due to how this module abuses the unary `+` and `-` operators, it is very likely to trigger linter errors.
As seen above, GitHub's Python syntax highlighting also complains about this.*


No other languages besides BF are currently planned for implementation.
