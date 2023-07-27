#include <stdio.h>
#include <stdarg.h>
#include "calc.h"

int success = 1;

void Error( char *Str, ... )
{
  va_list ap;

  printf("ERROR: ");
  va_start(ap, Str);
  vprintf(Str, ap);
  va_end(ap);
  printf("\n");

  success = 0;
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

  while (success) {
      ClearQueue(&Q);
      ClearQueue(&QRes);
      ClearStack(&StackEval);
      ClearVars();

      printf("Expression: ");
      GetStr(Str, MAX);
      Scanner(&Q, Str);
      Parser(&QRes, &Q);
      printf("Result: %f\n", Eval(&QRes));
      printf("\nPress ENTER to continue or Ctrl-C to exit...");
      getchar();
  }
}
