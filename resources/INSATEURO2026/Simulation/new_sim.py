#!/usr/bin/env python3
import pygame
import math
import json
# Constants
WIDTH, HEIGHT = 1080, 720  # Total screen size (split into controls + map)
CONTROL_WIDTH = 300        # Width of the control section
MAP_WIDTH = WIDTH - CONTROL_WIDTH  # Remaining width for the map
BACKGROUND_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
SLIDER_COLOR = (100, 100, 250)
SLIDER_BAR_COLOR = (180, 180, 180)
TOGGLE_ON_COLOR = (0, 255, 0)  # Green color for ON state
TOGGLE_OFF_COLOR = (255, 0, 0)  # Red color for OFF state

# Global variable to store path points
path_points = []

# Load the map image
map_image = pygame.image.load('ensi_map.png')
# Scale the map image to fit the map area
# Get the original dimensions of the image
map_original_width, map_original_height = map_image.get_size()

# Determine the maximum allowed size for the map image (MAP_WIDTH x HEIGHT)
max_map_width = MAP_WIDTH
max_map_height = HEIGHT

# Calculate the scale factor to fit the image within the map area while preserving the aspect ratio
scale_factor = min(max_map_width / map_original_width, max_map_height / map_original_height)
scale_px_to_mm=1800/MAP_WIDTH
# Calculate the new dimensions of the image
new_map_width = int(map_original_width * scale_factor)
new_map_height = int(map_original_height * scale_factor)

# Scale the map image
scaled_map_image = pygame.transform.scale(map_image, (new_map_width, new_map_height))

# Calculate the position to center the image within the map area
map_x = CONTROL_WIDTH + (max_map_width - new_map_width) // 2  # Center horizontally within map area
map_y = (max_map_height - new_map_height) // 2  # Center vertically within map area

# Load the robot image
robot_image = pygame.image.load('my_robot.png')

# Get the original dimensions of the robot image
robot_original_width, robot_original_height = robot_image.get_size()

# Scale the robot image using a much smaller scale factor for better proportions
robot_scale_factor = scale_factor * 0.1  # Make robot 10% of original scaled size
new_robot_width = int(robot_original_width * robot_scale_factor)
new_robot_height = int(robot_original_height * robot_scale_factor)

# Scale the robot image
scaled_robot_image = pygame.transform.scale(robot_image, (new_robot_width, new_robot_height))
path_points = []

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Robot Path Simulation with Controls")
font = pygame.font.Font(None, 30)

class Slider4State:
    def __init__(self, x, y, w, num_states=4, initial_state=0, title="Slider Title"):
        self.rect = pygame.Rect(x, y, w, 10)
        self.num_states = num_states
        self.state = initial_state
        self.state_positions = [x + (w / (num_states - 1)) * i for i in range(num_states)]
        self.knob_pos = self.state_positions[self.state]
        self.title = title

    def draw(self, surface):
        # Draw the slider title above the slider
        title_surface = font.render(self.title, True, BLACK)
        surface.blit(title_surface, (self.rect.x, self.rect.y - 30))  # Position the title above the slider

        # Draw the slider bar
        pygame.draw.rect(surface, SLIDER_BAR_COLOR, self.rect)
        
        # Draw the knob
        pygame.draw.circle(surface, (0, 0, 0), (int(self.knob_pos), self.rect.centery), 10)

        # Optional: Draw state labels below the slider
        for i, pos in enumerate(self.state_positions):
            label = font.render(str(i), True, BLACK)
            surface.blit(label, (pos - 5, self.rect.centery + 15))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if click is near one of the state positions
            for i, pos in enumerate(self.state_positions):
                if math.sqrt((event.pos[0] - pos)**2 +(event.pos[1]-self.rect.centery)**2) < 15:
                    self.state = i
                    self.knob_pos = pos

class InputBox:
    def __init__(self, x, y, w, title="Input Box"):
        self.rect = pygame.Rect(x, y, w, 30)
        self.color = BLACK
        self.text = ''
        self.title = title
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (0, 0, 255) if self.active else BLACK
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.set_text(self.text)
                    self.active=not self.active
                    self.color = (0, 0, 255) if self.active else BLACK
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, surface):
        # Draw the input box and the title
        pygame.draw.rect(surface, self.color, self.rect, 2)
        title_surface = font.render(self.title, True, BLACK)
        surface.blit(title_surface, (self.rect.x, self.rect.y - 20))
        
        # Draw the text
        text_surface = font.render(self.text, True, BLACK)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def set_text(self, new_text):
        self.text = new_text

