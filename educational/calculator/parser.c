#include "calc.h"

QUEUE Queue1 = {NULL};
STACK Stack2 = {NULL};

int GetPrior( char Op )
{
  switch (Op)
  {
  case ',':
    return -2;
  case '=':
    return -1;
  case '+':
  case '-':
    return 0;
  case '*':
  case '/':
  case '%':
    return 1;
  case '^':
    return 2;
  case '@':
    return 3;
  case ')':
    return -3;
  case '(':
    return -4;
  }
  Error("Unknown operator: %c", Op);
  return -32767;
}

int CheckPriority( char Op )
{
  int
    p1 = GetPrior(Stack2.Top->T.Op),
    p2 = GetPrior(Op);

  if (Op == '=')
    return p1 > p2;
  return p1 >= p2;
}

void DropOpers( char Op )
{
  while (Stack2.Top != NULL &&
         CheckPriority(Op))
  {
    TOKEN T;

    Pop(&Stack2, &T);
    Put(&Queue1, T);
  }
}

void Parser( QUEUE *QRes, QUEUE *Q )
{
  TOKEN T;

  while (Get(Q, &T))
    if (T.Id == TOK_NUM || T.Id == TOK_VAR)
      Put(&Queue1, T);
    else if (T.Id == TOK_OP)
    {
      if (T.Op != '(')
        DropOpers(T.Op);
      if (T.Op != ')')
        Push(&Stack2, T);
      else
        if (!Pop(&Stack2, NULL))
        {
            Error("Missing '('");
            break;
        }
    }
    else {
        Error("Syntax error");
        break;
    }

  DropOpers(')');
  if (Stack2.Top != NULL)
    Error("Missing ')'");
  *QRes = Queue1;
  Queue1.Head = NULL;
}
