// Project F: FPGA Graphics - Square (iCEBreaker 12-bit DVI Pmod)
// (C)2023 Will Green, open source hardware released under the MIT License
// Learn more at https://projectf.io/posts/fpga-graphics/

`default_nettype none

module top (
    input  wire logic CLK,       // 25 MHz clock
    input  wire logic SW1,       // reset button
    input wire logic SW2,       // right or up
    input wire logic SW3,       // left or down
    input wire logic SW4,       // switch axis, start left/right
    output      logic VGA_HS,    // VGA horizontal sync
    output      logic VGA_VS,    // VGA vertical sync
    output      logic [2:0] VGA_R,  // 3-bit VGA red
    output      logic [2:0] VGA_G,  // 3-bit VGA green
    output      logic [2:0] VGA_B   // 3-bit VGA blue
    );

    // display sync signals and coordinates
    localparam CORDW = 10;  // screen coordinate width in bits
    logic [CORDW-1:0] sx, sy;
    logic de;
    simple_480p display (
        .clk_pix(CLK),
        .rst_pix(SW1),  // wait for clock lock
        .sx,
        .sy,
        .hsync(VGA_HS),
        .vsync(VGA_VS),
        .de
    );
    
    // button synchronizers and edge detectors
    logic [1:0] sw1_sync, sw2_sync, sw3_sync, sw4_sync;
    logic sw4_prev;

    always_ff @(posedge CLK) begin
        // 2-stage synchronizer for all buttons
        sw1_sync <= {sw1_sync[0], SW1};
        sw2_sync <= {sw2_sync[0], SW2};
        sw3_sync <= {sw3_sync[0], SW3};
        sw4_sync <= {sw4_sync[0], SW4};
        
        // edge detection for SW4 (detects button press, not hold)
        sw4_prev <= sw4_sync[1];
    end

    // button movements
    integer adjust_x = 0;
    integer adjust_y = 0;
    logic axis = 0; // 0 = x, 1 = y
    always_ff @(posedge CLK) begin
        if (sw1_sync[1]) begin
            adjust_x <= 0;
            adjust_y <= 0;
            axis <= 0;
        end else begin
            if (sw4_sync[1] && !sw4_prev) axis <= ~axis; // change axis
            if (axis == 0) begin
                if (sw2_sync[1] && !sw2_sync[0] && adjust_x < 200) adjust_x <= adjust_x + 5; // right
                if (sw3_sync[1] && !sw3_sync[0] && adjust_x > -220) adjust_x <= adjust_x - 5; // left
            end else begin
                if (sw2_sync[1] && !sw2_sync[0] && adjust_y > -140) adjust_y <= adjust_y - 5; // up
                if (sw3_sync[1] && !sw3_sync[0] && adjust_y < 140) adjust_y <= adjust_y + 5; // down
            end

        end
    end


    // define a square with screen coordinates
    logic square;
    always_comb begin
        square = (sx > 220 + adjust_x && sx < 420 + adjust_x) && (sy > 140 + adjust_y && sy < 340 + adjust_y);
    end

    // paint color: white inside square, blue outside
    logic [2:0] paint_r, paint_g, paint_b;
    always_comb begin
        paint_r = (square) ? 3'h3 : 3'h1;
        paint_g = (square) ? 3'h1 : 3'h5;
        paint_b = (square) ? 3'h1 : 3'h3;
    end

    // display color: paint color but black in blanking interval
    logic [2:0] display_r, display_g, display_b;
    always_comb begin
        display_r = (de) ? paint_r : 3'b000;
        display_g = (de) ? paint_g : 3'b000;
        display_b = (de) ? paint_b : 3'b000;
    end

    always_ff @(posedge CLK) begin
        VGA_R <= display_r;
        VGA_G <= display_g;
        VGA_B <= display_b;
    end

endmodule

