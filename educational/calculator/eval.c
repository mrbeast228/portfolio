#include <math.h>
#include "calc.h"

STACK StackEval = {NULL};

double Eval( QUEUE *Q )
{
  TOKEN T;

  while (Get(Q, &T))
  {
    if (T.Id == TOK_NUM || T.Id == TOK_VAR)
      Push(&StackEval, T);
    else
    {
      TOKEN A, B;

      if (T.Op != '@')
        if (!Pop(&StackEval, &B))
          Error("Eval error");
        else
          if (B.Id == TOK_VAR)
            B.Num = GetVar(B.Name);
      if (!Pop(&StackEval, &A))
        Error("Eval error");
      else
        if (A.Id == TOK_VAR && T.Op != '=')
          A.Num = GetVar(A.Name);

      switch (T.Op)
      {
      case '=':
        if (A.Id != TOK_VAR)
          Error("LValue required");
        SetVar(A.Name, B.Num);
        /* ??? */
        break;
      case ',':
        A.Num = B.Num;
        A.Id = TOK_NUM;
        break;
      case '+':
        A.Num += B.Num;
        A.Id = TOK_NUM;
        break;
      case '@':
        A.Num *= -1;
        A.Id = TOK_NUM;
        break;
      case '-':
        A.Num -= B.Num;
        A.Id = TOK_NUM;
        break;
      case '*':
        A.Num *= B.Num;
        A.Id = TOK_NUM;
        break;
      case '/':
        A.Num /= B.Num;
        A.Id = TOK_NUM;
        break;
      case '%':
        A.Num = fmod(A.Num, B.Num);
        A.Id = TOK_NUM;
      case '^':
        A.Num = pow(A.Num, B.Num);
        A.Id = TOK_NUM;
        break;
      default:
        Error("Unknown operation '%c' in eval", T.Op);
      }
      Push(&StackEval, A);
    }
  }
  Pop(&StackEval, &T);
  return T.Num;
}
