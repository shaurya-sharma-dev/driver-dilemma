"""
`player` module

This module contains the `Player` class which is a subclass of the `Entity` class from ursina. 
The `Player` class contains movement logic, collision code, etc.
"""

from ursina import *
from ursina.prefabs.ursfx import ursfx
import math

class Player(Entity):
    SPAWN_LOCATIONS = {
        0: (0.15, 0.25, 7),
        1: (0.15, 0.25, 7),
        2: (0.15, 0.25, 7),
        3: (0.15, 0.25, 7)
    }

    FINISH_LINE_Z_COORDS = {
        0: -8,
        1: -8,
        2: -8,
        3: -8
    }
    
    def __init__(self, level):
        super().__init__(
            model='player.obj',
            texture='car',
            collider='box'
        )
        self.speed = 10
        self.type = 'player'
        self.level = level

    def move_if_not_solid(self, x_dif, z_dif):
        direction = Vec3(self.world_position+(x_dif, 0, 0)).normalized()
        origin = self.world_position + (self.up*.25)
        hit_info = raycast(origin, direction, ignore=(self,), distance=abs(x_dif))
        if not hit_info.hit:
            self.x += x_dif
        else:
            if hit_info.entity.type == 'obstacle':
                self.spawn()

        direction = Vec3(self.world_position+(0, 0, z_dif)).normalized()
        origin = self.world_position + (self.up*.25)
        hit_info = raycast(origin, direction, ignore=(self,), distance=abs(z_dif))
        if not hit_info.hit:
            self.z += z_dif
        else:
            if hit_info.entity.type == 'obstacle':
                self.spawn()
    
    def check_intersection_with_obstacle(self):
        # Cast rays around the player to check for obstacles
        directions = [
            Vec3(1, 0, 0),
            Vec3(-1, 0, 0),
            Vec3(0, 0, 1),
            Vec3(0, 0, -1),
        ]

        for direction in directions:
            origin = self.world_position + (self.up * 0.25)
            hit_info = raycast(origin, direction, ignore=(self,), distance=0.125)  # Short distance

            if hit_info.hit and hit_info.entity.type == 'obstacle':
                return True

        return False  # No intersection with obstacle

    def spawn(self):
        self.set_position(self.SPAWN_LOCATIONS[self.level])
        self.steering_dir = 0

    def check_if_above_ground(self):
        # Perform raycast to check for hits in the down direction
        hit_info = raycast(self.world_position, self.down, distance=1, ignore=(self,))

        # Ensure that the raycast hit something
        if hit_info.entity:
            # Check if the entity is of type 'lb'
            if hit_info.entity.type == 'lb':
                return True

        # Return False if no relevant entity is found
        return False

    def update(self):
        x = self.position
        x[1] = x[1] + 8.75
        x[2] = x[2] + 10
        camera.set_position(x)
        camera.look_at(self)
        camera.rotation_z = 0

        moved = True
        if held_keys['a']:
            self.steering_dir -= 25 * time.dt
        elif held_keys['d']:
            self.steering_dir += 25 * time.dt
        else:
            moved = False

        if moved:
            if self.steering_dir < -30:
                self.steering_dir = -30
            elif self.steering_dir > 30:
                self.steering_dir = 30
        else:
            self.steering_dir = self.steering_dir * 0.9

        # Apply the steering rotation
        self.rotation = (0, self.steering_dir, 0)
        self.collider_setter('box')

        if held_keys['w']:
            self.move_if_not_solid(
                math.sin(math.radians(self.steering_dir)) * time.dt * -self.speed, 
                math.cos(math.radians(self.steering_dir)) * time.dt * -self.speed
            )

        if held_keys['s']:
            self.move_if_not_solid(
                math.sin(math.radians(self.steering_dir)) * time.dt * self.speed, 
                math.cos(math.radians(self.steering_dir)) * time.dt * self.speed
            )

        # Player is dead
        if self.check_intersection_with_obstacle() or not self.check_if_above_ground() or held_keys['r']:
            self.spawn()
            ursfx([(0.0, 0.0), (0.1, 0.9), (0.8, 0.1), (1.0, 0.0), (1.0, 0.0)], volume=0.8, wave='square', pitch=-10, pitch_change=-12, speed=1.5)

    def check_if_in_finish_line(self):
        return True if self.position.z <= self.FINISH_LINE_Z_COORDS[self.level] else False
