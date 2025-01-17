'  SVR Robotics
'  Author : Vipul Pardeshi
'  Description : CHESS_ROBOT_CODE
'  This script is responsible for controlling a robotic arm to play Chess Game.
'  Visit this Website for Robot Code Upload and Data Link Layer Setup -https://shorturl.at/Xidwx
'  It communicates with an external device via a COM port and moves chess pieces.
'  The script reads data from the COM port, decides the piece to move, and executes the move accordingly.
'  Functions are provided to handle piece movement and attack.
'  Data1 is Position from where Robot Should Pick the Piece
'  Data2 is Position to where Robot should place the Piece
'  Data3 corresponds to Move Type :
'    It can be  1 -> Simple Move   2 -> Attack Move   3 -> Kingside Castling   4 -> Queenside Castling
'  Accordingly Functions are called and after Robot move is complete it returns
Function Main
    Mvs PHome ' Move to Home Position
    button_click_waitt()
    M_Out(13)=0  'Green LED OFF
    M_Out(12)=1  'Red LED ON
    Open "COM2:" As #1
    Print #1,1
    Input #1,Data1,Data2,Data3

    ' Check Game Over condition 
    If Data1 = 0  Then
        M_Out(13)=1  'Green LED ON
        M_Out(12)=1  'Red LED ON
        Dly 0.2
        M_Out(13)=0  'Green LED ON
        M_Out(12)=0  'Red LED ON
        Dly 0.2
        M_Out(13)=1  'Green LED ON
        M_Out(12)=1  'Red LED ON
        Dly 0.2
        M_Out(13)=0  'Green LED ON
        M_Out(12)=0  'Red LED ON
        Dly 0.2
        M_Out(13)=1  'Green LED ON
        M_Out(12)=1  'Red LED ON
        Dly 0.2
        M_Out(13)=0  'Green LED ON
        M_Out(12)=0  'Red LED ON
        Dly 0.2
        M_Out(13)=1  'Green LED ON
        M_Out(12)=1  'Red LED ON
        Dly 0.2
        M_Out(13)=0  'Green LED ON
        M_Out(12)=0  'Red LED ON
        Dly 0.2
        button_click_waitt()
    EndIf

    'PSRC Decision'
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
    Case 9
        PSRC = Pb1
        Break
    Case 10
        PSRC = Pb2
        Break
    Case 11
        PSRC = Pb3
        Break
    Case 12
        PSRC = Pb4
        Break
    Case 13
        PSRC = Pb5
        Break
    Case 14
        PSRC = Pb6
        Break
    Case 15
        PSRC = Pb7
        Break
    Case 16
        PSRC = Pb8
        Break
    Case 17
        PSRC = Pc1
        Break
    Case 18
        PSRC = Pc2
        Break
    Case 19
        PSRC = Pc3
        Break
    Case 20
        PSRC = Pc4
        Break
    Case 21
        PSRC = Pc5
        Break
    Case 22
        PSRC = Pc6
        Break
    Case 23
        PSRC = Pc7
        Break
    Case 24
        PSRC = Pc8
        Break
    Case 25
        PSRC = Pd1
        Break
    Case 26
        PSRC = Pd2
        Break
    Case 27
        PSRC = Pd3
        Break
    Case 28
        PSRC = Pd4
        Break
    Case 29
        PSRC = Pd5
        Break
    Case 30
        PSRC = Pd6
        Break
    Case 31
        PSRC = Pd7
        Break
    Case 32
        PSRC = Pd8
        Break
    Case 33
        PSRC = Pe1
        Break
    Case 34
        PSRC = Pe2
        Break
    Case 35
        PSRC = Pe3
        Break
    Case 36
        PSRC = Pe4
        Break
    Case 37
        PSRC = Pe5
        Break
    Case 38
        PSRC = Pe6
        Break
    Case 39
        PSRC = Pe7
        Break
    Case 40
        PSRC = Pe8
        Break
    Case 41
        PSRC = Pf1
        Break
    Case 42
        PSRC = Pf2
        Break
    Case 43
        PSRC = Pf3
        Break
    Case 44
        PSRC = Pf4
        Break
    Case 45
        PSRC = Pf5
        Break
    Case 46
        PSRC = Pf6
        Break
    Case 47
        PSRC = Pf7
        Break
    Case 48
        PSRC = Pf8
        Break
    Case 49
        PSRC = Pg1
        Break
    Case 50
        PSRC = Pg2
        Break
    Case 51
        PSRC = Pg3
        Break
    Case 52
        PSRC = Pg4
        Break
    Case 53
        PSRC = Pg5
        Break
    Case 54
        PSRC = Pg6
        Break
    Case 55
        PSRC = Pg7
        Break
    Case 56
        PSRC = Pg8
        Break
    Case 57
        PSRC = Ph1
        Break
    Case 58
        PSRC = Ph2
        Break
    Case 59
        PSRC = Ph3
        Break
    Case 60
        PSRC = Ph4
        Break
    Case 61
        PSRC = Ph5
        Break
    Case 62
        PSRC = Ph6
        Break
    Case 63
        PSRC = Ph7
        Break
    Case 64
        PSRC = Ph8
        Break
    Default
        PSRC = PHome
        Break
    End Select
      ' PDEST cases
    Select Data2
    Case 1
        PDEST = Pa1
        Break
    Case 2
        PDEST = Pa2
        Break
    Case 3
        PDEST = Pa3
        Break
    Case 4
        PDEST = Pa4
        Break
    Case 5
        PDEST = Pa5
        Break
    Case 6
        PDEST = Pa6
        Break
    Case 7
        PDEST = Pa7
        Break
    Case 8
        PDEST = Pa8
        Break
    Case 9
        PDEST = Pb1
        Break
    Case 10
        PDEST = Pb2
        Break
    Case 11
        PDEST = Pb3
        Break
    Case 12
        PDEST = Pb4
        Break
    Case 13
        PDEST = Pb5
        Break
    Case 14
        PDEST = Pb6
        Break
    Case 15
        PDEST = Pb7
        Break
    Case 16
        PDEST = Pb8
        Break
    Case 17
        PDEST = Pc1
        Break
    Case 18
        PDEST = Pc2
        Break
    Case 19
        PDEST = Pc3
        Break
    Case 20
        PDEST = Pc4
        Break
    Case 21
        PDEST = Pc5
        Break
    Case 22
        PDEST = Pc6
        Break
    Case 23
        PDEST = Pc7
        Break
    Case 24
        PDEST = Pc8
        Break
    Case 25
        PDEST = Pd1
        Break
    Case 26
        PDEST = Pd2
        Break
    Case 27
        PDEST = Pd3
        Break
    Case 28
        PDEST = Pd4
        Break
    Case 29
        PDEST = Pd5
        Break
    Case 30
        PDEST = Pd6
        Break
    Case 31
        PDEST = Pd7
        Break
    Case 32
        PDEST = Pd8
        Break
    Case 33
        PDEST = Pe1
        Break
    Case 34
        PDEST = Pe2
        Break
    Case 35
        PDEST = Pe3
        Break
    Case 36
        PDEST = Pe4
        Break
    Case 37
        PDEST = Pe5
        Break
    Case 38
        PDEST = Pe6
        Break
    Case 39
        PDEST = Pe7
        Break
    Case 40
        PDEST = Pe8
        Break
    Case 41
        PDEST = Pf1
        Break
    Case 42
        PDEST = Pf2
        Break
    Case 43
        PDEST = Pf3
        Break
    Case 44
        PDEST = Pf4
        Break
    Case 45
        PDEST = Pf5
        Break
    Case 46
        PDEST = Pf6
        Break
    Case 47
        PDEST = Pf7
        Break
    Case 48
        PDEST = Pf8
        Break
    Case 49
        PDEST = Pg1
        Break
    Case 50
        PDEST = Pg2
        Break
    Case 51
        PDEST = Pg3
        Break
    Case 52
        PDEST = Pg4
        Break
    Case 53
        PDEST = Pg5
        Break
    Case 54
        PDEST = Pg6
        Break
    Case 55
        PDEST = Pg7
        Break
    Case 56
        PDEST = Pg8
        Break
    Case 57
        PDEST = Ph1
        Break
    Case 58
        PDEST = Ph2
        Break
    Case 59
        PDEST = Ph3
        Break
    Case 60
        PDEST = Ph4
        Break
    Case 61
        PDEST = Ph5
        Break
    Case 62
        PDEST = Ph6
        Break
    Case 63
        PDEST = Ph7
        Break
    Case 64
        PDEST = Ph8
        Break
    Default
        PDEST = PHome
        Break
    End Select
    If Data3 = 1 Then
        PieceAttack(PSRC,PDEST)
    ElseIf Data3 = 2 Then
        PSRC1 = Pe1
        PDEST1 = Pg1
        PSRC2 = Ph1
        PDEST2 = Pf1
        PieceKSCastling(PSRC1,PDEST1,PSRC2,PDEST2)
    ElseIf Data3 = 3 Then
        PSRC1 = Pe1
        PDEST1 = Pb1
        PSRC2 = Pa1
        PDEST2 = Pc1
        PieceQSCastling(PSRC1,PDEST1,PSRC2,PDEST2)
    Else
        PieceMove(PSRC,PDEST)
    EndIf
    Print #1,Data1,Data2,Data3
    Dly 3
    M_Out(13)=1  'Green LED ON
    M_Out(12)=0  'Red LED OFF
    'While (M_In(15) = 0)
    '    Dly 0.1
   ' WEnd
