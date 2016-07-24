mov r0,3
loop:
sub r0,#1
jmp.ne loop
mov r0,end
jmp r0
end:
cmp r0,#0
set.ne r1
cmp r3,#0
set.eq r2
