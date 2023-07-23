#include <stdio.h>
#include <string.h>
#include "calc.h"

typedef struct tagVARTREE VARTREE;
static struct tagVARTREE
{
  VARTREE *Less, *More;
  double Value;
  char Name[MAX];
} *Vars;

void SetVar( char *Name, double Value )
{
  VARTREE **T = &Vars;
  int n;

  while (*T != NULL &&
         (n = strcmp((*T)->Name, Name)) != 0)
    T = n > 0 ? (&(*T)->Less) : (&(*T)->More);
  if (*T == NULL)
  {
    if ((*T = malloc(sizeof(VARTREE))) == NULL)
      Error("Not enough memory");
    strncpy((*T)->Name, Name, MAX - 1);
    (*T)->Less = (*T)->More = NULL;
  }
  (*T)->Value = Value;
}

double GetVar( char *Name )
{
  VARTREE **T = &Vars;
  int n;

  while (*T != NULL &&
         (n = strcmp((*T)->Name, Name)) != 0)
    T = n > 0 ? (&(*T)->Less) : (&(*T)->More);
  return *T == NULL ? 0 : (*T)->Value;
}

void PutTree( VARTREE *T )
{
  if (T != NULL)
  {
    printf("%s = %f,", T->Name, T->Value);
    PutTree(T->Less);
    PutTree(T->More);
  }
}

void ClearTree( VARTREE **T )
{
  if (*T != NULL)
  {
    ClearTree(&(*T)->Less);
    ClearTree(&(*T)->More);
    free(*T);
    *T = NULL;
  }
}

void DisplayVars( void )
{
  PutTree(Vars);
}

void ClearVars( void )
{
  VARTREE **T = &Vars;
  ClearTree(T);
}
