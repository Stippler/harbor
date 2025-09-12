# 🔌 Pi Zero 2W to Motor Controller Wiring Guide

This guide shows how to connect your Raspberry Pi Zero 2W to the dual motor driver board for Harbor robot control.

## 📋 **Components Needed**

### **Hardware**
- **Raspberry Pi Zero 2W** with GPIO header pins
- **Dual Motor Driver Board** (L298N or similar - the red board in your image)
- **2x DC Motors** (geared motors work best for robots)
- **Power Supply** for motors (6-12V depending on your motors)
- **MicroSD Card** with Harbor installed
- **Jumper Wires** (female-to-female recommended)
- **Breadboard** (optional, for cleaner connections)

### **Tools**
- **Soldering iron** (if GPIO pins not installed)
- **Multimeter** (for testing connections)
- **Screwdriver** (for motor terminal connections)

## 🔧 **Motor Driver Board Overview**

Based on your red motor driver board, here are the key connections:

```
Motor Driver Board Pinout:
┌─────────────────────────────┐
│  +12V  GND   IN1  IN2  ENA │  ← Power & Motor A Control
│                             │
│   D1    R1                  │  ← Indicator LEDs
│                             │
│  MOTOR A      MOTOR B       │  ← Motor Terminal Blocks
│   +    -       +    -      │
│                             │
│  IN3  IN4  ENB  +5V  GND   │  ← Motor B Control & Logic Power
└─────────────────────────────┘
```

## 🔌 **Complete Wiring Diagram**

### **Pi Zero 2W GPIO to Motor Driver**

| **Pi Zero 2W GPIO** | **Motor Driver** | **Function** | **Wire Color** |
|---------------------|------------------|--------------|----------------|
| **GPIO 18** (Pin 12) | **IN1** | Motor A Direction 1 | 🟡 Yellow |
| **GPIO 19** (Pin 35) | **IN2** | Motor A Direction 2 | 🟠 Orange |
| **GPIO 12** (Pin 32) | **ENA** | Motor A Speed (PWM) | 🔵 Blue |
| **GPIO 20** (Pin 38) | **IN3** | Motor B Direction 1 | 🟢 Green |
| **GPIO 21** (Pin 40) | **IN4** | Motor B Direction 2 | 🟣 Purple |
| **GPIO 13** (Pin 33) | **ENB** | Motor B Speed (PWM) | ⚫ Black |
| **5V** (Pin 2 or 4) | **+5V** | Logic Power | 🔴 Red |
| **GND** (Pin 6, 9, 14, 20, 25, 30, 34, 39) | **GND** | Ground | ⚪ White |

### **Power Connections**

| **Connection** | **Description** | **Notes** |
|---------------|-----------------|-----------|
| **Motor Power +** | Connect to **+12V** on driver | Use 6-12V power supply |
| **Motor Power -** | Connect to **GND** on driver | Share ground with Pi |
| **Motor A +/-** | Connect to **MOTOR A** terminals | Left motor typically |
| **Motor B +/-** | Connect to **MOTOR B** terminals | Right motor typically |

## 📐 **Step-by-Step Wiring Instructions**

### **Step 1: Safety First**
```bash
# Power off your Pi Zero 2W completely
sudo shutdown -h now

# Disconnect all power sources
# Never wire while powered on!
```

### **Step 2: GPIO Connections (Control Signals)**
Connect these wires from Pi Zero 2W to Motor Driver:

```
Pi Zero 2W → Motor Driver
─────────────────────────
GPIO 18   → IN1    (Motor A Forward)
GPIO 19   → IN2    (Motor A Reverse) 
GPIO 12   → ENA    (Motor A Speed)
GPIO 20   → IN3    (Motor B Forward)
GPIO 21   → IN4    (Motor B Reverse)
GPIO 13   → ENB    (Motor B Speed)
5V        → +5V    (Logic Power)
GND       → GND    (Common Ground)
```

### **Step 3: Motor Connections**
```
Left Motor  → MOTOR A terminals
Right Motor → MOTOR B terminals

Note: If motor spins wrong direction, swap the + and - wires
```

### **Step 4: Power Supply**
```
External Power Supply (6-12V):
  Positive (+) → +12V on motor driver
  Negative (-) → GND on motor driver (shared with Pi GND)

⚠️  IMPORTANT: 
- Use separate power for motors (don't power motors from Pi)
- Share ground between Pi and motor power supply
- Pi gets power from USB/GPIO separately
```

## 🔍 **Visual Wiring Reference**

