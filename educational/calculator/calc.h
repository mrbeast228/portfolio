
#ifdef _DEBUG
#define _CRTDBG_MAP_ALLOC
#include <crtdbg.h>
#define SetDbgMemHooks() \
  _CrtSetDbgFlag(_CRTDBG_LEAK_CHECK_DF | _CRTDBG_CHECK_ALWAYS_DF | \
    _CRTDBG_ALLOC_MEM_DF | _CrtSetDbgFlag(_CRTDBG_REPORT_FLAG))
#else
#define SetDbgMemHooks() ((void)0)
#endif
#include <stdlib.h>

#define MAX 255

typedef enum
{
  TOK_OP,
  TOK_NUM,
  TOK_VAR
} TOKID;

typedef struct
{
  TOKID Id;
  char Op;
  double Num;
  char Name[MAX];
} TOKEN;

typedef struct tagLIST LIST;
struct tagLIST
{
  TOKEN T;
  LIST *Next;
};

typedef struct
{
  LIST
    *Head,
    *Tail;
} QUEUE;

typedef struct
{
  LIST
    *Top;
} STACK;

extern STACK StackEval;

void GetStr( char *str, int max );
void Error( char *Str, ... );
void Put( QUEUE *Q, TOKEN NewData );
int Get( QUEUE *Q, TOKEN *OldData );
void Push( STACK *S, TOKEN NewData );
int Pop( STACK *S, TOKEN *OldData );
void DisplayStack( STACK *S );
void DisplayQueue( QUEUE *Q );
void ClearStack( STACK *S );
void ClearQueue( QUEUE *Q );
void Scanner( QUEUE *Q, char *Str );
double Eval( QUEUE *Q );
void Parser( QUEUE *QRes, QUEUE *Q );
void ClearVars( void );
void DisplayVars( void );
void SetVar( char *Name, double Value );
double GetVar( char *Name );
