`timescale 1ns/1ps
`default_nettype none

module main_tb;
    reg clock = 0;
    reg latch = 0;
    reg [7:0] d_in  = 8'h00;
    wire data;

    // Unit Under Test
    top uut (
        .clock(clock),
        .latch(latch),
        .d_in(d_in),
        .data(data)
    );

    always #10 clock = ~clock;

    initial begin
        $dumpvars(0, main_tb);
        $timeformat(-9, 0, " ns", 10);
    end

    integer i, idx;
    reg expb;
    reg [7:0] vec;

    initial begin
        // Let the chip settle
        repeat (2) @(posedge clock);

        vec = 8'b1010_1010;

        @(negedge clock);
        d_in  = vec;
        latch = 1;

        // Capture edge: load + output bit7
        idx  = 7;
        expb = vec[7];
        #1ps; // wait for NBAs to land
        $display("t=%0t  data=%b (bit %0d expected=%b)", $time, data, idx, expb);
        if (data !== expb) $fatal(1, "Mismatch at bit %0d: got %b expected %b", idx, data, expb);

        // Drop latch after the capture edge
        #5000ps;
        latch = 0;

        // Shift out remaining 7 bits: indices 6..0
        for (i = 6; i >= 0; i = i - 1) begin
            @(posedge clock);
            idx  = i;
            expb = vec[i];
            #1ps; // post-NBA check
            $display("t=%0t  data=%b (bit %0d expected=%b)", $time, data, idx, expb);
            if (data !== expb) $fatal(1, "Mismatch at bit %0d: got %b expected %b", idx, data, expb);
        end

        #20;
        $display("PASS: shifted 8 bits correctly.");
        $finish;
    end

    initial begin
        #5000;
        $display("Timeout — forcing finish");
        $finish;
    end
endmodule

