def ok():
    print("""
    
// a) Eliminate comment lines

%{
#include<stdio.h>
int sl=0;
int ml=0;
%}
%%
"/*"[a-zA-Z0-9' '\t\n]+"*/"	ml++;
"//".*	sl++;
%%
main()
{
	yyin=fopen("f1.c","r");
	yyout=fopen("f2.c","w");
	yylex();
	fclose(yyin);
	fclose(yyout);
	printf("\n Number of single line comments are = %d\n",sl); printf("\nNumber of multiline comments are =%d\n",ml);
}



// b) RECOGNIZE IDENTIFIER, OPERATORS & KEYWORDS

// LEX
%{
#include <stdio.h>
#include "y.tab.h"
extern yylval;
%}
%%
[ \t];
[+|-|*|/|=|<|>] {printf("operator is %s\n",yytext);return OP;}
[0-9]+ {yylval = atoi(yytext); printf("numbers is %d\n",yylval); return DIGIT;} 
int|char|bool|float|void|for|do|while|if|else|return|void {printf("keyword is %s\n",yytext);return KEY;}
[a-zA-Z0-9]+ {printf("identifier is %s\n",yytext);return ID;}
. ;
%%

// YACC
%{
#include <stdio.h>
#include <stdlib.h>
int id=0, dig=0, key=0, op=0;
%}
%token DIGIT ID KEY OP
%%
input:
DIGIT input { dig++; }
| ID input { id++; }
| KEY input { key++; }
| OP input {op++;}
| DIGIT { dig++; }
| ID { id++; }
| KEY { key++; }
| OP { op++;}
;
%%
#include <stdio.h>
extern int yylex();
extern int yyparse();
extern FILE *yyin;
main() 
{
	FILE *myfile = fopen("inputfile.c", "r"); 
	if (!myfile) 
	{
		printf("I can't open inputfile.c!");
		return -1;
	}
	yyin = myfile;
	do{
		yyparse();
	}while (!feof(yyin));
	printf("numbers = %d\nKeywords = %d\nIdentifiers = %d\noperators = %d\n",dig, key,id, op);
}

void yyerror() {
	printf("EEK, parse error! Message: ");
	exit(-1);
}


    """)