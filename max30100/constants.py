"""Configuration constants for MAX30100"""

class MAX30100Config:
    """Configuration constants for MAX30100"""
    
    # Register addresses
    REG_INT_STATUS = 0x00
    REG_INT_ENABLE = 0x01
    REG_FIFO_WR_PTR = 0x02
    REG_OVRFLOW_CTR = 0x03
    REG_FIFO_RD_PTR = 0x04
    REG_FIFO_DATA = 0x05
    REG_MODE_CONFIG = 0x06
    REG_SPO2_CONFIG = 0x07
    REG_LED_CONFIG = 0x09
    REG_TEMP_INT = 0x16
    REG_TEMP_FRAC = 0x17
    
    # Mode Configuration
    MODE_SHDN = 0x80
    MODE_RESET = 0x40
    MODE_TEMP_EN = 0x08
    MODE_HR_ONLY = 0x02
    MODE_SPO2_EN = 0x03
    
    # SpO2 Configuration
    SPO2_HI_RES_EN = 0x40
    SPO2_SR_1600 = 0x1C  # 1600us pulse width
    SPO2_SR_100HZ = 0x04  # 100Hz sample rate
    
    # LED Configuration
    LED_PW_MAX = 0xFF
    LED_PW_MED = 0x88
    LED_PW_LOW = 0x33
