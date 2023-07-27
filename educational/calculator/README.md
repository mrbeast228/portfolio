# Expressions calculator
This program can eval mathematical expressions with variables. It uses syntax and lexical analyzers and should have been a full programming language, but academic year of 10th grade ended earlier :(

## Requirments
+ C compiler (backward compatible with C++)
+ math library (-lm)

## Building
At first, we need to build it. We can use Visual C++, CLion, VS Code, or anything else. We also can directly build it with gcc
```
gcc eval.c parser.c qust.c scanner.c t35calc.c vars.c -lm -o calculator
./calculator
```

## Usage
Calculator support all classic math operations, variable definition and brackets priority ('^' is exponentiation)
```
Expression: 2 + 4
Result: 6.000000

Press ENTER to continue or Ctrl-C to exit...
Expression: x = (2 + 1) * 2, (x + 4) / 7
Result: 1.428571

Press ENTER to continue or Ctrl-C to exit...
Expression: x = 4 + (11 / 3), y = (2 * x + 4) / 7, z = y * y - 12, (z * 2 + 10) ^ 5
Result: 3.128642

Press ENTER to continue or Ctrl-C to exit...
```
Calculator is looped, so it will prompt you to enter the expression untill you press Ctrl-C
