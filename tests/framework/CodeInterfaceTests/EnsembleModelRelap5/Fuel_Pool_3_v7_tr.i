*RAVEN INPUT VALUES
* card: 20600700 word: 6 value: 5186.33632408
* card: 20600570 word: 6 value: 6714.41300221
* card: 20600610 word: 6 value: 7179.73062023
* card: 1000101 word: 3 value: 0.00350600500673
* card: 20600560 word: 6 value: 3002.55838945
*RAVEN INPUT VALUES
******************************************************************************                                 
*  SPENT FUEL  POOL  MODEL [! 1/third FA Length]                  
*  TESTING  External Events   Procedures  for LWRS/RISMC IA#2              
*                                
*  Idaho    National    Laboratory                       
*  Idaho Falls "(ID)  ,"   USA.  Date: 13-Jan-16                  
*                                
*  Nodalization   by Carlo Parisi                     
******************************************************************************                                 
*                                
*                                
=FUEL_POOL                                
*                                
*  PROBLEM  TYPE  AND   OPTION   100-199                 
*                                
*                                
*                                
100   restart  transnt                          
101   run                              
103   -1                            
*                                
*  104   mbinary                          
*                                
*                                
*                                
*  TIME  STEP  CONTROL  200-299                    
*  time  dt min   dt max   ssdtt min.ed.(plt)   maj.ed (out)   restart                     
203   3600.0  1.00E-07 0.01   07019 100   50000   500000           
*                                
*  VARIABLE TRIPS 401/599  1/1000         206NNNN0          
*                                
20600000 expanded                            
*                                
*  Cooling Sytems                            
20600560  time  0  gt  null  0  3002.55838945  n  -1.0  *  SYS1  ON
20600570  time  0  gt  null  0  6714.41300221  n  -1.0  *  SYS2  ON
*                                
20600580 tempf 002010000   gt null  0  349.00   n  -1.0  * trip by High Water Temperature    
*                                
20600590 cntrlvar 003   lt null  0  0.100 l  -1.0  * trip by Low Water Level     
*                                
*  Emergency Injection  [refill]                         
*                                
20600600 cntrlvar 003   lt null  0  2.100 n  -1.0  * Pool is emptying      
20600610  time  0  gt  timeof  1013  7179.73062023  l  -1.0  *  Time  needed  for  Operator  Action
*                                
*  Pool Break  Opening                          
20600700  time  0  gt  null  0  5186.33632408  l  -1.0  *  Large  Break  OPENING
20600710 time  0  gt null  0  1.00E+06 n  -1.0  * Large Break CLOSING (ALWAYS FALSE!)     
*                                
20600800 time  0  gt null  0  1.00E+06 l  -1.0  * Medium Break OPENING     
20600810 time  0  gt null  0  1.00E+06 n  -1.0  * Medium Break CLOSING (ALWAYS FALSE)     
*                                
*  End of Calculations                             
20608010 httemp   005000112   gt null  0  1.477E+03   l  -1.0        
20608020 httemp   005000212   gt null  0  1.477E+03   l  -1.0        
20608030 httemp   005000312   gt null  0  1.477E+03   l  -1.0        
20608040 httemp   005000412   gt null  0  1.477E+03   l  -1.0        
20608050 httemp   005000512   gt null  0  1.477E+03   l  -1.0        
20608060 httemp   005000612   gt null  0  1.477E+03   l  -1.0        
20608070 httemp   005000712   gt null  0  1.477E+03   l  -1.0        
20608080 httemp   005000812   gt null  0  1.477E+03   l  -1.0        
*                                
20608090 httemp   006000112   gt null  0  1.477E+03   l  -1.0        
20608100 httemp   006000212   gt null  0  1.477E+03   l  -1.0        
20608110 httemp   006000312   gt null  0  1.477E+03   l  -1.0        
20608120 httemp   006000412   gt null  0  1.477E+03   l  -1.0        
20608130 httemp   006000512   gt null  0  1.477E+03   l  -1.0        
20608140 httemp   006000612   gt null  0  1.477E+03   l  -1.0        
20608150 httemp   006000712   gt null  0  1.477E+03   l  -1.0        
20608160 httemp   006000812   gt null  0  1.477E+03   l  -1.0        
*                                
20609990 time  0  gt null  0  8.64E+04 n  -1.0        
*                                
*                                
*  LOGICAL  TRIPS 601/799  1001/2000         206NNNN0          
*                                
*  Cooling System                            
20610010 56 or 58 n  -1.0  *              
20610020 1001  or 59 n  -1.0  *  OFF   when  became T {failure by ecternal event or by high temperature or by low water level}   
*                                
20610030 57 or 58 n  -1.0  *              
20610040 1003  or 59 n  -1.0  *  OFF   when  became T {failure by ecternal event or by high temperature or by low water level}   
*                                
*  Operator Action                              
20610110 1002  and   1004  n  -1.0  *  "when both are true, operator action!"       [both cooling circuit failures]  
20610120 70 or 80 n  -1.0  *  "when one is true, operator action!"         [fuel pool failure]  
20610130 1011  or 1012  n  -1.0  *  "when one is true, operator action!"            
*                                
*  Emergency Injection                             
20610200 60 and   61 n  -1.0  *  "Em. Injection if pool is emptying, AND both systems are off or I have a pool breach"           
*                                
*  THE END                             
20610210 801   or 802   n  -1.0  *              
20610220 1021  or 803   n  -1.0  *              
20610230 1022  or 804   n  -1.0  *              
20610240 1023  or 805   n  -1.0  *              
20610250 1024  or 806   n  -1.0  *              
20610260 1025  or 807   n  -1.0  *              
20610270 1026  or 808   n  -1.0  *              
20610280 1027  or 809   n  -1.0  *              
20610290 1028  or 810   n  -1.0  *              
20610300 1029  or 811   n  -1.0  *              
20610310 1030  or 812   n  -1.0  *              
20610320 1031  or 813   n  -1.0  *              
20610330 1032  or 814   n  -1.0  *              
20610340 1033  or 815   n  -1.0  *              
20610350 1034  or 816   n  -1.0  *              
600   999   1035                          
*                                
*                                
*  BREAK    AREAS                         
*                                
*  LARGE BREAK                            
1000000  break1   valve                         
1000101  002000000  102010000  0.00350600500673  0.3  10.0  00000100
1000201  1  0.0   0.0                        
1000300  mtrvlv                              
1000301  70 71 0.2   0.0                     
*                                
*                                
*  MEDIUM BREAK                              
1010000  break2   valve                         
1010101  002000000   102010000   3.50E-03 0.3   10.0  00000100             
1010201  1  0.0   0.0                        
1010300  mtrvlv                              
1010301  80 81 0.2   0.0                     
*
***************************************************************
*
* minor edit variables
*
***************************************************************
0000301 mflowj   051000000
0000302 mflowj   052000000
0000303 cntrlvar 003
0000304 mflowj   006070000
0000305 httemp   006000612
0000306 httemp   006000712
0000307 httemp   006000812
.                                 
