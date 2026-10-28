// Snake Game for Go Board (iCE40 HX1K)
// Uses wave function for smooth circular movement

`default_nettype none

module top (
    input  wire logic CLK,       // 25 MHz clock
    input  wire logic SW1,       // reset button
    input  wire logic SW2,       // rotate clockwise
    input  wire logic SW3,       // rotate counter-clockwise  
    input  wire logic SW4,       // (unused)
    output      logic VGA_HS,    // VGA horizontal sync
    output      logic VGA_VS,    // VGA vertical sync
    output      logic [2:0] VGA_R,  // 3-bit VGA red
    output      logic [2:0] VGA_G,  // 3-bit VGA green
    output      logic [2:0] VGA_B   // 3-bit VGA blue
    );

    // VGA timing
    logic [9:0] sx, sy;
    logic de, hsync_i, vsync_i;
    
    simple_480p display (
        .clk_pix(CLK),
        .rst_pix(1'b0),
        .sx, .sy,
        .hsync(hsync_i),
        .vsync(vsync_i),
        .de
    );

    // ========= WAVE FUNCTION FOR CIRCULAR MOVEMENT =========
    // Returns sine-like values for smooth curved motion
    // 16 steps around a circle, values represent velocity component
    function signed [4:0] wave_x;
        input [3:0] idx;
        begin
            case (idx)
                4'd0:  wave_x =   5;   // Right
                4'd1:  wave_x =   5;
                4'd2:  wave_x =   4;
                4'd3:  wave_x =   2;
                4'd4:  wave_x =   0;   // Down
                4'd5:  wave_x =  -2;
                4'd6:  wave_x =  -4;
                4'd7:  wave_x =  -5;
                4'd8:  wave_x =  -5;   // Left
                4'd9:  wave_x =  -5;
                4'd10: wave_x =  -4;
                4'd11: wave_x =  -2;
                4'd12: wave_x =   0;   // Up
                4'd13: wave_x =   2;
                4'd14: wave_x =   4;
                4'd15: wave_x =   5;
            endcase
        end
    endfunction
    
    function signed [4:0] wave_y;
        input [3:0] idx;
        begin
            case (idx)
                4'd0:  wave_y =   0;   // Right
                4'd1:  wave_y =   2;
                4'd2:  wave_y =   4;
                4'd3:  wave_y =   5;
                4'd4:  wave_y =   5;   // Down
                4'd5:  wave_y =   5;
                4'd6:  wave_y =   4;
                4'd7:  wave_y =   2;
                4'd8:  wave_y =   0;   // Left
                4'd9:  wave_y =  -2;
                4'd10: wave_y =  -4;
                4'd11: wave_y =  -5;
                4'd12: wave_y =  -5;   // Up
                4'd13: wave_y =  -5;
                4'd14: wave_y =  -4;
                4'd15: wave_y =  -2;
            endcase
        end
    endfunction

    // Snake parameters
    localparam SEG_SIZE = 14;
    localparam FOOD_SIZE = 10;
    
    // Direction index (0-15 around the circle)
    reg [3:0] dir_idx = 4'd0;
    
    // Snake head position (signed for proper math)
    reg signed [10:0] head_x = 11'd200;
    reg signed [10:0] head_y = 11'd240;
    
    // Snake body (up to 5 segments)
    reg signed [10:0] body_x [0:4];
    reg signed [10:0] body_y [0:4];
    reg [2:0] segments = 3'd3;
    
    // Food
    reg [9:0] food_x = 10'd400;
    reg [9:0] food_y = 10'd200;
    reg [7:0] lfsr = 8'hAC;
    
    // Frame counter for movement
    reg [3:0] frame_count = 4'd0;
    logic vsync_prev;
    
    // Button sync
    logic [1:0] sw1_sync, sw2_sync, sw3_sync;
    logic sw2_edge, sw3_edge, sw2_prev, sw3_prev;
    
    always_ff @(posedge CLK) begin
        sw1_sync <= {sw1_sync[0], SW1};
        sw2_sync <= {sw2_sync[0], SW2};
        sw3_sync <= {sw3_sync[0], SW3};
        sw2_prev <= sw2_sync[1];
        sw3_prev <= sw3_sync[1];
        sw2_edge <= sw2_sync[1] && !sw2_prev;
        sw3_edge <= sw3_sync[1] && !sw3_prev;
    end
    
    // Collision detection (simple box overlap)
    wire food_collision = (head_x < $signed({1'b0, food_x}) + FOOD_SIZE) && (head_x + SEG_SIZE > $signed({1'b0, food_x})) &&
                          (head_y < $signed({1'b0, food_y}) + FOOD_SIZE) && (head_y + SEG_SIZE > $signed({1'b0, food_y}));
    
    // Rendering
    logic snake_pixel, food_pixel;
    integer i;
    
    always_comb begin
        snake_pixel = 1'b0;
        food_pixel = 1'b0;
        
        // Check head
        if (sx >= head_x[9:0] && sx < head_x[9:0] + SEG_SIZE &&
            sy >= head_y[9:0] && sy < head_y[9:0] + SEG_SIZE)
            snake_pixel = 1'b1;
        
        // Check food
        if (sx >= food_x && sx < food_x + FOOD_SIZE &&
            sy >= food_y && sy < food_y + FOOD_SIZE)
            food_pixel = 1'b1;
        
        // Check body segments
        for (i = 0; i < 5; i = i + 1) begin
            if (i < segments) begin
                if (sx >= body_x[i][9:0] && sx < body_x[i][9:0] + SEG_SIZE &&
                    sy >= body_y[i][9:0] && sy < body_y[i][9:0] + SEG_SIZE)
                    snake_pixel = 1'b1;
            end
        end
    end
    
    // Color output
    logic [2:0] paint_r, paint_g, paint_b;
    always_comb begin
        if (de && food_pixel) begin
            paint_r = 3'b111;  // Red food
            paint_g = 3'b000;
            paint_b = 3'b000;
        end else if (de && snake_pixel) begin
            paint_r = 3'b000;  // Green snake
            paint_g = 3'b111;
            paint_b = 3'b000;
        end else begin
            paint_r = 3'b000;  // Black background
            paint_g = 3'b000;
            paint_b = 3'b001;
        end
    end
    
    // Game logic
    integer j;
    always_ff @(posedge CLK) begin
        vsync_prev <= vsync_i;
        
        if (vsync_i && !vsync_prev) begin
            // Update LFSR
            lfsr <= {lfsr[6:0], lfsr[7] ^ lfsr[5] ^ lfsr[4] ^ lfsr[3]};
            
            if (sw1_sync[1]) begin
                // Reset
                head_x <= 11'd200;
                head_y <= 11'd240;
                dir_idx <= 4'd0;
                segments <= 3'd3;
                food_x <= 10'd400;
                food_y <= 10'd200;
                frame_count <= 4'd0;
                for (j = 0; j < 5; j = j + 1) begin
                    body_x[j] <= 11'd200 - (j+1) * SEG_SIZE;
                    body_y[j] <= 11'd240;
                end
            end else begin
                // Button controls - rotate direction around circle
                if (sw2_edge) begin
                    dir_idx <= dir_idx + 4'd1;  // Rotate clockwise
                end
                if (sw3_edge) begin
                    dir_idx <= dir_idx - 4'd1;  // Rotate counter-clockwise
                end
                
                // Move snake every N frames
                if (frame_count == 4'd3) begin
                    frame_count <= 4'd0;
                    
                    // Check food collision
                    if (food_collision) begin
                        food_x <= {2'b00, lfsr} + 10'd50;
                        food_y <= {2'b00, lfsr[7:0] ^ lfsr[3:0], lfsr[7:4]} + 10'd50;
                        if (segments < 3'd5)
                            segments <= segments + 3'd1;
                    end
                    
                    // Shift body
                    for (j = 4; j > 0; j = j - 1) begin
                        body_x[j] <= body_x[j-1];
                        body_y[j] <= body_y[j-1];
                    end
                    body_x[0] <= head_x;
                    body_y[0] <= head_y;
                    
                    // Move head using wave functions for circular motion
                    head_x <= head_x + wave_x(dir_idx);
                    head_y <= head_y + wave_y(dir_idx);
                end else begin
                    frame_count <= frame_count + 4'd1;
                end
            end
        end
    end
    
    // Output registers
    always_ff @(posedge CLK) begin
        VGA_R <= paint_r;
        VGA_G <= paint_g;
        VGA_B <= paint_b;
        VGA_HS <= hsync_i;
        VGA_VS <= vsync_i;
    end

endmodule
