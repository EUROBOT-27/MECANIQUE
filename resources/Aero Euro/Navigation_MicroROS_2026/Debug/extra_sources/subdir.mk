################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../extra_sources/custom_memory_manager.c \
../extra_sources/microros_allocators.c \
../extra_sources/microros_time.c 

C_DEPS += \
./extra_sources/custom_memory_manager.d \
./extra_sources/microros_allocators.d \
./extra_sources/microros_time.d 

OBJS += \
./extra_sources/custom_memory_manager.o \
./extra_sources/microros_allocators.o \
./extra_sources/microros_time.o 


# Each subdirectory must supply rules for building sources it contributes
extra_sources/%.o extra_sources/%.su extra_sources/%.cyclo: ../extra_sources/%.c extra_sources/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F446xx -c -I../../Core/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../Middlewares/Third_Party/FreeRTOS/Source/include -I../../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -I../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-extra_sources

clean-extra_sources:
	-$(RM) ./extra_sources/custom_memory_manager.cyclo ./extra_sources/custom_memory_manager.d ./extra_sources/custom_memory_manager.o ./extra_sources/custom_memory_manager.su ./extra_sources/microros_allocators.cyclo ./extra_sources/microros_allocators.d ./extra_sources/microros_allocators.o ./extra_sources/microros_allocators.su ./extra_sources/microros_time.cyclo ./extra_sources/microros_time.d ./extra_sources/microros_time.o ./extra_sources/microros_time.su

.PHONY: clean-extra_sources

