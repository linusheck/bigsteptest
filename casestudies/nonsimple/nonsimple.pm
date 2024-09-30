
dtmc

const double p1;
const double p2;
const double p3;
const double p4;
const double p5;
const double p6;
const double p7;
const double p8;

module nonsimple
    s : [0..10] init 0;
    
    [] s=0 ->
        p1 : (s'=1) +
        p2 : (s'=2) +
        p3 : (s'=3) +
        p4 : (s'=4) +
        p5 : (s'=5) +
        p6 : (s'=6) +
        p7 : (s'=7) +
        p8 : (s'=8);
    [] s=1 -> 1/1 : (s'=9) + (1-1/1) : (s'=10);
    [] s=2 -> 1/2 : (s'=9) + (1-1/2) : (s'=10);
    [] s=3 -> 1/3 : (s'=9) + (1-1/3) : (s'=10);
    [] s=4 -> 1/4 : (s'=9) + (1-1/4) : (s'=10);
    [] s=5 -> 1/5 : (s'=9) + (1-1/5) : (s'=10);
    [] s=6 -> 1/6 : (s'=9) + (1-1/6) : (s'=10);
    [] s=7 -> 1/7 : (s'=9) + (1-1/7) : (s'=10);
    [] s=8 -> 1/8 : (s'=9) + (1-1/8) : (s'=10);
    
endmodule

label "target" = s=9;
