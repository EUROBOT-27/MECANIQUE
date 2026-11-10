################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Inc/custom_memory_manager.c \
../Core/Inc/dma_transport.c \
../Core/Inc/microros_allocators.c \
../Core/Inc/microros_time.c 

C_DEPS += \
./Core/Inc/custom_memory_manager.d \
./Core/Inc/dma_transport.d \
./Core/Inc/microros_allocators.d \
./Core/Inc/microros_time.d 

OBJS += \
./Core/Inc/custom_memory_manager.o \
./Core/Inc/dma_transport.o \
./Core/Inc/microros_allocators.o \
./Core/Inc/microros_time.o 


# Each subdirectory must supply rules for building sources it contributes
Core/Inc/%.o Core/Inc/%.su Core/Inc/%.cyclo: ../Core/Inc/%.c Core/Inc/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F446xx -c -I../../Core/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../Middlewares/Third_Party/FreeRTOS/Source/include -I../../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -I../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Core-2f-Inc

clean-Core-2f-Inc:
	-$(RM) ./Core/Inc/custom_memory_manager.cyclo ./Core/Inc/custom_memory_manager.d ./Core/Inc/custom_memory_manager.o ./Core/Inc/custom_memory_manager.su ./Core/Inc/dma_transport.cyclo ./Core/Inc/dma_transport.d ./Core/Inc/dma_transport.o ./Core/Inc/dma_transport.su ./Core/Inc/microros_allocators.cyclo ./Core/Inc/microros_allocators.d ./Core/Inc/microros_allocators.o ./Core/Inc/microros_allocators.su ./Core/Inc/microros_time.cyclo ./Core/Inc/microros_time.d ./Core/Inc/microros_time.o ./Core/Inc/microros_time.su

.PHONY: clean-Core-2f-Inc

