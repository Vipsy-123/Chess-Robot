Function Main
    Const 1 = Pa1
    Open "COM2:" As #1
    Input #1,Data1,Data2,Data3
    Select Data1
    Case 1
        PSRC = Pa1
        Break
    Case 2
        PSRC = Pa2
        Break
    Case 3
        PSRC = Pa3
        Break
    Case 4
        PSRC = Pa4
        Break
    Case 5
        PSRC = Pa5
        Break
    Case 6
        PSRC = Pa6
        Break
    Case 7
        PSRC = Pa7
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Case 8
        PSRC = Pa8
        Break
    Default 
        PSRC = PHome
        Break
    End Select
    If Data3 = 1 Then
        PieceAttack(PSRC,PDEST)
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
