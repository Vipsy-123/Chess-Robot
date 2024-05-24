Function Main
    Open "COM2:" As #1
    Input #1,Data1,Data2,Data3
    Dim C1$(64)
    For Idx=1 To 64 Step 1  ' Processing for storing a value in Mary
        C1$(Idx) = "P"
    Next
    If ATTK = 1 Then
        PieceAttack(Pa1,Ph8)
    Else
        PieceMove(PSRC,PDEST)
    EndIf
FEnd
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
Mvs POUT,-50
Mvs POUT
HOpen 1 ' Open gripper
Dly 0.2
Mvs POUT, -50
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