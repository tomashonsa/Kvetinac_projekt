from machine import ADC, Pin
def vlhkost_pudy(adc_pin=26):
    adc = ADC(Pin(adc_pin))
    raw = adc.read_u16()
    procento = 100 - int((raw / 65535) * 100)
    return procento
#knihovna pro vypocet vlhkosti pudy
