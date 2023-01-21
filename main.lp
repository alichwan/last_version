#include "traces.lp".


% Los parámetros como id, var y time serán dependientes de las traces que entren en juego.
id(Id) :- trace(Id,_,_).
var(Var) :- trace(_,Var,_).
time(0..MT) :- MT=#max{T: trace(_,_,T)}.

sat(Id, F) :- sat(Id, F, 0). %Una trace es satisfacible si su fórmula es satisfacible en tiempo 0

% se definien las subfórmulas,
subformula(F) :- theformula(F).

% queremos, filtrar si la fórmula satisface las traces positivas y rechaza las negativas
:- theformula(F), posTrace(Id), not sat(Id,F).
finalPosSat(Id) :- theformula(F), posTrace(Id), sat(Id,F).
:- theformula(F), negTrace(Id), sat(Id,F).
finalNegSat(Id) :- theformula(F), negTrace(Id), not sat(Id,F).

% operadores: satisfacibilidad y subformulabilidad
% not
sat(Id, F, T) :- F=f(not_,I), not sat(Id, I, T), id(Id), time(T), subformula(F), subformula(I).
subformula(I) :- F=f(not_,I), subformula(F).
% and
sat(Id, F, T) :- F=f(Op,I,D), binop(Op, and_), id(Id), time(T),sat(Id, I, T), sat(Id, D, T), subformula(F), subformula(I), subformula(D).
subformula(I) :- F=f(Op,I,D), binop(Op, and_), subformula(F).
subformula(D) :- F=f(Op,I,D), binop(Op, and_), subformula(F).
% or
sat(Id, F, T) :- F=f(Op,I,D), binop(Op, or_), id(Id), time(T), sat(Id, I, T), subformula(F), subformula(I).
sat(Id, F, T) :- F=f(Op,I,D), binop(Op, or_), id(Id), time(T), sat(Id, D, T), subformula(F), subformula(D).
subformula(I) :- F=f(Op,I,D), binop(Op, or_), subformula(F).
subformula(D) :- F=f(Op,I,D), binop(Op, or_), subformula(F).
% next
sat(Id, F, T-1) :- F=f(Op,I), unop(Op, next_), sat(Id, I, T), id(Id), time(T), subformula(F), subformula(I), T>0.
subformula(I)   :-  F=f(Op,I), unop(Op, next_), subformula(F).
% eventually
sat(Id, F, T) :- F=f(Op,I), unop(Op, eventually_), sat(Id, I, Tp), Tp>=T, time(T), time(Tp), id(Id), subformula(F), subformula(I).
subformula(I) :- F=f(Op,I), unop(Op, eventually_), subformula(F).
% always
sat(Id, F, T) :- F=f(Op,I), unop(Op, always_), subformula(I), satbetween(Id, I, T, Tf), Tf=#max{Taux: trace(Id,_,Taux)}.
subformula(I) :- F=f(Op,I), unop(Op, always_), subformula(F).
% until  - id(Id), subformula(F), time(T), time(Taux), 
sat(Id, F, T) :-  F=f(Op,I,D), binop(Op, until_), satbetween(Id, I, T, T1), sat(Id,D,T1+1), subformula(I), subformula(D).
subformula(I) :- F=f(Op,I,D), binop(Op, until_), subformula(F).
subformula(D) :- F=f(Op,I,D), binop(Op, until_), subformula(F).
% satbetween : auxiliar para los "temporalmente conexos" como until_ o always_
satbetween(Id, F, T, T)   :- sat(Id, F, T), time(T).
satbetween(Id, F, T1, T2)   :- satbetween(Id, F, T1+1, T2), sat(Id, F, T1).
% -------------fin de operadores---------

% -------------hojas---------
% Por abajo, las hojas deben ser subformulas y satisfacibles.
% subformula(H) :- trace(Id, Var, T), id(Id), time(T), var(Var), predVar(Pred, Var), H=h(Pred).
% % Satisfacibilidad de las hojas
sat(Id, H, T) :- trace(Id, Var, T), id(Id), time(T), var(Var), predVar(Pred, Var), H=h(Pred), subformula(H).
% -------------fin de hojas---------

% -------------operadores abstractos---------
1{predVar(Pred, Var): var(Var)}1 :- predicate(Pred).
1{unop(Op, not_); unop(Op, next_); unop(Op, eventually_); unop(Op, always_)}1 :- unary(Op).
1{binop(Op, and_); binop(Op, or_); binop(Op, until_)}1 :- binary(Op).
% -------------fin de operadores abstractos---------

% #show sat/2.
% #show finalPosSat/1.
% #show finalNegSat/1.
% #show subformula/1.
#show theformula/1.
#show predVar/2.
#show unop/2.
#show binop/2.