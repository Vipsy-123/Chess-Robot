Open "COM2:" As #1
Input #1,PSRC,PDEST,ATTK
If ATTK = 1 Then
    PieceAttack(PSRC,PDEST)
Else 
    PieceMove(PSRC,PDEST)
EndIf
End

Function P PieceMove(PSRC,PDEST)
Mvs PHome ' Move to Home Position
HOpen 1 ' Open gripper
Mvs PSRC,-50
Mvs PSRC
HClose 1 ' Close gripper
Mvs PSRC,-50
Mvs PDEST,-50
Mvs PDEST
HOpen 1 ' Open gripper
Dly 0.2
Mvs PDEST, -50
Mvs PHome
FEnd 

Function P PieceAttack(PSRC,PDEST)
Mvs PHome ' Move to Home Position
HOpen 1 ' Open gripper
Mvs PDEST,-50
Mvs PDEST
HClose 1 ' Close gripper
Mvs PDEST,-50
Mvs OUT,-50
Mvs OUT
HOpen 1 ' Open gripper
Dly 0.2
Mvs OUT, -50
Mvs PSRC,-50
Mvs PSRC
HClose 1 ' Close gripper
Mvs PSRC,-50
Mvs PDEST,-50
Mvs PDEST
HOpen 1 ' Open gripper
Dly 0.2
Mvs PDEST, -50
Mvs PHome
FEnd
