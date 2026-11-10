################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.c \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.c \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.c \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.c \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.c \
../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.c 

C_DEPS += \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.d \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.d \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.d \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.d \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.d \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.d 

OBJS += \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.o \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.o \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.o \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.o \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.o \
./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.o 


# Each subdirectory must supply rules for building sources it contributes
libmicroros/uros_include/test_msgs/test_msgs/srv/detail/%.o libmicroros/uros_include/test_msgs/test_msgs/srv/detail/%.su libmicroros/uros_include/test_msgs/test_msgs/srv/detail/%.cyclo: ../libmicroros/uros_include/test_msgs/test_msgs/srv/detail/%.c libmicroros/uros_include/test_msgs/test_msgs/srv/detail/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F446xx -c -I../../Core/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../Middlewares/Third_Party/FreeRTOS/Source/include -I../../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -I../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-libmicroros-2f-uros_include-2f-test_msgs-2f-test_msgs-2f-srv-2f-detail

clean-libmicroros-2f-uros_include-2f-test_msgs-2f-test_msgs-2f-srv-2f-detail:
	-$(RM) ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__functions.su ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/arrays__type_support.su ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__functions.su ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/basic_types__type_support.su ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__functions.su ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.cyclo ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.d ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.o ./libmicroros/uros_include/test_msgs/test_msgs/srv/detail/empty__type_support.su

.PHONY: clean-libmicroros-2f-uros_include-2f-test_msgs-2f-test_msgs-2f-srv-2f-detail

