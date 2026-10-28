`timescale 1ns/1ps
module simple_switch_tb;
  reg SW1 = 0;
  reg SW2 = 0;
  reg SW3 = 0;
  wire LED1;
  wire LED4;

  simple_switch dut(.SW1(SW1), .SW2(SW2), .SW3(SW3), .LED1(LED1), .LED4(LED4));

  initial begin
    $dumpfile("simple_switch.vcd");
    $dumpvars(0, simple_switch_tb);

    // test all combinations
    #10 SW1 = 0; SW2 = 0; SW3 = 0;
    #10 SW1 = 0; SW2 = 1; SW3 = 0;
    #10 SW1 = 1; SW2 = 0; SW3 = 0;
    #10 SW1 = 1; SW2 = 1; SW3 = 0;
    #10 SW1 = 0; SW2 = 0; SW3 = 1;
    #10 SW1 = 0; SW2 = 1; SW3 = 1;
    #10 SW1 = 1; SW2 = 0; SW3 = 1;
    #10 SW1 = 1; SW2 = 1; SW3 = 1;

    #10 $finish;
  end
endmodule
