% defining the prefix tree.

% % -----------------------ex1-----------
% % Nodes
% node(0..7).
% % q0
% root(0).
% % F = positive ones
% pos(1;4;6;7).
% % Sigma
% sigma("a"; "b"; "c").
% % branch
% branch(0,"a",1).
% branch(1,"c",3).
% branch(3,"a",7).
% branch(0,"b",2).
% branch(2,"a",4).
% branch(2,"b",5).
% branch(2,"c",6).

% % -----------------------ex2-----------
% % Nodes
% node(0..19).
% % q0
% root(0).
% % F = positive ones
% pos(1;2;11;14;15;8;17;19;9).
% neg(5;7;10;12;13;16;18).
% % Sigma
% sigma("a"; "b"; "c";"d";"e").
% % branch
% branch(0,"a",1).
% branch(0,"b",2).
% branch(0,"c",3).
% branch(1,"a",4).
% branch(4,"e",5).
% branch(2,"e",6).
% branch(2,"c",7).
% branch(6,"d",11).
% branch(6,"c",12).
% branch(6,"b",13).
% branch(12,"b",14).
% branch(7,"a",15).
% branch(3,"e",9).
% branch(9,"b",19).
% branch(3,"d",8).
% branch(8,"e",16).
% branch(16,"b",17).
% branch(16,"c",19).
% branch(16,"d",18).

% --------------------------------------------
% definig the final automata  
% Q
% #const maxStates = 10.
state(0..maxStates).
% q0
q0(0).
% Sigma
% Same as tree

% definig the mapping  
% + rest: raiz se mapea a estado 0
mapping(0,0).
% + rest: cada nodo es asignado a exactamente 1 estado asignado
1{mapping(N,Q): state(Q)}1 :- node(N).
% No puede haber un mapeo que lleve un nodo neg y otro pos al mismo esado
:- mapping(N1, Q), mapping(N2, Q), pos(N1), neg(N2).

% JB: no hacer mapping a un estado Q si no se ha hecho a Q-1
mapped(Q) :- mapping(_,Q).
:- mapping(N,Q), Q>0, not mapped(Q-1).

% delta exhaustivo
delta(Q1,S,Q2) :- state(Q1;Q2), mapping(N1,Q1), mapping(N2,Q2), node(N1;N2), branch(N1, S, N2), sigma(S).
% + rest: para cada estado destino, solo se puede tener 1 par estado original
%% 0{delta(Q1,S,Q2): state(Q2)}1 :- state(Q1), sigma(S).
:- delta(Q1,S,Q2), delta(Q1,S,Q3), Q2!=Q3. %%% JB - CAMBIO: la cambié por esta, revisa por favor.
%  no puede haber un delta desde o hasta un estado que no se está usando.
%:- delta(Q,_,_), not mapping(_,Q).  %%% JB - PREGUNTA: por la linea 71, esto no debiera pasar, cierto?
%:- delta(_,_,Q), not mapping(_,Q).  %%% JB - PREGUNTA: por la linea 71, esto no debiera pasar, cierto?

% F
%%% JB - PREGUNTA: acceptState será mejor nombre que finalPos
%%% finalPos(Q) :- state(Q), mapping(N,Q), node(N), pos(N).
%%% JB - CAMBIO la linea anterior por esta:
finalPos(Q) :- mapping(N,Q), pos(N).
%%% JB - PREGUNTA: probé borrar la línea siguiente, pues no debiera ser necesaria dado que finalPos solo se asigna positivos según la línea anterior la linea anterior por esta. SIN EMBARGO, noté que aumentó el tiempo. Sería interesante entender por qué
:- finalPos(Q), neg(N), mapping(N,Q). % Si tengo nodo negativo no puedo terminaren aceptación

% explicitar negativos
%%% JB - PREGUNTA: finalNeg no se usa en ninguna parte más, cierto?
finalNeg(Q) :- state(Q), not finalPos(Q), mapping(_,Q).

% minimizing the state to use in the automata 
%%% JB - COMENTARIO: simplemente para experimentar, probaría si es más rápido haciendo llamados 
%%%                  sucesivos a clingo pidiendo un número cada vez mejor de statesUsed
statesUsed(Qs) :- Qs=#max{Q: mapping(_,Q)}.
#minimize{Q : statesUsed(Q)}. 

% q0 has no relevance
% important states == 0..min{q: mapping(_,_,q)}
#show finalPos/1.
#show finalNeg/1.
#show sigma/1.
#show mapping/2.
#show delta/3.

