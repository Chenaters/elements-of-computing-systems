/*
 * Snake Code for Tiny Tapeout VGA Playground
 * Copy paste into the playground.
 * Press 0 to toggle reset snake.
 * Press 1 to toggle snake turn counter clockwise
 * Press 2 to togler snake turn clockwise. 
 */

`default_nettype none

module tt_um_vga_example(
  input  wire [7:0] ui_in,    // Dedicated inputs
  output wire [7:0] uo_out,   // Dedicated outputs
  input  wire [7:0] uio_in,   // IOs: Input path
  output wire [7:0] uio_out,  // IOs: Output path
  output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
  input  wire       ena,      // always 1 when the design is powered, so you can ignore it
  input  wire       clk,      // clock
  input  wire       rst_n     // reset_n - low to reset
);

  // VGA signals
  wire hsync;
  wire vsync;
  wire [1:0] R;
  wire [1:0] G;
  wire [1:0] B;
  wire video_active;
  wire [9:0] pix_x;
  wire [9:0] pix_y;
  wire sound;

  // TinyVGA PMOD
  //   [7] hsync
  //   [6] B[1]
  //   [5] G[0]
  //   [4] R[0]
  //   [3] vsync
  //   [2] B[0]
  //   [1] G[0]
  //   [0] R[0]
  assign uo_out = {hsync, B[1], G[1], R[0], vsync, B[0], G[0], R[0]};

  // Unused outputs assigned to 0.
  assign uio_out = 0;
  assign uio_oe  = 0;

  // Suppress unused signals warning
  wire _unused_ok = &{ena, ui_in, uio_in};

  // Frame counter – increments once per frame (per vsync)
  reg [9:0] counter;

  hvsync_generator hvsync_gen(
    .clk(clk),
    .reset(~rst_n),
    .hsync(hsync),
    .vsync(vsync),
    .display_on(video_active),
    .hpos(pix_x),
    .vpos(pix_y)
  );
  
  // ========= SNAKE PARAMETERS =========

  function signed [7:0] wave_value;
    input [4:0] idx;
    begin
      case (idx)
        4'd0:  wave_value =   0;
        4'd1:  wave_value =   5;
        4'd2:  wave_value =   9;
        4'd3:  wave_value =  12;
        4'd4:  wave_value =  14;
        4'd5:  wave_value =  15;
        4'd6:  wave_value =  14;
        4'd7:  wave_value =  12;
        4'd8:  wave_value =   9;
        4'd9:  wave_value =   5;
        4'd10: wave_value =   0;
        4'd11: wave_value =  -5;
        4'd12: wave_value =  -9;
        4'd13: wave_value = -12;
        4'd14: wave_value = -14;
        4'd15: wave_value = -15;
        5'd16: wave_value = -14;
        5'd17: wave_value =  -12;
        5'd18: wave_value =   -9;
        5'd19: wave_value =   -5;
        default: wave_value = 0;
      endcase
    end
  endfunction

  localparam integer SNAKE_SEGMENTS = 5;   // how many circles
  localparam integer MAX_SEG = 16;
  localparam integer SEG_SPACING    = 15;  // spacing in pixels between segment centers
  localparam integer RADIUS         = 10;  // circle radius in pixels
  localparam integer RADIUS2        = RADIUS * RADIUS; // radius^2 for distance check
  localparam integer FOOD_RADIUS    = 6;   // food radius in pixels
  localparam integer FOOD_RADIUS2   = FOOD_RADIUS * FOOD_RADIUS;
  localparam integer UPDATE_RATE = 1;

  // should have spacing of 5
  reg [4:0] wave_idx_x = 5'd0;
  reg [4:0] wave_idx_y = 5'd5;

  // Head position: move horizontally across screen
  reg signed [10:0] head_x = 200;
  reg signed [10:0] head_y = 200;

  // Food position and LFSR for random placement
  reg signed [10:0] food_x = 300;
  reg signed [10:0] food_y = 150;
  reg [15:0] lfsr = 16'hACE1;  // LFSR seed for pseudo-random numbers
  reg food_eaten = 1'b0;
  
  integer i;
  integer j;

  // Decide if current pixel is inside ANY snake segment (circle)
  reg snake_pixel;
  reg food_pixel;

  reg signed [10:0] body_x [0:SNAKE_SEGMENTS-1];
  reg signed [10:0] body_y [0:SNAKE_SEGMENTS-1];
 
  reg signed [10:0] dx, dy;
  reg [21:0]        dist2;
  reg signed [10:0]         seg_x;
  reg signed [10:0]         seg_y;

  // Collision detection between head and food
  reg head_food_collision;

  always @* begin
    // Check if head collides with food
    dx = $signed({1'b0, head_x}) - $signed({1'b0, food_x});
    dy = $signed({1'b0, head_y}) - $signed({1'b0, food_y});
    dist2 = dx*dx + dy*dy;
    head_food_collision = (dist2 <= (RADIUS + FOOD_RADIUS) * (RADIUS + FOOD_RADIUS));
  end

  always @* begin 
    snake_pixel = 1'b0;
    food_pixel = 1'b0;

    // Check head
    dx = $signed({1'b0, pix_x}) - $signed({1'b0, head_x});
    dy = $signed({1'b0, pix_y}) - $signed({1'b0, head_y});
    dist2 = dx*dx + dy*dy;
    if (dist2 <= RADIUS2)
      snake_pixel = 1'b1;

    // Check food
    dx = $signed({1'b0, pix_x}) - $signed({1'b0, food_x});
    dy = $signed({1'b0, pix_y}) - $signed({1'b0, food_y});
    dist2 = dx*dx + dy*dy;
    if (dist2 <= FOOD_RADIUS2)
      food_pixel = 1'b1;

    // Check body segments
    for (j = 0; j < (SNAKE_SEGMENTS - 1); j = j + 1) begin
      dx = $signed({1'b0, pix_x}) - $signed({1'b0, body_x[j]});
      dy = $signed({1'b0, pix_y}) - $signed({1'b0, body_y[j]});
      dist2 = dx*dx + dy*dy;
      if (dist2 <= RADIUS2)
        snake_pixel = 1'b1;
    end
  end

  // Color: bright green snake, red food on black background
  wire pixel_on_snake = video_active && snake_pixel;
  wire pixel_on_food = video_active && food_pixel;

  assign R = pixel_on_food ? 2'b11 : (pixel_on_snake ? 2'b00 : 2'b00);  // red food, black/green snake
  assign G = pixel_on_snake ? 2'b11 : 2'b00;  // full green for snake
  assign B = pixel_on_snake ? 2'b00 : 2'b00;  // no blue

  // Frame counter updates once per frame (vsync)
  always @(posedge vsync or negedge rst_n) begin
    if (~rst_n || ui_in[0]) begin
      head_x <= 10'd200;
      head_y <= 10'd200;
      counter <= 9'd0;
      wave_idx_x <= 5'd0;
      wave_idx_y <= 5'd5;
      food_x <= {1'b0, lfsr[9:0]} % 480 + 50;  // 50-530 range
      food_y <= {1'b0, lfsr[15:6]} % 420 + 30; // 30-450 range
      for (i = 0; i < SNAKE_SEGMENTS; i = i + 1) begin
      // Segment centers: spaced to the left of the head
        body_x[i] <= head_x - (i+1) * (wave_value(wave_idx_x));
        body_y[i] <= head_y - (i+1) * (wave_value(wave_idx_y));
      end
    end else begin
      // LFSR update for pseudo-random number generation (Galois LFSR)
      lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};

      if(counter == UPDATE_RATE) begin
        // Update direction
        if(ui_in[1]) begin
          wave_idx_x <= (wave_idx_x + 1) % 20;
          wave_idx_y <= (wave_idx_y + 1) % 20;
        end
        if(ui_in[2]) begin
          if(wave_idx_x == 0) begin
            wave_idx_x <= 19;
          end
          else begin
            wave_idx_x <= (wave_idx_x - 1);
          end
          if(wave_idx_y == 0) begin
            wave_idx_y <= 19;
          end
          else begin
            wave_idx_y <= (wave_idx_y - 1);
          end       
        end

        // Check if food was eaten and spawn new food
        if (head_food_collision) begin
          // Spawn new food using LFSR for pseudo-random position
          food_x <= {1'b0, lfsr[9:0]} % 480 + 50;  // 50-530 range
          food_y <= {1'b0, lfsr[15:6]} % 420 + 30; // 30-450 range
        end

        counter <= 9'd0;
        for (i = SNAKE_SEGMENTS-1; i > 0; i = i - 1) begin
          body_x[i] <= body_x[i-1];
          body_y[i] <= body_y[i-1];
        end

      // 2) body segment 0 takes the *old* head position
        body_x[0] <= head_x;
        body_y[0] <= head_y;

        head_x <= head_x + (wave_value(wave_idx_x));
        head_y <= head_y + (wave_value(wave_idx_y));
      end
      else begin
        counter <= counter + 9'd1;
      end 
      
    end
  end

endmodule
