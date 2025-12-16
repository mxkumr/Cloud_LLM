.text
.global copy_bytes
copy_bytes:
    push {lr}           @ Guardar el registro de retorno

    mov r3, r2          @ r3 = número de bytes a copiar (r2)

loop:
    cmp r3, #0          @ Comprobar si r3 == 0
    beq end_loop        @ Si es 0, salir del bucle

    ldrb r0, [r1]       @ Cargar un byte desde la fuente (r1)
    strb r0, [r0, r0]   @ Almacenar el byte en el destino (r0) - ¡Error aquí! Corrección:

    @ Corrección: Usar r0 como destino, r1 como fuente, r2 como contador
    @ Revisar: r0 = destino, r1 = fuente, r2 = bytes

    @ Corrección del código:
    mov r3, r2          @ r3 = número de bytes a copiar
    mov r4, r0          @ r4 = puntero destino
    mov r5, r1          @ r5 = puntero fuente

copy_loop:
    cmp r3, #0          @ Comprobar si aún hay bytes por copiar
    beq copy_end        @ Si no hay, salir

    ldrb r0, [r5], #1   @ Cargar byte desde fuente y avanzar fuente
    strb r0, [r4], #1   @ Almacenar byte en destino y avanzar destino
    subs r3, r3, #1     @ Decrementar contador
    b copy_loop         @ Volver a iterar

copy_end:
    mov r0, r2          @ Devolver número de bytes copiados (r2)
    pop {pc}            @ Restaurar y devolver