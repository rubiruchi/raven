*RAVEN INPUT VALUES
* card: 20600610 word: 6 value: 7179.73062023
* card: 1000101 word: 3 value: 0.00350600500673
* card: 20600570 word: 6 value: 6714.41300221
* card: time1 word: 0 value: 7200.0
* card: 20600560 word: 6 value: 3002.55838945
* card: 20600700 word: 6 value: 5186.33632408
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
*  time  dt min   dt max         ssdtt min.ed.(plt)   maj.ed (out)   restart                     
203   7200.0  1.00E-07 0.01   07019   100   50000   500000           
*                                
.