FEnd
Function button_click_waitt()
    While (M_In(15) = 0)
        Dly 0.1
    WEnd
FEnd
Function P PieceMove(PSRC,PDEST)
Mvs PHome ' Move to Home Position
M_Out(15)=0       'grip open
Mvs PSRC,-100
Mvs PSRC
M_Out(15)=1  'grip close
Mvs PSRC,-100
Mvs PDEST,-100
Mvs PDEST
M_Out(15)=0       'grip open
Mvs PDEST, -100
Mvs PHome
FEnd
Function P PieceAttack(PSRC,PDEST)
Mvs PHome ' Move to Home Position
M_Out(15)=0       'grip open
Mvs PDEST,-100
Mvs PDEST
M_Out(15)=1  'grip close
Mvs PDEST,-100
Mvs POUT,-100
Mvs POUT
M_Out(15)=0       'grip open
Mvs POUT, -100
Mvs PSRC,-100
Mvs PSRC
M_Out(15)=1  'grip close
Mvs PSRC,-100
Mvs PDEST,-100
Mvs PDEST
M_Out(15)=0       'grip open
Mvs PDEST, -100
Mvs PHome
FEnd
Function P PieceKSCastling(PSRC1,PDEST1,PSRC2,PDEST2)
Mvs PHome ' Move to Home Position
M_Out(15)=0       'grip open
Mvs PSRC1,-100
Mvs PSRC1
M_Out(15)=1  'grip close
Mvs PSRC1,-100
Mvs PDEST1,-100
Mvs PDEST1
M_Out(15)=0       'grip open
Mvs PDEST1, -100
Mvs PSRC2,-100
Mvs PSRC2
M_Out(15)=1  'grip close
Mvs PSRC2,-100
Mvs PDEST2,-100
Mvs PDEST2
M_Out(15)=0       'grip open
Mvs PDEST2, -100
Mvs PHome
FEnd
Function P PieceQSCastling(PSRC1,PDEST1,PSRC2,PDEST2)
Mvs PHome ' Move to Home Position
M_Out(15)=0       'grip open
Mvs PSRC1,-100
Mvs PSRC1
M_Out(15)=1  'grip close
Mvs PSRC1,-100
Mvs PDEST1,-100
Mvs PDEST1
M_Out(15)=0       'grip open
Mvs PDEST1, -100
Mvs PSRC2,-100
Mvs PSRC2
M_Out(15)=1  'grip close
Mvs PSRC2,-100
Mvs PDEST2,-100
Mvs PDEST2
M_Out(15)=0       'grip open
Mvs PDEST2, -100
Mvs PHome
FEnd
