module SwitchOp (
  input  wire SW1,
  input  wire SW2,
  input  wire SW3,  // selector
  output wire LED1, // result
  output wire LED4  // status 
);

  assign LED1 = (SW3 == 1'b0) ? (SW1 + SW2) : (SW1 & SW2);


  assign LED4 = 1'b1;

endmodule