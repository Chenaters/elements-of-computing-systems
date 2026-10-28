//------------------------------------------------------------------
//-- Verilog template
//-- Top entity
//-- Board: Nandland go-board
//------------------------------------------------------------------
`default_nettype none

//-- Template for the top entity
module top (
    input clock,
    input latch,
    input [7:0] d_in,
    output reg data
);
  reg [7:0] shift_reg;
  always @(posedge latch) begin
    shift_reg <= d_in;
    data <= d_in[7];
  end
  always @(posedge clock) begin
    
    shift_reg <= {shift_reg[6:0], 1'b0};
    data <= shift_reg[6];
  end

endmodule
