// Application of Speedreducer protocol [DHT04]
// on top of Herman's self stabilising algorithm as given in [KMOWZ11]
// Random pass interpretation
// Second variant

// the procotol is synchronous with no nondeterminism (a DTMC)
dtmc

// Probability of passing token along in speed reducer mode
const double r;

// Probability to switch from speed reducer to normal mode
const double p; // = 1/n
// Probability to switch from normal to speed reducer mode
const double q; // = 1/(n*(n-1))

// module process 1
module process1

	// Variable for process 1
	x1 : [0..1];

    // Variable indicating which mode is used
    // 0 -> normal mode
    // 1 -> just switched to speedreducer mode
    // 2 -> speedreducer mode
    m1 : [0..2] init 0;

    [initial] (c=0) -> 1/2 : (x1'=0)
                     + 1/2 : (x1'=1);

    // Step
	[step] (c=1 & x1!=x0) -> true; // No token
	[step] (c=1 & x1=x0 & m1=0) -> (x1'=1-x1); // Token in normal mode
	[step] (c=1 & x1=x0 & m1=2) -> r : (x1'=1-x1) + 1-r : (x1'=x1); // Token in speed reducer mode
    // Switching between modes
    [switch_sr] (m1=0)  -> q : (m1'=1) + 1-q : true;
    [switch_sr] (m1!=0) -> true;
    [switch_n]  (m1=0)  -> true;
    [switch_n]  (m1=1)  -> (m1'=2);
    [switch_n]  (m1=2)  -> p : (m1'=0) + 1-p : true;

endmodule

// add further processes through renaming
module process2 = process1 [ x1=x2, x0=x1, m1=m2 ] endmodule
module process3 = process1 [ x1=x3, x0=x2, m1=m3 ] endmodule
module process4 = process1 [ x1=x4, x0=x3, m1=m4 ] endmodule
module process5 = process1 [ x1=x5, x0=x4, m1=m5 ] endmodule
module process6 = process1 [ x1=x6, x0=x5, m1=m6 ] endmodule
module process7 = process1 [ x1=x7, x0=x6, m1=m7 ] endmodule
module process8 = process1 [ x1=x8, x0=x7, m1=m8 ] endmodule
module process9 = process1 [ x1=x9, x0=x8, m1=m9 ] endmodule
module process10 = process1 [ x1=x10, x0=x9, m1=m10 ] endmodule
module process11 = process1 [ x1=x11, x0=x10, m1=m11 ] endmodule
module process12 = process1 [ x1=x12, x0=x11, m1=m12 ] endmodule
module process13 = process1 [ x1=x13, x0=x12, m1=m13 ] endmodule
module process14 = process1 [ x1=x14, x0=x13, m1=m14 ] endmodule
module process15 = process1 [ x1=x15, x0=x14, m1=m15 ] endmodule
module process16 = process1 [ x1=x16, x0=x15, m1=m16 ] endmodule
module process17 = process1 [ x1=x17, x0=x16, m1=m17 ] endmodule
module process18 = process1 [ x1=x18, x0=x17, m1=m18 ] endmodule
module process0 = process1 [ x1=x0, x0=x18, m1=m0 ] endmodule

// General control module
module control
    // Phases for control loop:
    // 0: init processes
    // 1: step
    // 2: switch to speedreducer
    // 3: switch to normal mode
    c : [0..3] init 0;

    [initial]   (c=0) -> 1 : (c'=1);
    [step]      (c=1) -> 1 : (c'=2);
    [switch_sr] (c=2) -> 1 : (c'=3);
    [switch_n]  (c=3) -> 1 : (c'=1);
endmodule

formula phase_step  = c=1; // Marks phase of synchronous step

// cost - 1 in each state (expected number of steps)
rewards "steps"
	phase_step : 1;
endrewards

// formula for number of tokens
formula num_tokens = (x1=x0?1:0)
                    +(x2=x1?1:0)
                    +(x3=x2?1:0)
                    +(x4=x3?1:0)
                    +(x5=x4?1:0)
                    +(x6=x5?1:0)
                    +(x7=x6?1:0)
                    +(x8=x7?1:0)
                    +(x9=x8?1:0)
                    +(x10=x9?1:0)
                    +(x11=x10?1:0)
                    +(x12=x11?1:0)
                    +(x13=x12?1:0)
                    +(x14=x13?1:0)
                    +(x15=x14?1:0)
                    +(x16=x15?1:0)
                    +(x17=x16?1:0)
                    +(x18=x17?1:0)
                    +(x0=x18?1:0);

// label for stable configurations with exactly one token
label "stable" = phase_step & num_tokens=1;


// labels useful for debugging
label "initialized" = c>0;
