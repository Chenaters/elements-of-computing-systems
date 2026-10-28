module switch_prime (
  input  wire SW1, 
  input  wire SW2,
  input  wire SW3, 
  input  wire SW4,
  output wire LED1, // result

);
  wire [3:0] switches;
  assign switches = {SW4, SW3, SW2, SW1};  // order matters!
  assign LED1 =  (switches==2) || (switches == 3) || (switches == 5)
   || (switches == 7) || (switches == 11) || (switches == 13);



endmodule