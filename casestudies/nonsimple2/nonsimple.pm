
dtmc

const double p0;
const double p1;
const double p2;
const double p3;

module nonsimple
    s : [0..6] init 0;
    
    [] s=0 ->
        0.5 : (s'=1) + 0.5 : (s'=5);
    [] s=1 ->
        p1 : (s'=1) +
        p2 : (s'=2) +
        p3 : (s'=3)
        1-p1-p2-p3 : (s'=4);
    [] s=2 -> 1/2 : (s'=5) + 1-1/2 : (s'=6);
    [] s=3 -> 1/3 : (s'=5) + 1-1/3 : (s'=6);
    [] s=4 -> 1/4 : (s'=5) + 1-1/4 : (s'=6);
    
endmodule

label "target" = s=5;
