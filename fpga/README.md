# FPGA and digital logic coursework

| Folder | Source |
| --- | --- |
| vga-square | 640x480 timing, colored-square top module, Go Board pin map and Apio configuration |
| vga-snake | VGA snake/curved movement top module and timing for the Go Board |
| tiny-tapeout-snake | Alternate Tiny Tapeout VGA wrapper; requires an external hvsync_generator module not present in this source snapshot |
| shift-register | Serial shift register and original self-checking Verilog testbench |
| switch-logic | Switch/prime logic exercises and a source testbench |

Each board project has its own top module; do not merge all the files into one
build. Existing board constraints and course/template material retain their
headers. The shift register writes shared registers in two always blocks; its
educational simulation is not proof of synthesis or timing correctness.

HDL tools were unavailable during publication. No fresh simulation, synthesis,
board programming, or FPGA timing result is claimed. Generated bitstreams and
build caches are excluded.
