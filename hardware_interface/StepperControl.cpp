#include "StepperControl.h"
#ifndef TEST_MODE
#include <pigpio.h>
#endif
#include <cstdio>
#include <unistd.h> // For unix file functions
#include <ctime>
#include <iostream>

using namespace std;

const unsigned int signalCycles[STEPPER_SIGNAL_CYCLES_COUNT][STEPPER_CONTROL_PINS_COUNT] = {
    {0, 0, 0, 0},
    {0, 1, 0, 0},
    {0, 1, 0, 1},
    {0, 0, 0, 1},
    {1, 0, 0, 1},
    {1, 0, 0, 0},
    {1, 0, 1, 0},
    {0, 0, 1, 0},
    {0, 1, 1, 0},
    {0, 0, 0, 0}
};

Stepper::Stepper(unsigned int a1, unsigned int a2, unsigned int b1, unsigned int b2) {
    this->pins[A1_INDEX] = a1;
    this->pins[A2_INDEX] = a2;
    this->pins[B1_INDEX] = b1;
    this->pins[B2_INDEX] = b2;
    
    #ifndef TEST_MODE
    
    for (int i = 0; i < STEPPER_CONTROL_PINS_COUNT; i++) {
        if (gpioSetMode(this->pins[i], PI_OUTPUT) != 0) {
            perror("Unable to set pin to output.");
        }
    }
    #endif
}

void Stepper::signalStepper(int cycleIndex) {
    for (int i = 0; i < STEPPER_CONTROL_PINS_COUNT; i++) {
        #ifndef TEST_MODE
        if (gpioWrite(this->pins[i], signalCycles[cycleIndex][i]) != 0) {
            perror("Unable to write to pin.");
        }
        #else
        cout << i << " : " << signalCycles[cycleIndex][i] << ", \t";
        #endif
    }
    #ifdef TEST_MODE
    cout << '\n';
    #endif
}


void Stepper::stepClockwise() {
    for (int i = 0; i < STEPPER_SIGNAL_CYCLES_COUNT; i++) {
        this->signalStepper(i);
        usleep(STEPPER_SIGNAL_DELAY_US);
    }
}

void Stepper::stepAnticlockwise() {
    for (int i = STEPPER_SIGNAL_CYCLES_COUNT - 1; i >= 0; i--) {
        this->signalStepper(i);
        usleep(STEPPER_SIGNAL_DELAY_US);
    }
}

Stepper::~Stepper() {
    #ifndef TEST_MODE
    gpioTerminate();
    #endif
}


