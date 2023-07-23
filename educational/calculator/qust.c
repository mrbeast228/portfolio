#include <stdio.h>
#include "calc.h"

/* add to queue */
void Put( QUEUE *Q, TOKEN NewData )
{
  LIST *NewElement = malloc(sizeof(LIST));

  if (NewElement == NULL)
    Error("Memory error");
  NewElement->T = NewData;
  NewElement->Next = NULL;
  if (Q->Head == NULL)
    Q->Head = Q->Tail = NewElement;
  else
    Q->Tail->Next = NewElement, Q->Tail = NewElement;
}

/* remove from queue */
int Get( QUEUE *Q, TOKEN *OldData )
{
  LIST *OldElement = Q->Head;
      
  if (OldElement == NULL)
    return 0;
  Q->Head = Q->Head->Next;

  if (OldData != NULL)
    *OldData = OldElement->T;
  free(OldElement);
  return 1;
}

/* add to stack */
void Push( STACK *S, TOKEN NewData )
{
  LIST *NewElement = malloc(sizeof(LIST));

  if (NewElement == NULL)
    Error("Memory error");
  NewElement->T = NewData;
  NewElement->Next = S->Top;
  S->Top = NewElement;
}

/* remove from stack */
int Pop( STACK *S, TOKEN *OldData )
{
  LIST *OldElement = S->Top;
      
  if (OldElement == NULL)
    return 0;
  S->Top = S->Top->Next;

  if (OldData != NULL)
    *OldData = OldElement->T;
  free(OldElement);
  return 1;
}

void PrintToken( TOKEN T )
{
  if (T.Id == TOK_NUM)
    printf("a:%f\n", T.Num);
  else if (T.Id == TOK_OP)
    printf("o:%c\n", T.Op);
  else if (T.Id == TOK_VAR)
    printf("v:%s\n", T.Name);
  else
    Error("Error token");
}

void DisplayList( LIST *L )
{
  if (L == NULL)
    printf("<Empty>\n");
  else
    while (L != NULL)
    {
      PrintToken(L->T);
      L = L->Next;
    }
}

void ClearList( LIST **L )
{
  LIST *OldElement = *L;

  while (OldElement != NULL)
  {
    *L = (*L)->Next;
    free(OldElement);
    OldElement = *L;
  }
}

void DisplayStack( STACK *S )
{
  DisplayList(S->Top);
}

void DisplayQueue( QUEUE *Q )
{
  DisplayList(Q->Head);
}

void ClearStack( STACK *S )
{
  ClearList(&S->Top);
}

void ClearQueue( QUEUE *Q )
{
  ClearList(&Q->Head);
}