### **Pi Zero 2W GPIO Pinout**
```
     3V3  (1) (2)  5V     ← Use Pin 2 for +5V to motor driver
   GPIO2  (3) (4)  5V
   GPIO3  (5) (6)  GND    ← Use for GND to motor driver
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18  ← IN1 (Motor A Dir 1)
  GPIO27 (13) (14) GND
  GPIO22 (15) (16) GPIO23
     3V3 (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12  ← ENA (Motor A Speed)
  GPIO13 (33) (34) GND     ← ENB (Motor B Speed)
  GPIO19 (35) (36) GPIO16  ← IN2 (Motor A Dir 2)
  GPIO26 (37) (38) GPIO20  ← IN3 (Motor B Dir 1)
     GND (39) (40) GPIO21  ← IN4 (Motor B Dir 2)
```

## ⚡ **Power Supply Requirements**

### **Motor Driver Power**
- **Voltage**: 6V - 12V DC (depends on your motors)
- **Current**: 2A+ per motor (check motor specifications)
- **Recommended**: 12V 3A power supply for most small robots

### **Pi Zero 2W Power**
- **Separate 5V USB power** for the Pi
- **Do not power Pi from motor driver** (can cause voltage drops)

## 🧪 **Testing Your Connections**

### **1. Visual Inspection**
```bash
# Check all connections are secure
# Verify no loose wires
# Confirm power supply polarity
```

### **2. Continuity Test**
```bash
# Use multimeter to verify connections
# Check for short circuits
# Ensure proper ground connections
```

### **3. Software Test**
```bash
# Start Harbor with motor control
python app.py --host 0.0.0.0 --port 8080

# Test motors through web interface
# Check motor response and direction
```

## 🤖 **Motor Control Logic**

### **Direction Control**
```python
# Motor A Forward
IN1 = HIGH, IN2 = LOW

# Motor A Reverse  
IN1 = LOW, IN2 = HIGH

# Motor A Stop
IN1 = LOW, IN2 = LOW
```

### **Speed Control**
```python
# ENA and ENB control speed via PWM
# 0% = Stopped
# 100% = Full Speed
```

### **Robot Movement Patterns**
```python
# Forward: Both motors forward
# Backward: Both motors reverse
# Left Turn: Left motor reverse, right motor forward
# Right Turn: Left motor forward, right motor reverse
# Spin Left: Left motor reverse, right motor forward (same speed)
# Spin Right: Left motor forward, right motor reverse (same speed)
```

## ⚠️ **Safety Warnings**

### **Electrical Safety**
- ⚡ **Always power off** before making connections
- 🔌 **Check polarity** on power connections
- ⚠️ **Don't exceed voltage ratings** of your motors
- 🔥 **Motors can get hot** during extended use

### **Mechanical Safety**
- 🤖 **Test motors before mounting** to wheels/chassis
- 🔄 **Verify rotation direction** matches expected movement
- 🛑 **Have emergency stop** accessible during testing

## 🔧 **Troubleshooting**

### **Motors Don't Move**
1. Check power supply connections
2. Verify GPIO pin assignments in Harbor
3. Test with multimeter for voltage at motor terminals
4. Check motor driver LED indicators

### **Motors Move Wrong Direction**
1. Swap motor wires (+ and -)
2. Or modify software pin assignments

### **Motors Move Slowly**
1. Check power supply voltage
2. Verify PWM speed settings
3. Check for loose connections

### **One Motor Works, Other Doesn't**
1. Check individual GPIO connections
2. Test motor driver channels separately
3. Verify both motors work when swapped

## 📱 **Harbor Configuration**

The default Harbor motor configuration matches this wiring:

```python
# In harbor/motor.py - Default L298N Configuration
MOTOR_CONFIGS = {
    "l298n_default": {
        "left": {"in1_pin": 18, "in2_pin": 19, "enable_pin": 12},    # Motor A
        "right": {"in1_pin": 20, "in2_pin": 21, "enable_pin": 13}    # Motor B
    }
}
```

If you use different pins, update this configuration or use custom pin setup in the web interface.

## 🎯 **Final Testing**

Once everything is connected:

1. **Power up the Pi Zero 2W** (USB power)
2. **Connect motor power supply** (6-12V)
3. **Start Harbor**: `python app.py`
4. **Open web interface**: `http://your-pi-ip:8080`
5. **Test each motor direction** using the web controls
6. **Verify robot movement** matches button presses

Your Pi Zero 2W should now be able to control two motors through Harbor's web interface! 🎉

---

**Need Help?** Run the diagnostic script: `python diagnose_camera.py` or check the logs for any GPIO errors.
