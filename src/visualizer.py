import pygame
import sys
import math
import os
from src.simulation import Simulation


class Visualizer:
    def __init__(self, simu: Simulation) -> None:
        self.simu = simu

        pygame.init()
        # ou 16 pour que ce soit plus lisible
        self.font = pygame.font.Font(None, 14)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Fly-in Weather Map Visualizer")

        self.assets_loaded = False
        self.textures = {}
        self._load_weather_assets()

        self.LINE_COLOR = (240, 240, 240)
        self.BORDER_NORMAL = (250, 200, 255)

        self.SKY_COLOR = (135, 206, 235)

    def _load_weather_assets(self) -> None:
        asset_path = "assets"

        REQUIRED_IMAGES = {
            "cloud_slow": "cumulus_texture.bmp",
            "cloud_storm": "storm_texture.bmp"
        }

        if not os.path.exists(asset_path):
            print(
                f"[-] Dossier '{asset_path}/' manquant. Rendu simplifié activé.")
            return

        try:
            slow_img = pygame.image.load(os.path.join(
                asset_path, REQUIRED_IMAGES["cloud_slow"])).convert()
            slow_img.set_colorkey((0, 0, 0))
            self.textures["cloud_slow"] = slow_img

            storm_img = pygame.image.load(os.path.join(
                asset_path, REQUIRED_IMAGES["cloud_storm"])).convert()
            storm_img.set_colorkey((0, 0, 0))
            self.textures["cloud_storm"] = storm_img

            self.assets_loaded = True
            print("[+] Textures BMP météo chargées avec succès (avec Couleur Clé).")

        except pygame.error as e:
            print(
                f"[-] Erreur de chargement d'asset : {e}. Rendu simplifié activé.")
            self.assets_loaded = False

    def draw_map(self) -> None:
        self.screen.fill(self.SKY_COLOR)

        xs = [z.x for z in self.simu.map.zones.values()]
        ys = [z.y for z in self.simu.map.zones.values()]

        if not xs or not ys:
            return

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max_x - min_x if max_x != min_x else 1
        map_h = max_y - min_y if max_y != min_y else 1

        margin_x, margin_y = self.width * 0.03, self.height * 0.05

        scale_x = (self.width - 2 * margin_x) / map_w
        scale_y = (self.height - 2 * margin_y) / map_h

        offset_x = margin_x - (min_x * scale_x)
        offset_y = margin_y - (min_y * scale_y)

        base_scale = min(scale_x, scale_y)
        node_h = int(base_scale * 1.0)
        node_w = int(base_scale * 0.9)

        drones_by_zone = {}
        for drone in self.simu.drones:
            if not drone.path:
                continue
            zone_name = drone.path[-1][0]
            if zone_name not in drones_by_zone:
                drones_by_zone[zone_name] = []
            drones_by_zone[zone_name].append(drone.id)

        # 1. Routes : Tracées directement de centre à centre
        for connection in self.simu.map.connections:
            z1 = self.simu.map.zones[connection.zone1]
            z2 = self.simu.map.zones[connection.zone2]

            c1 = (z1.x * scale_x + offset_x, z1.y * scale_y + offset_y)
            c2 = (z2.x * scale_x + offset_x, z2.y * scale_y + offset_y)

            pygame.draw.line(self.screen, self.LINE_COLOR, c1, c2, 4)
            pygame.draw.line(self.screen, (255, 255, 255, 100), c1, c2, 1)

        # 2. Zones et Drones
        mouse_pos = pygame.mouse.get_pos()
        hovered_surplus = None  # Pour stocker la liste à afficher

        for name, zone in self.simu.map.zones.items():
            zone_type = getattr(zone, "zone_type", "normal")
            pos = (int(zone.x * scale_x + offset_x),
                   int(zone.y * scale_y + offset_y))

            zone_rect = pygame.Rect(0, 0, node_w, node_h)
            zone_rect.center = pos

            # MASQUE : Remplit le rectangle pour cacher la ligne qui passe au centre
            pygame.draw.rect(self.screen, self.SKY_COLOR, zone_rect)

            border_color = zone.color if hasattr(
                zone, "color") and zone.color else self.BORDER_NORMAL
            blit_texture = None

            if zone_type == "blocked":
                if self.assets_loaded:
                    blit_texture = self.textures["cloud_storm"]
                else:
                    pygame.draw.rect(self.screen, border_color, zone_rect)

            elif zone_type == "restricted":
                if self.assets_loaded:
                    blit_texture = self.textures["cloud_slow"]
                else:
                    pygame.draw.rect(self.screen, (160, 160, 170), zone_rect)
                border_color = zone.color if hasattr(
                    zone, "color") and zone.color else self.BORDER_NORMAL

            if blit_texture:
                tex_surface = pygame.Surface((node_w, node_h))
                tex_surface.set_colorkey((0, 0, 0))
                tex_w, tex_h = blit_texture.get_size()
                for px in range(0, node_w, tex_w):
                    for py in range(0, node_h, tex_h):
                        tex_surface.blit(blit_texture, (px, py))
                self.screen.blit(tex_surface, zone_rect.topleft)

            pygame.draw.rect(self.screen, border_color, zone_rect, 2)

            if name.lower() == "start":
                pygame.draw.circle(
                    self.screen, (0, 255, 120), pos, int(node_w/4))
                pygame.draw.circle(
                    self.screen, (255, 255, 255), pos, int(node_w/4), 2)
            elif name.lower() in ["end", "goal"]:
                pygame.draw.circle(
                    self.screen, (255, 50, 80), pos, int(node_w/4))
                pygame.draw.circle(
                    self.screen, (255, 255, 255), pos, int(node_w/4), 2)

            # Affichage des drones
            drones_in_zone = drones_by_zone.get(name, [])
            if drones_in_zone:
                MAX_DISPLAY = 6
                drone_radius = int(node_w * 0.15)
                start_y = zone_rect.bottom - drone_radius - 5
                total_drones = len(drones_in_zone)

                for i, drone_id in enumerate(drones_in_zone):
                    if i >= MAX_DISPLAY:
                        break

                    row = i // 2
                    is_left_column = (i % 2 == 0)
                    offset_x = drone_radius + 2
                    drone_x = zone_rect.centerx - \
                        offset_x if is_left_column else zone_rect.centerx + offset_x
                    drone_y = start_y - (row * (drone_radius * 2 + 2))
                    drone_pos = (int(drone_x), int(drone_y))

                    if total_drones <= MAX_DISPLAY or i < MAX_DISPLAY - 1:
                        pygame.draw.circle(
                            self.screen, (255, 50, 80), drone_pos, drone_radius)
                        pygame.draw.circle(
                            self.screen, (255, 255, 255), drone_pos, drone_radius, 1)

                        # Affichage ID du drone
                        text = self.font.render(
                            str(drone_id), True, (255, 255, 255))
                        self.screen.blit(text, text.get_rect(center=drone_pos))

                    elif i == MAX_DISPLAY - 1:
                        pygame.draw.circle(
                            self.screen, (255, 215, 0), drone_pos, drone_radius)
                        pygame.draw.circle(
                            self.screen, (0, 0, 0), drone_pos, drone_radius, 1)

                        # Affichage du petit "+"
                        text = self.font.render("+", True, (0, 0, 0))
                        self.screen.blit(text, text.get_rect(center=drone_pos))

                        # Détection du survol pour afficher l'infobulle
                        mx, my = mouse_pos
                        if math.hypot(mx - drone_x, my - drone_y) <= drone_radius:
                            hovered_surplus = (
                                mx, my, drones_in_zone[MAX_DISPLAY - 1:])

        # 3. Affichage de la bulle d'information par-dessus tout le reste
        if hovered_surplus:
            mx, my, hidden_drones = hovered_surplus
            text_str = f"Drones: {', '.join(map(str, hidden_drones))}"
            text_surf = self.font.render(text_str, True, (255, 255, 255))

            box_rect = text_surf.get_rect(topleft=(mx + 15, my - 10))
            box_rect.inflate_ip(10, 10)  # Ajoute des marges

            pygame.draw.rect(self.screen, (40, 40, 45), box_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 1)
            self.screen.blit(text_surf, (box_rect.x + 5, box_rect.y + 5))

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            self.draw_map()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()
