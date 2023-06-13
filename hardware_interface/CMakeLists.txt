cmake_minimum_required(VERSION 2.8)

project(StepperController)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -lm -lpigpio -lrt")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -lm -D TEST_MODE")

add_executable(
StepperController
main.cpp
commands.h
StepperControl.h
StepperControl.cpp
)

target_link_libraries(StepperController PRIVATE pigpio)

