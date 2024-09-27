dtmc

// timing:
// tick-0:
//     queue state is observed and state change is planned (pm)
//     request are generated (if service requester is active)
// tick-1:
//     requests are served
//     state change is executed
//     service requester changes its state
//     battery depletes

// initial queue size
const int q_init = 0;

// ----- synthesized parameters ------------------------------------------------

// profiles desired at observation levels
// hole int P1 in {0,1,2};
// hole int P2 in {0,1,2};
// hole int P3 in {0,1,2};
// hole int P4 in {0,1,2};
const double P11;
const double P12;
const double P21;
const double P22;
const double P31;
const double P32;
const double P41;
const double P42;

// observation level thresholds
// hole double T1 in {0.0,0.1,0.2,0.3,0.4};
// hole double T2 in {0.5};
// hole double T3 in {0.6,0.7,0.8};

const double T1 = 2.5;
const double T2 = 5;
const double T3 = 7.5;

// const double T1;
// const double T2;
// const double T3;

// const double empty = 0.01;
// const double startsend = 0.5;
// const double contsend = 0.8;

const double empty;
const double startsend;
const double contsend;

// queue size
// hole int QMAX in {1,2,3,4,5,6,7,8,9,10};
const int QMAX = 10;

// ----- modules ---------------------------------------------------------------


// clock

module CLOCK
    c : [0..1] init 0;
    [tick0] c=0 -> (c'=1);
    [tick1] c=1 -> (c'=0);
endmodule


// simple power manager
module PM
    pm     :  [0..2] init 0; // 0 - sleep, 1 - idle, 2 - active
    state  :  [0..1] init 0; // internal state

    [tick0] state=0 & q*10 <= T1*QMAX -> P11 : (pm'=0) + (1-P11) : (state'=1);
    [tick0] state=1 & q*10 <= T1*QMAX -> P12 : (pm'=1) & (state'=0) + (1-P12) : (pm'=2) & (state'=0);

    [tick0] state=0 & q*10 > T1*QMAX & q*10 <= T2*QMAX -> P21 : (pm'=0) + (1-P21) : (state'=1);
    [tick0] state=1 & q*10 > T1*QMAX & q*10 <= T2*QMAX -> P22 : (pm'=1) & (state'=0) + (1-P22) : (pm'=2) & (state'=0);

    [tick0] state=0 & q*10 > T2*QMAX & q*10 <= T3*QMAX -> P31 : (pm'=0) + (1-P31) : (state'=1);
    [tick0] state=1 & q*10 > T2*QMAX & q*10 <= T3*QMAX -> P32 : (pm'=1) & (state'=0) + (1-P32) : (pm'=2) & (state'=0);

    [tick0] state=0 & q*10 > T3*QMAX -> P41 : (pm'=0) + (1-P41) : (state'=1);
    [tick0] state=1 & q*10 > T3*QMAX -> P42 : (pm'=1) & (state'=0) + (1-P42) : (pm'=2) & (state'=0);
endmodule

// service provider

module SP
    sp : [0..4] init 0;
    // 0 - sleep, 1 - idle, 2 - active
    // waiting states: 3 - sleep to idle, 4 - idle to active

    // immediate transitions - change to lower-energy (or same) state
    [tick1] sp <= 2 & pm <= sp -> (sp'=pm);

    // transitions through waiting states - change to higher-energy state (sleep to idle or idle to active)
    [tick1] sp <= 2 & pm > sp -> (sp'=sp+3);

    // waiting states
    [tick1] sp = 3 -> 0.8 : (sp'=sp-2) + 0.2 : true;
    [tick1] sp = 4 -> 0.6 : (sp'=sp-2) + 0.4 : true;

endmodule


// service requester

module SR
    sr : [0..1] init 0; // 0 - idle, 1 - active
    [tick1] sr=0 -> startsend: true + 1-startsend: (sr' = 1);
    [tick1] sr=1 -> contsend: true + 1-contsend: (sr' = 0);
endmodule


// service request queue

module SRQ
    q : [0..10000] init q_init;
    lost : [0..1] init 0;

    [tick0] sr=1 & q < QMAX -> (q'=q+1); // request
    [tick0] sr=1 & q = QMAX -> (lost'=1); // request lost
    [tick0] sr!=1 -> true;

    [tick1] sp=2 -> (lost'=0) & (q'=max(q-1,0)); // serve
    [tick1] sp!=2 -> (lost'=0);

endmodule

// battery

module BAT
    bat : [0..1] init 1; // 0 empty, 1 - operational
    [tick1] bat=0 ->true;
    [tick1] bat=1 -> empty : (bat'=0) + 1-empty : true;
endmodule

// ----- rewards ----------------------------------------------------------------

label "finished" = (bat = 0);

// rewards "time"
//     [tick0] true : 1;
// endrewards

rewards "queuesize"
    [tick0] true: q;
endrewards

// rewards "requests"
//     [tick0] sr=1 : 1;
// endrewards

// rewards "served"
//     [tick1] q > 0 & sp=2 : 1;
// endrewards

// rewards "lost"
//    [tick0] q=QMAX & sr=1 : 1;
// endrewards

// rewards "lost"
//     [tick1] lost=1 : 1;
// endrewards

// rewards "power"
//     [tick1] sp=2 : 100 + 10*q; // active
//     [tick1] sp=3 : 10; // idle to active
//     [tick1] sp=4 : 5; // sleep to idle
// endrewards
