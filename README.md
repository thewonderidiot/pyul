# Pyul

## Overview

Pyul is a port of the [Yul assembler](https://archive.org/details/yulsystemsourcec00hugh/mode/1up) from Honeywell 1800 assembly to python. Yul was written by Hugh Blair-Smith, originally for the IBM 650. It was later ported to the Honeywell 800, and then to its successor, the Honeywell 1800. It a was finally rewritten for the IBM 360 as GAP ("General Assembler Program"). The Honeywell 1800 version is the only known to still survive. This version was used to assemble the code for all unmanned flights of the Apollo Guidance Computer; GAP was used for all manned flights.

The Honeywell 1800 has a rather unique architecture, which poses interesting challenges for porting to other machines:
* The machine has _two_ program counters, the "sequence counter" and the "cosequence counter", each of which can count either forwards or backwards (although this latter capability was apparently very rarely used).
* Almost every instruction specifies which program counter the next instruction should be executed with. A branch instruction specifying the other program counter first moves that other program counter to the target address, and then switches to it and begins executing there.
* Most instructions can be masked, causing the instruction to only operate on the bits that pass the mask. For example, the middle 10 bits of two words can be added together without affecting the rest of the bits.

Hugh, in his own words, found "clever" ways to use some of these capabilities -- and as a result, Yul provides its own challenges on top of the basic H-1800 challenges:
* There are many instances of self-modifying code.
* Certain sections of code behave differently depending on which program counter executes them.
* Yul was written to run on a custom MIT-developed operating system for the H-1800 called the "Monitor". No source code or documentation for this operating system or its support libraries survives.

For the most part, pyul is a direct port of the H-1800 logic to python, with as few modifications as possible. Self-modifying code is handled with conditional logic containing all possibilities for the relevant code; rather than actually modifying instructions, a variable is updated to select which implementation should be currently active.

Programs written natively in assembly can be difficult to disentangle into high-level language constructs like conditionals, loops, and functions; control flow is entirely achieved through branch instructions which effectively operate as `goto`. I have function-ized logic where it was possible to do so cleanly, but there are many, many places where it was not. To simulate these `goto`s, I have made use of the fact that all python functions return `None` implicitly if no explicit return is given, and the type of any given return is not enforced (at least, if unspecified). Therefore, it is possible to make a function for each label accessed from multiple points, and jump to it with `return label()`. This achieves the desired control flow at the expense of rapidly deepening the call stack until (if) the function associated with some label actually returns something. In a few strategic places, to manage the deep call stack, I have inserted exceptions to unwind the stack and go back to the beginning of the current big chunk of logic. I readily admit that this is quite janky and is hard to follow if you think about what's actually going on instead of translating the `return label()` calls to `goto label` in your head. I apologize, and promise this isn't how I would usually write python.

The main differences from Yul are in symbol tracking and tape management. Yul uses a complex threading strategy for keeping track of symbols; I have replaced all of this logic with the much easier-to-manage python `dict`. Likewise, tapes are modeled as folders containing a tree of files -- logically equivalent, but again, easier to work with.

## Interacting with Pyul

The [Yul Programmer's Digest](https://archive.org/details/yulsystemsourcec00hugh/page/n4/mode/1up) and the [AGC Information Series issue on Yul](https://ibiblio.org/apollo/Documents/agcis_13_yul.pdf) are both excellent pieces of documentation for Yul that are equally applicable to pyul. 

Pyul expects 80-column punchcard images separated by newlines on stdin. It will produce line-printer outputs on stdin, and typewriter printouts on stderr. To properly launch pyul, the first two cards in the input deck should monitor cards (asterisk in column 1) similar to:
```
* 1800A JOB 55-238-00  YUL SYSTEM
*       YUL NANSTONE
```
The first card launches the Yul job. In the example shown, `1800A` is the machine name and `55-238-00` is the job number. The second card is a special monitor card expected by Yul as its first input. The `YUL` on this card is required. The word following `YUL` is optional, and if given, is the name of the tape that the following cards will operate on. If no tape name is given, the default of `YULPROGS` is used.

If starting a new tape, a series of Yul director cards (`Y` in column 1) must follow declaring the existence of the target computer(s), and which assembly passes are available for each. This looks like:
```
Y  NAN  ADD NEW COMPUTER BLK2
Y  NAN  ASSEMBLY PASS 1 FOR BLK2 IS AVAILABLE
Y  NAN  ASSEMBLY PASS 2 FOR BLK2 IS AVAILABLE
Y  NAN  ASSEMBLY PASS 3 FOR BLK2 IS AVAILABLE
Y  NAN  MANUFACTURING FOR BLK2 IS AVAILABLE
```

Columns 2-8 of director cards must contain an abbreviation of the tape being operated on. If the first letter of the abbreviation does not match that specified when Yul was launched, an error will be raised.

Currently supported computers and passes in pyul include:
* AGC4 - passes 1-3 and manufacturing
* BLK2 - passes 1-3 and manufacturing
* AGC - passes 1-2

Once the tape has been set up (or if operating on a tape that has already been set up), you can insert director cards to perform the desired assembly maintenance functions. For example, to assembly a new program:
```
Y  NAN  ASSEMBLE NEW BLK2 PROGRAM AURORA BY DAP GROUP
```

Optional subdirector cards (`S` in column 1`) can follow this director. After that, all cards processed are considered part of the new assembly until a director card or monitor card is encountered. Both mark the end of the assembly.

The example program TRIVIUM from the AGC Information Series issue can be assembled as follows:
```
./pyul/pyul.py -y 1963 -d 1963-11-24 -j 95175 < decks/TRIVIUM.R0.deck > TRIVIUM.R0.lst
```

The `-y` flag specifies the assembly year, and is used to control feature availability and output formats. `-d` and `-j` specify the date and job number to print in the listing. Pyul will produce the following typewriter output:
```
55-238-50
BEGIN YUL SYSTEM


■■■■■■■■
MESSAGE ASSEMBLY TESTING
■■■■■■■■


  NEW COMPUTER: AGC4
ACCEPTED



RE: ASSEMBLY PASS 1 FOR AGC4 DECLARED AVAILABLE
ACCEPTED



RE: ASSEMBLY PASS 2 FOR AGC4 DECLARED AVAILABLE
ACCEPTED



RE: ASSEMBLY PASS 3 FOR AGC4 DECLARED AVAILABLE
ACCEPTED



ASSEMBLY FOR AGC4:
NEW PROGRAM TRIVIUM BY IMA NIT-PICKER
END YUL PASS 1
END YUL PASS 2
UNDEFINED:  HUNTSVIL
  AWFUL ASSEMBLY; FILED ON DISC
       3 LINES CUSSED BETWEEN PAGES   1 AND   7.



END YUL SYSTEM
```
The resulting TRIVIUM.R0.lst will consist of 8 pages that should relatively closely match the printout included in the AGC Information Series document. The year flag does not yet cover all differences of Yul through the years, so imperfections will be the result of later Yul logic reacting differently than earlier Yul would have.

## Punch card decks

Conversion of the available AGC software back into its original punchard format is ongoing. Decks either completed or in-progress are available in the `decks` directory.
