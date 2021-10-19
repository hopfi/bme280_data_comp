import os
from os.path import exists
import numpy as np
from bitstring import BitArray, BitStream

# Compensation equations ported from datasheet to pythonp

def BME280_compensate_T(adc_T):
    # Constants extracted from sensor
    dig_T1 = 28181
    dig_T2 = 27029
    dig_T3 = 50

    # Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC. 
    # t_fine carries fine temperature as global value 
    # Calculates T in counts? To get real Temperature value multiply result by resolution of 0.01degC
    var1_temp1 = (adc_T>>3) - (dig_T1<<1)
    var1_temp2 = var1_temp1 * dig_T2
    var1 = var1_temp2>>11
    #var1 = ((((adc_T>>3) - (dig_T1<<1))) * (dig_T2)) >> 11

    var2_temp1 = (adc_T>>4) - (dig_T1)
    var2_temp2 = (var2_temp1 * var2_temp1)>>12
    var2_temp3 = var2_temp2 * dig_T3
    var2 = var2_temp3>>14
    #var2 = (((((adc_T>>4) - (dig_T1)) * ((adc_T>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    
    
    t_fine = var1 + var2
    T  = (t_fine * 5 + 128) >> 8
    return T, t_fine

def BME280_compensate_T_BINARY(adc_T):
    # Constants extracted from sensor
    dig_T1 = 28181
    dig_T2 = 27029
    dig_T3 = 50

    # Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC. 
    # t_fine carries fine temperature as global value 
    # Calculates T in counts? To get real Temperature value multiply result by resolution of 0.01degC
    var1_temp1 = (adc_T>>3) - (dig_T1<<1)
    var1_temp2 = var1_temp1 * dig_T2
    var1 = var1_temp2>>11
    #var1 = ((((adc_T>>3) - (dig_T1<<1))) * (dig_T2)) >> 11

    var2_temp1 = (adc_T>>4) - (dig_T1)
    var2_temp2 = (var2_temp1 * var2_temp1)>>12
    var2_temp3 = var2_temp2 * dig_T3
    var2 = var2_temp3>>14
    #var2 = (((((adc_T>>4) - (dig_T1)) * ((adc_T>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    
    
    t_fine = var1 + var2
    T  = (t_fine * 5 + 128) >> 8
    return T, t_fine



def BME280_compensate_P(adc_P, t_fine):
    # Constants extracted from sensor
    dig_P1=36835
    dig_P2=-10440
    dig_P3=3024
    dig_P4=8789
    dig_P5=-128
    dig_P6=-7
    dig_P7=12300
    dig_P8=-12000
    dig_P9=5000

    # Returns pressure in Pa as unsigned 32 bit integer in Q24.8 format (24 integer bits and 8 fractional bits). 
    # Output value of “24674867” represents 24674867/256 = 96386.2 Pa = 963.862 hPa
    var1 = (t_fine) - 128000
    var2 = var1 * var1 * dig_P6
    var2 = var2 + ((var1*dig_P5)<<17)
    var2 = var2 + ((dig_P4)<<35)
    var1 = ((var1 * var1 * dig_P3)>>8) + ((var1 * dig_P2)<<12)
    var1 = ((((1)<<47)+var1))*(dig_P1)>>33
    if (var1 == 0):
        return 0; # avoid exception caused by division by zero
    p = 1048576 - adc_P
    p = (((p<<31)-var2)*3125)/var1
    var1 = (dig_P9 * (int(p)>>13) * (int(p)>>13)) >> 25
    var2 = int(dig_P8 * p) >> 19
    p = (int(p + var1 + var2) >> 8) + ((dig_P7)<<4)
    return p

def BME280_compensate_P_ALT(adc_P, t_fine):
    # Constants extracted from sensor
    dig_P1=36835
    dig_P2=-10440
    dig_P3=3024
    dig_P4=8789
    dig_P5=-128
    dig_P6=-7
    dig_P7=12300
    dig_P8=-12000
    dig_P9=5000

    p_var1_temp1 = (t_fine) - 128000 #ok
    p_var1_temp2 = p_var1_temp1 * p_var1_temp1 #ok
    p_var1_temp3 = (p_var1_temp2 * dig_P3) >> 8 #ok
    p_var1_temp4 = (p_var1_temp1 * dig_P2) << 12 #ok
    p_var1_temp5 = p_var1_temp3 + p_var1_temp4 #ok
    p_var1_temp6 = (1 << 47) + p_var1_temp5 #ok
    p_var1 = (p_var1_temp6 * dig_P1) >> 33 #ok

    p_var2_temp1 = p_var1_temp2 * dig_P6 #ok
    #p_var2_temp2 = (p_var1 * dig_P5) << 17
    p_var2_temp2 = (p_var1_temp1 * dig_P5) << 17 #ok
    p_var2_temp3 = p_var2_temp1 + p_var2_temp2 #ok
    p_var2_temp4 = dig_P4 << 35 #ok
    p_var2 = p_var2_temp3 + p_var2_temp4 #ok

    if p_var1 == 0:
        p = 0
    else:
        p_temp1 = 1048576 - adc_P
        p_temp2 = (p_temp1 << 31) - p_var2
        p_temp3 = p_temp2 * 3125 #5427f28318a88400
        p_quo = int(p_temp3 / p_var1)
        var3_temp1 = (p_quo >> 13) * (p_quo >> 13)
        var3 = (dig_P9 * var3_temp1) >> 25
        var4 = (dig_P8 * p_quo) >> 19
        p_temp4 = var3 + var4
        p_temp5 = (p_quo + p_temp4) >> 8
        p_temp6 = p_temp5 + (dig_P7 << 4)
        p = p_temp6

    return p



