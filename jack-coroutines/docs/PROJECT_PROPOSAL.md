# Original capstone proposal

Historical project proposal by Louis Chen, extracted from the original coursework document. This records the intended design; the implemented task syntax is `task step()`, without a return type.

For my project I will be implementing coroutines in the Jack compiler. This will require me to:

Extend the Jack syntax with keywords of coroutine, task, yield, and finish.

Modify the tokenizer and parser.

Add compiler-generated coroutine state fields.

Turn coroutine tasks into run step state machine methods.

Generate hack vm code to then be run and tested on the Nand2tetris vm emulator.

I would want to be able to run code like 

task void run() {

    do A();

    yield;

    do B();

    yield;

    do C();

    finish;

}

I would create a coroutine class that keeps track of a coroutines state and whether it is finished or not. I would need a scheduler that calls each coroutine’s steps one at a time, to simulate multiple tasks to run together. This would need to be implemented with VM commands. Then with handling variables across functions, since variables disappear after a function ends, requiring variables used to be declared as fields can make the project easier. I would also want to just focus on implementing basic coroutine tasks without loops to start, to make code easier to generate. There will also probably be great challenges debugging the code, since VM code is very hard to read.

For a final demo, I would probably have a jack program that runs two coroutines that take turns counting and printing values.
