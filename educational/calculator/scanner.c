#include <stdio.h>
#include <ctype.h>
#include "calc.h"

typedef unsigned char uchar;
void Scanner( QUEUE *Q, char *Str )
{
  TOKEN T;
  double denum;

  while (*Str != 0)
  {
    if (isspace((uchar)*Str))
      Str++;
    else if (isdigit((uchar)*Str))
    {
      T.Id = TOK_NUM;
      T.Num = 0;
      while (isdigit((uchar)*Str))
        T.Num = T.Num * 10 + (*Str++ - '0');
      if (*Str == '.')
      {
        denum = 10;
        Str++;
        while (isdigit((uchar)*Str))
          T.Num += (*Str++ - '0') / denum, denum *= 10;
      }
      Put(Q, T);
    }
    else if (*Str == '+' ||
             *Str == '-' ||
             *Str == '*' ||
             *Str == '/' ||
             *Str == '%' ||
             *Str == '^' ||
             *Str == '(' ||
             *Str == ')' ||
             *Str == '@' ||
             *Str == '=' ||
             *Str == ',')
    {
      T.Id = TOK_OP;
      T.Op = *Str++;
      Put(Q, T);
    }
    else if (isalpha((unsigned char)*Str))
    {
      int i = 0;

      T.Id = TOK_VAR;
      do
      {
        if (i < MAX - 1)
          T.Name[i++] = *Str;
        Str++;
      } while (isalpha((unsigned char)*Str) || isdigit((unsigned char)*Str));
      T.Name[i] = 0;
      Put(Q, T);
    }
    else {
        Error("Unrecognized character '%c'", *Str);
        break;
    }
  }
}