def BME280_compensate_H(adc_H, t_fine):
    # Constants extracted from sensor
    dig_H1=75
    dig_H2=341
    dig_H3=0
    dig_H4=371
    dig_H5=50
    dig_H6=30

    # Returns humidity in %RH as unsigned 32 bit integer in Q22.10 format (22 integer and 10 fractional bits). 
    # Output value of “47445” represents 47445/1024 = 46.333 %RH 
    v_x1_u32r = t_fine - 76800
    v_x1_u32r = (((((adc_H << 14) - (dig_H4 << 20) - (dig_H5 * v_x1_u32r)) + 16384) >> 15) * (((((((v_x1_u32r * dig_H6) >> 10) * (((v_x1_u32r * dig_H3) >> 11) + 32768)) >> 10) + 2097152) * dig_H2 + 8192) >> 14))
    v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * (dig_H1)) >> 4))
    # v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r)
    if v_x1_u32r < 0:
        v_x1_u32r = 0
    else:
        v_x1_u32r = v_x1_u32r

    #v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r)
    if v_x1_u32r > 419430400:
        v_x1_u32r = 419430400
    else:
        v_x1_u32r = v_x1_u32r

    return (v_x1_u32r>>12)


def BME280_compensate_H_ALT(adc_H, t_fine):
    dig_H1=75
    dig_H2=341
    dig_H3=0
    dig_H4=371
    dig_H5=50
    dig_H6=30

    h_var1        = t_fine - 76800;

    h_var2_temp1  = adc_H << 14
    h_var2_temp2  = dig_H4 << 20
    h_var2_temp3  = dig_H5 * h_var1
    h_var2_temp4  = h_var2_temp1 - h_var2_temp2 - h_var2_temp3 + 16384 >> 15
    h_var2_temp5  = (h_var1 * dig_H6) >> 10
    h_var2_temp6  = (h_var1 * dig_H3) >> 11
    h_var2_temp7  = h_var2_temp6 + 32768;
    h_var2_temp8  = (h_var2_temp5 * h_var2_temp7) >> 10
    h_var2_temp9  = dig_H2 + 8192;
    h_var2_temp10 = h_var2_temp8 + 2097152;
    h_var2_temp11_temp = (h_var2_temp10 * h_var2_temp9)# & 0x00000000FFFFFFFF
    h_var2_temp11 = (h_var2_temp11_temp) >> 14
    h_var2        = (h_var2_temp4 * h_var2_temp11)# & 0x00000000FFFFFFFF

    h_var3_temp1 = h_var2 >> 15
    h_var3_temp2 = (h_var3_temp1 * h_var3_temp1) >> 7
    h_var3_temp3 = (h_var3_temp2 * dig_H1) >> 4
    h_var3       = h_var2 - h_var3_temp3;

    if h_var3 < 0:
        h = 0
    else:
        h_temp1 = h_var3 >> 12
        h = h_temp1

    if h_var3 > 419430400:
        h_temp1 = 419430400 >> 12
        h = h_temp1;
    else:
        h_temp1 = h_var3 >> 12
        h = h_temp1

    return h

def resize(slv, sgn, nbit):
    data = slv & (2**nbit - 1)

    sizeOfslv = number of bits in slv

    if sgn == "signed":
        if (slv & (1<<sizeOfslv)) >> sizeOfslv == 1:
            data = data | (1<<(nbit-1))

    return data

a = resize(0x80, "signed", 4)


Temp, t_fine = BME280_compensate_T(1)
press = BME280_compensate_P(1, t_fine)        # result is  29563023
press_ALT = BME280_compensate_P_ALT(1, t_fine) #result is 260673444
hum = BME280_compensate_H(1, t_fine)
hum_ALT = BME280_compensate_H_ALT(1, t_fine)

Temp, t_fine = BME280_compensate_T(524287)
press = BME280_compensate_P(1, t_fine)
press_ALT = BME280_compensate_P_ALT(1, t_fine)
hum = BME280_compensate_H(1, t_fine)
hum_ALT = BME280_compensate_H_ALT(1, t_fine)


Temp, t_fine = BME280_compensate_T(3) #262143
press = BME280_compensate_P(1, t_fine)
press_ALT = BME280_compensate_P_ALT(1, t_fine)
hum = BME280_compensate_H(1, t_fine)
hum_ALT = BME280_compensate_H_ALT(1, t_fine)

T_raw = 537104
p_raw = 348896
H_raw = 33676
T, t_fine = BME280_compensate_T(T_raw)
p = BME280_compensate_P(p_raw, t_fine)
H = BME280_compensate_H(H_raw, t_fine)

file_path = os.path.dirname(__file__)

stimFile = file_path + "/stimData.txt"
if exists(stimFile) == True:
    os.remove(stimFile)

stimFileHandle = open(stimFile,"w+")

#for inValue in range(-2**31, 2**31-1, 2**16):
#for inValue in np.logspace(-2**31, 2**31-1,num=2**16,dtype='int'):
#    T, t_fine = BME280_compensate_T(inValue)
#    p = BME280_compensate_P(inValue, t_fine)
#    h = bme280_compensate_H(inValue, t_fine)
#    stimFileHandle.write(f"{inValue}, {T}, {p}, {h}\n")

inValue = 0
for shiftIdx in range(0, 64, 1):
    if shiftIdx <= 31:
        inValue = (inValue << 1) | 1
    elif shiftIdx > 31:
        inValue = (inValue & 0x7fff_ffff) << 1

    T, t_fine = BME280_compensate_T(inValue)
    T = abs(T)
    p = abs(BME280_compensate_P(inValue, t_fine))
    h = abs(BME280_compensate_H(inValue, t_fine))
    stimFileHandle.write(f"{inValue:032b}, {T:032b}, {p:032b}, {h:032b}\n")

stimFileHandle.close()