mov r0,3
mov r7,0x108
call func
jmp end
func:
    add r0, 1
    ret
end:
nop
