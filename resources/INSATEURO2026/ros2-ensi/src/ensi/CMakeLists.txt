cmake_minimum_required(VERSION 3.8)
project(ensi)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Generate service interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/ColorService.srv"
  "srv/NumberService.srv"
  "srv/NumberTrianglesCubesService.srv"
  DEPENDENCIES std_msgs sensor_msgs
)

# Install Python executables
install(PROGRAMS
  scripts/color_detection_server.py
  scripts/number_detection_server.py
  scripts/shape_detection_server.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
