start:
    mov r7, 0xfe00
    call getc
    call putc
    mov r0, 0xA
    call putc
    kill


putc:
    ld.b r1, [0xff03]
    test r1, 1
    jmp.eq putc
    st.b[0xff02], r0
    ret
getc:
    ld.b r1, [0xff03]
    test r1, 4
    jmp.eq getc
    ld.b r0, [0xff02]
    ret
