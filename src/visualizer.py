import sys
import math
import os
from src.simulation import Simulation
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Visualizer:
    def __init__(self, simu: Simulation) -> None:
        try:
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
            import pygame
        except Exception as e:
            raise (e)
        self.simu = simu

        pygame.init()
        print()
        self.font = pygame.font.Font(None, 14)

        self.capacity_font = pygame.font.Font(None, 11)

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

        except pygame.error as e:
            print(
                f"Asset Error: {e}.")
            self.assets_loaded = False

    def draw_star(self, surface, color, center_pos, outer_radius, inner_radius, points=5):
        cx, cy = center_pos
        angle_step = math.pi / points
        vertices = []

        start_angle = -math.pi / 2

        for i in range(points * 2):
            r = outer_radius if i % 2 == 0 else inner_radius
            theta = start_angle + i * angle_step

            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            vertices.append((x, y))

        pygame.draw.polygon(surface, color, vertices)

    def draw_map(self, progress: float = 0.0) -> None:
        self.screen.fill(self.SKY_COLOR)

        xs = [z.x for z in self.simu.map.zones.values()]
        ys = [z.y for z in self.simu.map.zones.values()]

        if not xs or not ys:
            return

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max_x - min_x if max_x != min_x else 1
        map_h = max_y - min_y if max_y != min_y else 1

        margin_x, margin_y = self.width * 0.05, self.height * 0.05

        scale_x = (self.width - 2 * margin_x) / (map_w + 1.5)
        scale_y = (self.height - 2 * margin_y) / (map_h + 1.5)

        base_scale = min(scale_x, scale_y)
        MAX_SCALE = min(self.width, self.height) * 0.15
        base_scale = min(base_scale, MAX_SCALE)

        node_h = int(base_scale * 0.8)
        node_w = int(base_scale * 0.8)

        offset_x = margin_x - (min_x * base_scale)
        offset_y = (self.height - (map_h * base_scale)) / \
            2 - (min_y * base_scale)

        drone_radius = int(node_w * 0.15)
        current_turn = getattr(self, "current_turn", 0)

        def get_turn_data(turn):
            d_by_z = {}
            for d in self.simu.drones:
                if not d.path:
                    continue
                idx = min(turn, len(d.path) - 1)
                z = d.path[idx][0]
                if z not in d_by_z:
                    d_by_z[z] = []
                d_by_z[z].append(d.id)

            coords = {}
            hidden_plus = {}

            for z_name, d_list in d_by_z.items():
                z_obj = self.simu.map.zones[z_name]
                cx = int(z_obj.x * base_scale + offset_x)
                cy = int(z_obj.y * base_scale + offset_y)
                start_y = cy + (node_h // 2) - drone_radius - 5

                for i, d_id in enumerate(d_list):
                    if i < 5 or (i == 5 and len(d_list) <= 6):
                        row = i // 2
                        off_x = drone_radius + 2
                        dx = cx - off_x if (i % 2 == 0) else cx + off_x
                        dy = start_y - (row * (drone_radius * 2 + 2))
                        coords[d_id] = (dx, dy, True)
                    else:
                        row = 5 // 2
                        off_x = drone_radius + 2
                        dx = cx - off_x if (5 % 2 == 0) else cx + off_x
                        dy = start_y - (row * (drone_radius * 2 + 2))
                        coords[d_id] = (dx, dy, False)
                        hidden_plus[z_name] = (dx, dy, d_list[5:])

            return coords, hidden_plus, d_by_z

        coords_now, hidden_now, drones_by_zone = get_turn_data(current_turn)
        coords_next, _, _ = get_turn_data(current_turn + 1)

        for connection in self.simu.map.connections:
            z1 = self.simu.map.zones[connection.zone1]
            z2 = self.simu.map.zones[connection.zone2]

            c1 = (z1.x * base_scale + offset_x, z1.y * base_scale + offset_y)
            c2 = (z2.x * base_scale + offset_x, z2.y * base_scale + offset_y)

            pygame.draw.line(self.screen, self.LINE_COLOR, c1, c2, 4)
            pygame.draw.line(self.screen, (255, 255, 255, 100), c1, c2, 1)

        mouse_pos = pygame.mouse.get_pos()
        hovered_surplus = None

        for name, zone in self.simu.map.zones.items():
            zone_type = getattr(zone, "zone_type", "normal")
            pos = (int(zone.x * base_scale + offset_x),
                   int(zone.y * base_scale + offset_y))
            zone_rect = pygame.Rect(0, 0, node_w, node_h)
            zone_rect.center = pos

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

            current_count = len(drones_by_zone.get(name, []))
            max_capacity = getattr(zone, "max_drones", 0)
            cap_text = f"{current_count}/{max_capacity}"
            cap_surf = self.capacity_font.render(cap_text, True, (80, 80, 80))
            cap_rect = cap_surf.get_rect()
            cap_rect.bottomright = (zone_rect.right - 3, zone_rect.bottom - 3)
            self.screen.blit(cap_surf, cap_rect)

            if zone_type == "priority":
                outer_r = min(node_w, node_h) * 0.30
                inner_r = outer_r * 0.45
                self.draw_star(self.screen, (255, 215, 0),
                               pos, outer_r, inner_r, 5)

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

        for drone in self.simu.drones:
            if drone.id not in coords_now:
                continue

            x_now, y_now, vis_now = coords_now[drone.id]
            x_next, y_next, vis_next = coords_next.get(
                drone.id, coords_now[drone.id])

            anim_x = x_now + (x_next - x_now) * progress
            anim_y = y_now + (y_next - y_now) * progress

            if not vis_now and not vis_next and progress < 0.9:
                continue

            pygame.draw.circle(self.screen, (255, 50, 80),
                               (int(anim_x), int(anim_y)), drone_radius)
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (int(anim_x), int(anim_y)), drone_radius, 1)

            text = self.font.render(str(drone.id), True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(
                center=(int(anim_x), int(anim_y))))

        # --- CALQUE 4 : SYMBOLE + ET INFOBULLES ---
        for z_name, (hx, hy, hidden_list) in hidden_now.items():
            pygame.draw.circle(self.screen, (255, 215, 0),
                               (int(hx), int(hy)), drone_radius)
            pygame.draw.circle(self.screen, (0, 0, 0),
                               (int(hx), int(hy)), drone_radius, 1)

            text = self.font.render("+", True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=(int(hx), int(hy))))

            mx, my = mouse_pos
            if math.hypot(mx - hx, my - hy) <= drone_radius:
                hovered_surplus = (mx, my, hidden_list)

        if hovered_surplus:
            mx, my, hidden_drones = hovered_surplus
            text_str = f"Drones: {', '.join(map(str, hidden_drones))}"
            text_surf = self.font.render(text_str, True, (255, 255, 255))

            box_rect = text_surf.get_rect(topleft=(mx + 15, my - 10))
            box_rect.inflate_ip(10, 10)

            pygame.draw.rect(self.screen, (40, 40, 45), box_rect)
            pygame.draw.rect(self.screen, (255, 215, 0), box_rect, 1)
            self.screen.blit(text_surf, (box_rect.x + 5, box_rect.y + 5))

    def run(self) -> None:
        self.simu.resolve_all_paths()
        self.current_turn = 0

        clock = pygame.time.Clock()
        running = True

        last_step_time = pygame.time.get_ticks()
        step_delay = 1000

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            current_time = pygame.time.get_ticks()
            elapsed = current_time - last_step_time

            if elapsed >= step_delay:
                self.current_turn += 1
                last_step_time = current_time
                elapsed = 0

            # Calcul du pourcentage de déplacement en temps réel (0.0 à 1.0)
            progress = elapsed / step_delay

            # On passe la progression à la méthode de dessin
            self.draw_map(progress)
            pygame.display.flip()

            clock.tick(60)

        pygame.quit()
        sys.exit()
