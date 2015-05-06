/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

grammar nlquery;
options {
    language = Python;
    }
NUM : ('0'..'9')+;
UNIT : 'km'|'mile'|'miles' |'m';
WORD : ('a'..'z'|'A'..'Z')+;
WS  :   (' '|'\t')+ {$channel=HIDDEN};
term :WORD+;
location : (WORD | ',')+;
range : NUM UNIT;
query : term ('in' location)? ('with' exp)? ('within' range ('of' location)? | 'near' ('me' | location) )?;
exp : exp 'and' exp | exp 'or' exp | 'not' exp | term ('more' | 'less') 'than' value | term 'between' value 'and' value;
value : NUM UNIT?;