class ToggleSwitch:
    def __init__(self, x, y, title="Toggle"):
        self.rect = pygame.Rect(x, y, 60, 30)
        self.state = True  # Initial state is OFF
        self.title = title

    def draw(self, surface):
        # Draw the toggle background
        color = TOGGLE_ON_COLOR if self.state else TOGGLE_OFF_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=15)

        # Draw the toggle switch
        switch_x = self.rect.x + (30 if self.state else 0)  # Position the switch inside the rectangle
        pygame.draw.circle(surface, BLACK, (switch_x + 15, self.rect.centery), 15)

        # Draw the title above the toggle
        title_surface = font.render(self.title, True, BLACK)
        surface.blit(title_surface, (self.rect.x-150, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state  # Toggle the state
                robot.update_isForward()

class Button:
    def __init__(self, x, y, w, h, title):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.color = (180, 180, 180)
        self.hover_color = (220, 220, 220)
        self.clicked=False

    def draw(self, surface):
        current_color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        
        # Draw the button title
        title_surface = font.render(self.title, True, BLACK)
        title_rect = title_surface.get_rect(center=self.rect.center)
        surface.blit(title_surface, title_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.clicked=True
            return True  # Indicate that the button was clicked
        return False

class Robot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.robot_image=scaled_robot_image
        self.isForward=True
        self.is_dragging=False
        
        # Movement control variables
        self.is_moving = False
        self.current_waypoint_index = 0
        self.target_x = x
        self.target_y = y
        self.target_angle = 0
        self.movement_speed = 2.0  # pixels per frame
        self.rotation_speed = 3.0  # degrees per frame

    def draw(self, surface:pygame.Surface):
        # Adjust the robot's position to the scaled map
        adjusted_x = self.x
        adjusted_y = self.y
        
        rotated_robot_image=pygame.transform.rotate(scaled_robot_image, self.angle)

        self.robot_image=rotated_robot_image

        robot_edge_center_x, robot_edge_center_y=self.get_robot_edge_center()
        # robot_x_projection=self.new_robot_diameter*math.cos(math.radians(self.angle)-math.atan2(new_robot_height,new_robot_width))
        # robot_y_projection=self.new_robot_diameter*math.sin(math.radians(self.angle)+math.atan2(new_robot_height,new_robot_width))
        robot_center_x, robot_center_y=self.get_robot_center()

        # Draw the scaled robot image at the adjusted position
        surface.blit(self.robot_image, (adjusted_x - robot_center_x, adjusted_y - robot_center_y))  # Center the robot image


    def draw_arrows(self, surface):
        if len(path_points) > 1:
            for i in range(len(path_points) - 1):
                start = path_points[i][0:2]
                end =  path_points[i+1][0:2]
                
                self.draw_arrow(surface, start, end)

    def draw_arrow(self, surface, start, end):
        start[0], start[1]=get_px_coordinates(start[0],start[1])
        end[0], end[1]=get_px_coordinates(end[0],end[1])

        # Calculate angle and draw arrow
        pygame.draw.line(surface, BLACK, start, end, 3)  # Draw line
        # Arrowhead drawing code
        arrow_size = 10
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        arrow_start = end
        pygame.draw.polygon(surface, BLACK, [
            (arrow_start[0], arrow_start[1]),
            (arrow_start[0] - arrow_size * math.cos(angle - 0.5), arrow_start[1] - arrow_size * math.sin(angle - 0.5)),
            (arrow_start[0] - arrow_size * math.cos(angle + 0.5), arrow_start[1] - arrow_size * math.sin(angle + 0.5))
        ])
        
    
    def update_position (self, new_x, new_y):
        self.x=new_x
        self.y=new_y
    
    def update_angle (self,new_angle):
        self.angle=new_angle

    def rotate(self, angular_velocity, angular_acceleration):
        pass
        

    def update_isForward(self):
            self.angle=self.angle+180
    
    def start_path_following(self):
        """Start following the planned path"""
        if len(path_points) > 0:
            self.is_moving = True
            self.current_waypoint_index = 0
            self.set_next_target()
    
    def stop_movement(self):
        """Stop robot movement"""
        self.is_moving = False
    
    def reset_to_start(self):
        """Reset robot to starting position"""
        self.is_moving = False
        self.current_waypoint_index = 0
        if len(path_points) > 0:
            start_point = path_points[0]
            start_x, start_y = get_px_coordinates(start_point[0], start_point[1])
            self.update_position(start_x, start_y)
            self.update_angle(start_point[2])
    
    def set_next_target(self):
        """Set the next waypoint as target"""
        if self.current_waypoint_index < len(path_points):
            waypoint = path_points[self.current_waypoint_index]
            self.target_x, self.target_y = get_px_coordinates(waypoint[0], waypoint[1])
            self.target_angle = waypoint[2]
    
    def update_movement(self):
        """Update robot position during automatic movement"""
        if not self.is_moving or len(path_points) == 0:
            return
        
        # Calculate distance to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle difference
        angle_diff = self.target_angle - self.angle
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360
        
        # Move towards target position
        if distance > self.movement_speed:
            # Normalize movement vector
            move_x = (dx / distance) * self.movement_speed
            move_y = (dy / distance) * self.movement_speed
            self.update_position(self.x + move_x, self.y + move_y)
        else:
            # Reached position target
            self.update_position(self.target_x, self.target_y)
        
        # Rotate towards target angle
        if abs(angle_diff) > self.rotation_speed:
            if angle_diff > 0:
                self.update_angle(self.angle + self.rotation_speed)
            else:
                self.update_angle(self.angle - self.rotation_speed)
        else:
            # Reached angle target
            self.update_angle(self.target_angle)
        
        # Check if waypoint is reached
        if distance <= self.movement_speed and abs(angle_diff) <= self.rotation_speed:
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(path_points):
                self.set_next_target()
            else:
                # Path completed
                self.is_moving = False
                print("Path following completed!")


    def get_robot_center(self):
        bounding_rect=self.robot_image.get_rect()
        robot_center_x,robot_center_y=bounding_rect.center

        return robot_center_x,robot_center_y
    
    def get_robot_edge_center(self):
        
        bounding_rect=self.robot_image.get_rect()
        robot_center_x,robot_center_y=bounding_rect.center
        
        robot_edge_center_x=robot_center_x+(new_robot_height//2)*math.sin(math.radians(self.angle))
        robot_edge_center_y=robot_center_y+(new_robot_height//2)*math.cos(math.radians(self.angle))
        
        return robot_edge_center_x,robot_edge_center_y
    
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            robot_center_x, robot_center_y=self.get_robot_center()
            distance = math.hypot(mouse_x - (-robot_center_x+self.x), mouse_y - (-robot_center_y+self.y))
            if distance <= math.hypot(new_robot_height,new_robot_width):  # Click inside the robot
                self.is_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x, mouse_y = event.pos
            self.update_position(mouse_x, mouse_y)
            robot_x_mm, robot_y_mm=get_mm_coordinates(mouse_x,mouse_y)
            target_x_box.set_text(str(round(robot_x_mm,3)))
            target_y_box.set_text(str(round(robot_y_mm,3)))


class AngleWheel:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.knob_radius = 10  # Small circle for the knob
        self.is_dragging = False
        self.angle = 0  # Initial angle


    def draw(self, surface):
        # Draw the outer circle (wheel)
        pygame.draw.circle(surface, (150, 150, 150), (self.x, self.y), self.radius, 5)

        # Draw the knob position
        knob_x = self.x + int(self.radius * math.cos(math.radians(self.angle)))
        knob_y = self.y - int(self.radius * math.sin(math.radians(self.angle)))
        pygame.draw.circle(surface, (255, 0, 0), (knob_x, knob_y), self.knob_radius)

        # Display the current angle as text
        angle_text = font.render(f"Angle: {int(self.angle)}°", True, BLACK)
        surface.blit(angle_text, (self.x - 40, self.y + self.radius + 20))

    def set_angle(self, angle):
        self.angle=angle
        robot.update_angle(self.angle)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            distance = math.hypot(mouse_x - self.x, mouse_y - self.y)
            if distance <= self.radius+10:  # Click inside the wheel
                self.is_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            mouse_x, mouse_y = event.pos
            rel_x, rel_y = mouse_x - self.x, mouse_y - self.y
            self.set_angle((math.degrees(math.atan2(-rel_y, rel_x)) + 360) % 360)

def save_path():
    """Function to save the path points to a file."""
    if path_points:
        with open('path_points.json', 'w') as f:
            json.dump(path_points, f, indent=4)
        print("Path points saved!")
    else:
        print("No points to save.")

def get_mm_coordinates(mouse_x, mouse_y):
    if mouse_x<map_x:
        x_mm_coordinates=0
    else:
        x_mm_coordinates=(min((abs((mouse_x-map_x)/new_map_width)*1800),1800))

    if mouse_y>map_y+new_map_height:
        y_mm_coordinates=0
    else:
        y_mm_coordinates=(min(abs(((mouse_y-map_y)/new_map_height*1200)-1200),1200))

    return x_mm_coordinates,y_mm_coordinates

def get_px_coordinates(x_mm_coordinates, y_mm_coordinates):
    x_px_coordinates=(x_mm_coordinates/1800)*new_map_width+map_x
    y_px_coordinates=(abs(1200-y_mm_coordinates)/1200)*new_map_height+map_y

    return x_px_coordinates,y_px_coordinates


def draw_controls(mouse_x, mouse_y):
    """Draw the UI controls on the left side."""
    # Set control section background
    pygame.draw.rect(screen, (240, 240, 240), pygame.Rect(0, 0, CONTROL_WIDTH, HEIGHT))

    # Draw UI elements like sliders, buttons, etc.
    slider1.draw(screen)
    slider2.draw(screen)
    slider3.draw(screen)
    slider4.draw(screen)

    # Draw the toggle for "Is it forward?"
    toggle.draw(screen)

    # Display current mouse coordinates

    x_mm_coordinates,y_mm_coordinates=get_mm_coordinates(mouse_x,mouse_y)
    #coord_text = font.render(f"Mouse X: {(mouse_x-300)*scale_px_to_mm}, Y: {(mouse_y-map_y)*scale_px_to_mm}", True, BLACK)
    coord_text = font.render("Mouse X: {:.2f},       Y: {:.2f}".format(x_mm_coordinates,y_mm_coordinates),True,BLACK)
    screen.blit(coord_text, (20, 660))  # Position text in the control panel

    # Draw the input boxes
    target_x_box.draw(screen)
    target_y_box.draw(screen)
    target_angle_box.draw(screen)

    # Draw the validation button
    validate_button.draw(screen)
    
    undo_button.draw(screen)

    save_button.draw(screen)

    # Draw movement control buttons
    play_button.draw(screen)
    pause_button.draw(screen)
    reset_button.draw(screen)

    # Draw the angle selection wheel
    angle_wheel.draw(screen)

def draw_map():
    """Draw the map section on the right side of the screen."""
    # Draw the scaled map image centered in the map section
    screen.blit(scaled_map_image, (map_x, map_y))
    
    # Draw the robot on the map section
    robot.draw(screen)

    # Draw arrows connecting the path points
    robot.draw_arrows(screen)

def handle_events(event):
    """Handle events like mouse clicks and key presses."""
    slider1.handle_event(event)
    slider2.handle_event(event)
    slider3.handle_event(event)
    slider4.handle_event(event)

    target_x_entry= target_x_box.handle_event(event)
    target_y_entry= target_y_box.handle_event(event)
    target_angle_entry= target_angle_box.handle_event(event)


    if target_x_entry:
        
        robot.update_position(get_px_coordinates(float(target_x_box.text),0)[0],robot.y)
    if target_y_entry:
        robot.update_position(robot.x,get_px_coordinates(0,float(target_y_box.text))[1])

    if target_angle_entry:
        angle_wheel.set_angle(float(target_angle_box.text))
    toggle.handle_event(event)  # Handle toggle events

    angle_wheel.handle_event(event)

    robot.handle_event(event)

    if validate_button.handle_event(event):
        # Get the target coordinates from input boxes
        global path_points
        try:
            target_x= float(target_x_box.text)
            target_y = float(target_y_box.text)
            TargetAngle=float(angle_wheel.angle)
            is_forward = toggle.state
            linear_velocity_choice = int(slider1.state)
            angular_velocity_choice = int(slider2.state)
            linear_acceleration_choice = int(slider3.state)
            angular_acceleration_choice = int(slider4.state)
            clicked_point = [(target_x),
                             (target_y),
                             TargetAngle,
                             is_forward,
                             linear_velocity_choice,
                             angular_velocity_choice,
                             linear_acceleration_choice,
                             angular_acceleration_choice
                            ]  # Adjust for control width
            path_points.append(clicked_point)
            x_px_robot_coordinates, y_px_robot_coordinates=get_px_coordinates(target_x, target_y)
            robot.update_position(x_px_robot_coordinates,y_px_robot_coordinates)
            robot.draw_arrows(screen)
            print(path_points)

        except ValueError:
            print("Invalid input. please validate trajectory")  # Optional error handling

    if save_button.handle_event(event):
        save_path()

    if undo_button.handle_event(event):
        path_points=path_points[:-1]

    # Handle movement control buttons
    if play_button.handle_event(event):
        robot.start_path_following()
        print("Starting path following...")
    
    if pause_button.handle_event(event):
        robot.stop_movement()
        print("Movement paused.")
    
    if reset_button.handle_event(event):
        robot.reset_to_start()
        print("Robot reset to start position.")

    # Handle mouse click in the map area to set target_X and target_Y
    if event.type == pygame.MOUSEBUTTONDOWN:
        if map_x < event.pos[0] < map_x+new_map_width and map_y< event.pos[1]< map_y+new_map_height:  # Check if click is inside the map area
            x_mm_coordinates,y_mm_coordinates=get_mm_coordinates(event.pos[0],event.pos[1])
            target_x_box.set_text(str(round(x_mm_coordinates,3))) # Set X coordinate
            target_y_box.set_text(str(round(y_mm_coordinates,3))) # Set Y coordinate

            robot.update_position(event.pos[0], event.pos[1])

def main():
    clock = pygame.time.Clock()
    running = True

    global robot, slider1, slider2, slider3, slider4, target_x_box, target_y_box, toggle, validate_button,angle_wheel, save_button, undo_button, path_points, target_angle_box, play_button, pause_button, reset_button

    # Create sliders for velocity and acceleration choices
    slider1 = Slider4State(20, 60, 200, title="Linear Velocity")
    slider2 = Slider4State(20, 140, 200, title="Angular Velocity")
    slider3 = Slider4State(20, 220, 200, title="Linear Acceleration")
    slider4 = Slider4State(20, 300, 200, title="Angular Acceleration")

    # Create input boxes for target_X and target_Y
    target_x_box = InputBox(20, 380, 120, title="Target X")
    target_y_box = InputBox(20, 440, 120, title="Target Y")
    target_angle_box = InputBox(20, 500, 120, title="Target Angle")

    # Create toggle switch for "Is it forward?"
    toggle = ToggleSwitch(200, 620, title="Is it forward")

    #Initialize the validate trajectory button (no angle)
    undo_button=Button(20, 560, 100, 40, "UNDO")
    
    #initialize the validation button
    validate_button = Button(130, 560, 100, 40, "Validate")

    save_button= Button(240, 560, 50, 40, "save")

    # Movement control buttons
    play_button = Button(20, 620, 60, 30, "PLAY")
    pause_button = Button(90, 620, 60, 30, "PAUSE") 
    reset_button = Button(160, 620, 60, 30, "RESET")

    # Create an instance of AngleWheel
    angle_wheel = AngleWheel(215, 400, 50) 

    # Initialize robot in the map area (starting from CONTROL_WIDTH for x-coordinate)
    robot = Robot(CONTROL_WIDTH + MAP_WIDTH // 2, HEIGHT // 2)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Press ESC to exit fullscreen
                    running = False
            handle_events(event)

        # Drawing
        screen.fill(BACKGROUND_COLOR)

        # Get current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Drawing
        screen.fill(BACKGROUND_COLOR)
        
        # Draw the control panel with mouse coordinates
        draw_controls(mouse_x, mouse_y)

        # Update robot movement
        robot.update_movement()
        
        # Draw the map and the robot
        draw_map()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()