#ifndef __STEPPER_CONTROL
#define __STEPPER_CONTROL

#define STEPPER_CONTROL_PINS_COUNT 4
#define STEPPER_SIGNAL_CYCLES_COUNT 10
#define STEPPER_SIGNAL_DELAY_US 900
#define A1_INDEX 0
#define A2_INDEX 1
#define B1_INDEX 2
#define B2_INDEX 3

class Stepper {
private:
    unsigned int pins[STEPPER_CONTROL_PINS_COUNT];
    void signalStepper(int cycleIndex);
public:
    Stepper(unsigned int a1, unsigned int a2, unsigned int b1, unsigned int b2);
    ~Stepper();
    void stepClockwise();
    void stepAnticlockwise();
};

#endif
