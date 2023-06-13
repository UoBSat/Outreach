#include <arpa/inet.h>
#include <math.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/time.h>
#include <ctime>
#include <unistd.h>
#include <csignal>
#ifndef TEST_MODE
#include <pigpio.h>
#endif
#include "commands.h"
#include "StepperControl.h"


#define ROTATION_SPEED 50


#define COMMAND_TIMEOUT_SECONDS 1
#define COMMAND_TIMEOUT_MICROSECONDS 0

using namespace std;

void commandInterpreter(uint8_t[], float);
clock_t timer;
Stepper stepperX(4, 3, 2, 18), stepperY(20, 16, 12, 7);
bool keepRunning;

void ctrl_c_handler(int signum) {
  keepRunning = false;
}

int main() {
  // Register signal for graceful shutdown
  signal(SIGINT, ctrl_c_handler);
  
  #ifndef TEST_MODE
  // Initialize GPIO library
  if (gpioInitialise() < 0) {
    perror("Unable to init GPIO library");
  }
  // Initialize UDP server
  int socketFileDescriptor = socket(AF_INET, SOCK_DGRAM, 0);
  // Set timeout in case connection is broken mid command sequence
  struct timeval timeout;
  timeout.tv_sec = COMMAND_TIMEOUT_SECONDS;
  timeout.tv_usec = COMMAND_TIMEOUT_MICROSECONDS;
  if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
    perror("Error setting socket timeout\n");
    return 0;
  }
  
  struct sockaddr_in server, client;
  unsigned int clientAddressSize = sizeof(client);
  uint8_t recvBuffer[COMMAND_BYTE_COUNT];

  server.sin_addr.s_addr = INADDR_ANY;
  server.sin_family = AF_INET;
  server.sin_port = htons(COMMAND_SERVER_PORT);

  if (bind(socketFileDescriptor, (struct sockaddr *)&server, sizeof(server)) < 0) {
    perror("Binding failed\n");
    return 0;
  }
  #endif

  
  float deltaTime = 0.0f;
  timer = clock();
  cout << "Loop starting...\n";
  keepRunning = true;
  int receivedBytesCount;

  while (keepRunning) {
    #ifndef TEST_MODE
    //printf("Listening at %d\n", server.sin_port);

    receivedBytesCount = recvfrom(
        socketFileDescriptor,
        recvBuffer,
        COMMAND_BYTE_COUNT,
        0,
        (struct sockaddr *)&client,
        (socklen_t *)&clientAddressSize);
    
    
    clientAddressSize = sizeof(client);
    commandInterpreter(recvBuffer, deltaTime);
    // Clear the receive buffer
    memset(recvBuffer, 0, sizeof(uint8_t) * COMMAND_BYTE_COUNT);
    
    #else
    // Put testing code here
    
    #endif
    
    deltaTime = ((float)(clock() - timer)) / CLOCKS_PER_SEC;
    timer = clock();
    

    // for (int i = 0; i < 8; i++) {
    //   receivedByteString[i] = ((recvBuffer[1] & (0b10000000 >> i)) == 0b10000000 >> i) + '0';
    // }

    // printf("%s\n", receivedByteString);
  }
  #ifndef TEST_MODE
  close(socketFileDescriptor);
  #endif
  // Release i2c channel
  cout << "User interrupt, shutting down...\n";
  return 0;
}

bool hasCommand(uint8_t commandByte, uint8_t mask) {
  return ((commandByte & mask) == mask);
}

/**
 * The first byte is used to detect mouse click events and the second byte is used to detect keyboard and mouse clicks
 */
void commandInterpreter(uint8_t commandBytes[], float dT) {
  if (hasCommand(commandBytes[0], X_POSITIVE)) {
    stepperX.stepClockwise();
  }
  else if (hasCommand(commandBytes[0], X_NEGATIVE)) {
    stepperX.stepAnticlockwise();
  }
  
  if (hasCommand(commandBytes[0], Y_POSITIVE)) {
    stepperY.stepClockwise();
  }
  else if (hasCommand(commandBytes[0], Y_NEGATIVE)) {
    stepperY.stepAnticlockwise();
  }
  
}
