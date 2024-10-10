// Application of Speedreducer protocol [DHT04]
// on top of Herman's self stabilising algorithm as given in [KMOWZ11]
// Random pass interpretation
// Second variant

// the procotol is synchronous with no nondeterminism (a DTMC)
dtmc

// Probability of passing token along in speed reducer mode
const double r;

// Probability to switch from speed reducer to normal mode
const double p;
// Probability to switch from normal to speed reducer mode
const double q;

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
module process0 = process1 [ x1=x0, x0=x2, m1=m0 ] endmodule

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
                    +(x0=x2?1:0);

// label for stable configurations with exactly one token
label "stable" = phase_step & num_tokens=1;


// labels useful for debugging
label "initialized" = c>0;
