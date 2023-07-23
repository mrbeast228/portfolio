#include <stdio.h>
#include <setjmp.h>
#include <stdarg.h>
#include "calc.h"

jmp_buf ExprJumpBuf;

void Error( char *Str, ... )
{
  va_list ap;

  printf("ERROR: ");
  va_start(ap, Str);
  vprintf(Str, ap);
  va_end(ap);
  printf("\n");
  longjmp(ExprJumpBuf, 1);
}

void GetStr( char *str, int max )
{
  char ch;
  int i = 0;

  while ((ch = getchar()) != '\n')
    if (str != NULL && i < max - 1)
      str[i++] = ch;
  if (str != NULL && i < max)
    str[i] = 0;
}

void main( void )
{
  char Str[MAX];
  QUEUE Q = {NULL}, QRes = {NULL};

  SetDbgMemHooks();

  if (setjmp(ExprJumpBuf))
  {
    ClearQueue(&Q);
    ClearQueue(&QRes);
    ClearStack(&StackEval);
    ClearVars();
    getchar();
    return;
  }

  printf("Expression: ");
  GetStr(Str, MAX);
  Scanner(&Q, Str);
  printf("Scanned queue:\n");
  DisplayQueue(&Q);
  Parser(&QRes, &Q);
  printf("Parsed queue:\n");
  DisplayQueue(&QRes);
  printf("Result: %f\n", Eval(&QRes));
  printf("Variables: ");
  DisplayVars();

  longjmp(ExprJumpBuf, 1);
}
