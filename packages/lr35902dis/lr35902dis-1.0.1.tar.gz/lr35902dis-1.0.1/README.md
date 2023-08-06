# lr35902dis

A python disassembler library for the LR35902 CPU (the CPU of the GameBoy, similar to a Z80 processor).
This is an adaptation of [z80dis](https://github.com/lwerdna/z80dis). Any errors are probably mine, PRs welcome :).

# Use

```
>>> from lr35902dis import lr35902
>>> lr35902.disasm(b'\xCB\xE7', 0)
'set 4,a'
```

Or, if you'd like access to the instruction internals, like opcode identifier, length, and operands:

```
>>> decoded = lr35902.decode(b'\xCB\xE7', 0)
>>> decoded.op
<OP.SET: 58>
>>> decoded.operands[0]
(<OPER_TYPE.IMM: 45>, 4)
>>> decoded.operands[1]
(<OPER_TYPE.REG_A: 1>,)
>>> decoded.len
2
```

The decoded structure can be supplied to disasm() to make a string:

```
>>> lr35902.disasm(decoded)
'set 4,a'
```

