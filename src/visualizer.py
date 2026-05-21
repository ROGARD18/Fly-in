import pygame
import sys
from src.simulation import Simulation


class Visualizer:
    def __init__(self, simu: Simulation,
                 width: int = 800,
                 height: int = 600) -> None:
        self.simu = simu
        self.width = width
        self.height = height

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")

        self.BG_COLOR = (30, 30, 30)
        self.LINE_COLOR = (100, 100, 100)
        self.NODE_COLOR = (200, 200, 200)
        self.GOAL_COLOR = (50, 200, 50)
        self.START_COLOR = (200, 50, 50)

    def draw_map(self) -> None:

        scale = 50
        offset_x, offset_y = 50, 50

        for connection in self.simu.map.connections:
            z1 = self.simu.map.zones[connection.zone1]
            z2 = self.simu.map.zones[connection.zone2]

            p1 = (z1.x * scale + offset_x, z1.y * scale + offset_y)
            p2 = (z2.x * scale + offset_x, z2.y * scale + offset_y)
            pygame.draw.line(self.screen, self.LINE_COLOR, p1, p2, 2)

        for name, zone in self.simu.map.zones.items():
            color = self.NODE_COLOR
            if getattr(zone, "zone", "") == "normal":
                color = self.NODE_COLOR
            if zone.zone_type == "blocked":
                color = (100, 20, 20)

            pos = (int(float(zone.x) * scale + offset_x),
                   int(float(zone.y) * scale + offset_y))
            pygame.draw.circle(self.screen, color, pos, 15)
    
    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.screen.fill(self.BG_COLOR)
            self.draw_map()

            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()