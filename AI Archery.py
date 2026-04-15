import pygame
import math
import random

# --- Professional Configuration ---
WIDTH, HEIGHT = 1000, 700
FPS = 60
GRAVITY = 0.20

# Professional High-Contrast Palette
BG_SKY = (240, 240, 240)      # Clean Off-White Sky
FLOOR_P1 = (192, 57, 43)      # Strong Crimson Red (P1 Area)
FLOOR_P2 = (41, 128, 185)     # Strong Steel Blue (P2 Area)

UI_PANEL = (33, 47, 61)       # Dark Charcoal for HUD
P1_ACCENT = (231, 76, 60)     # Bright Red
P2_ACCENT = (52, 152, 219)    # Bright Sky Blue
WHITE = (255, 255, 255)
GOLD = (241, 196, 15)        # Contrast Gold for Bullseye
ARROW_COLOR = (20, 20, 20)    # Pitch Black Projectile

class Arrow:
    def __init__(self, x, y, angle, power, wind):
        self.pos = [x, y]
        self.vel = [
            power * math.cos(math.radians(angle)),
            -power * math.sin(math.radians(angle))
        ]
        self.wind = wind
        self.active = True

    def update(self):
        self.vel[1] += GRAVITY
        self.vel[0] += self.wind * 0.02
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[1] > HEIGHT or self.pos[0] > WIDTH or self.pos[0] < 0:
            self.active = False

class ArcheryGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Archery Battle with AI")
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Verdana", 28, bold=True)
        self.font_ui = pygame.font.SysFont("Verdana", 16, bold=True)

        try:
            self.bow_img_src = pygame.image.load("image_f958e5.jpg").convert_alpha()
            self.bow_img_src = pygame.transform.scale(self.bow_img_src, (150, 150))
        except:
            # Reverted to your original blank surface fallback
            self.bow_img_src = pygame.Surface((150, 150), pygame.SRCALPHA)

        self.p1_score, self.p2_score = 0, 0
        self.turn = 1 
        self.arrow = None
        self.wind = round(random.uniform(-4.0, 4.0), 1)
        
        self.target_pos = [WIDTH - 150, HEIGHT // 2]
        self.target_speed = 3
        self.target_dir = 1 
        
        self.reset_controls()
        self.running = True

    def reset_controls(self):
        self.power = 15
        self.angle = 45

    def update_target(self):
        self.target_pos[1] += self.target_speed * self.target_dir
        if self.target_pos[1] < 100 or self.target_pos[1] > HEIGHT - 200:
            self.target_dir *= -1

    # --- AI HILL CLIMBING LOGIC ---
    def simulate_heuristic(self, sim_angle, sim_power):
        temp_x, temp_y = 140, HEIGHT - 220
        vx = sim_power * math.cos(math.radians(sim_angle))
        vy = -sim_power * math.sin(math.radians(sim_angle))
        
        min_dist = 9999
        for _ in range(200):
            temp_x += vx
            temp_y += vy
            vy += GRAVITY
            vx += self.wind * 0.02
            curr_dist = math.hypot(temp_x - self.target_pos[0], temp_y - self.target_pos[1])
            min_dist = min(min_dist, curr_dist)
            if temp_y > HEIGHT or temp_x > WIDTH or temp_x < 0:
                break
        return min_dist

    def bot_move_hill_climbing(self):
        curr_angle = random.randint(20, 70)
        curr_pwr = random.randint(15, 25)
        curr_score = self.simulate_heuristic(curr_angle, curr_pwr)

        for _ in range(40):
            adj_angle = curr_angle + random.uniform(-3, 3)
            adj_pwr = curr_pwr + random.uniform(-1, 1)
            adj_angle = max(5, min(85, adj_angle))
            adj_pwr = max(5, min(30, adj_pwr))
            
            new_score = self.simulate_heuristic(adj_angle, adj_pwr)
            if new_score < curr_score:
                curr_score = new_score
                curr_angle, curr_pwr = adj_angle, adj_pwr
        
        self.angle = curr_angle
        self.power = curr_pwr
        self.arrow = Arrow(140, HEIGHT - 220, self.angle, self.power, self.wind)

    def draw_button(self, rect, text, color, hover_color):
        mouse = pygame.mouse.get_pos()
        c = hover_color if rect.collidepoint(mouse) else color
        pygame.draw.rect(self.screen, c, rect, border_radius=8)
        txt = self.font_ui.render(text, True, WHITE)
        self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

    def draw_trajectory(self, start_x, start_y):
        temp_x, temp_y = start_x, start_y
        vx = self.power * math.cos(math.radians(self.angle))
        vy = -self.power * math.sin(math.radians(self.angle))
        dot_color = (150, 150, 150)
        for i in range(25):
            temp_x += vx
            temp_y += vy
            vy += GRAVITY
            vx += self.wind * 0.02
            if i % 2 == 0:
                pygame.draw.circle(self.screen, dot_color, (int(temp_x), int(temp_y)), 2)

    def draw_power_gauge(self):
        gauge_bg_rect = pygame.Rect(320, HEIGHT - 100, 200, 30)
        pygame.draw.rect(self.screen, UI_PANEL, gauge_bg_rect, border_radius=5)
        fill_width = (self.power / 30) * 194
        fill_rect = pygame.Rect(323, HEIGHT - 97, fill_width, 24)
        gauge_color = (46, 204, 113) if self.power < 22 else (243, 156, 18)
        pygame.draw.rect(self.screen, gauge_color, fill_rect, border_radius=3)
        label = self.font_ui.render(f"POWER: {int(self.power)}", True, WHITE)
        self.screen.blit(label, (320, HEIGHT - 130))

    def draw_scene(self):
        self.screen.fill(BG_SKY)
        floor_color = FLOOR_P1 if self.turn == 1 else FLOOR_P2
        pygame.draw.rect(self.screen, floor_color, (0, HEIGHT - 150, WIDTH, 150))
        pivot = pygame.Vector2(140, HEIGHT - 220)
        
        if not self.arrow:
            self.draw_trajectory(pivot.x, pivot.y)
            self.draw_power_gauge()

        rotated_bow = pygame.transform.rotate(self.bow_img_src, self.angle - 45)
        rect = rotated_bow.get_rect(center=pivot)
        self.screen.blit(rotated_bow, rect)

        target_colors = [(50, UI_PANEL), (35, WHITE), (20, P1_ACCENT), (10, GOLD)]
        for r, c in target_colors:
            pygame.draw.circle(self.screen, c, (int(self.target_pos[0]), int(self.target_pos[1])), r)
        
        pygame.draw.rect(self.screen, UI_PANEL, (WIDTH//2 - 200, 15, 400, 50), border_radius=12)
        p1_color = P1_ACCENT if self.turn == 1 else (100, 100, 100)
        p2_color = P2_ACCENT if self.turn == 2 else (100, 100, 100)
        self.screen.blit(self.font_main.render(f"P1: {self.p1_score}", True, p1_color), (WIDTH//2 - 170, 22))
        self.screen.blit(self.font_main.render(f"BOT: {self.p2_score}", True, p2_color), (WIDTH//2 + 30, 22))

        self.btn_ang_up = pygame.Rect(130, HEIGHT-120, 80, 35)
        self.btn_ang_dn = pygame.Rect(130, HEIGHT-75, 80, 35)
        self.btn_pwr_up = pygame.Rect(220, HEIGHT-120, 80, 35)
        self.btn_pwr_dn = pygame.Rect(220, HEIGHT-75, 80, 35)
        self.btn_shoot = pygame.Rect(WIDTH-150, HEIGHT-100, 120, 60)
        
        shoot_color = P1_ACCENT if self.turn == 1 else P2_ACCENT
        shoot_hover = (255, 100, 100) if self.turn == 1 else (100, 200, 255)
        
        self.draw_button(self.btn_ang_up, "+ ANG", UI_PANEL, (50, 70, 90))
        self.draw_button(self.btn_ang_dn, "- ANG", UI_PANEL, (50, 70, 90))
        self.draw_button(self.btn_pwr_up, "+ PWR", UI_PANEL, (50, 70, 90))
        self.draw_button(self.btn_pwr_dn, "- PWR", UI_PANEL, (50, 70, 90))
        self.draw_button(self.btn_shoot, "SHOOT", shoot_color, shoot_hover)

        wind_txt = self.font_ui.render(f"WIND: {self.wind}", True, UI_PANEL)
        self.screen.blit(wind_txt, (WIDTH - 150, 85))

        if self.arrow:
            pos_int = (int(self.arrow.pos[0]), int(self.arrow.pos[1]))
            pygame.draw.circle(self.screen, ARROW_COLOR, pos_int, 10)
            pygame.draw.circle(self.screen, (100, 100, 100), (pos_int[0]-3, pos_int[1]-3), 3)

    def run(self):
        while self.running:
            self.update_target()
            self.draw_scene()
            
            if self.turn == 2 and not self.arrow:
                pygame.time.delay(500)
                self.bot_move_hill_climbing()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and not self.arrow and self.turn == 1:
                    if self.btn_shoot.collidepoint(event.pos):
                        self.arrow = Arrow(140, HEIGHT - 220, self.angle, self.power, self.wind)
                    if self.btn_ang_up.collidepoint(event.pos): self.angle = min(85, self.angle + 5)
                    if self.btn_ang_dn.collidepoint(event.pos): self.angle = max(5, self.angle - 5)
                    if self.btn_pwr_up.collidepoint(event.pos): self.power = min(30, self.power + 2)
                    if self.btn_pwr_dn.collidepoint(event.pos): self.power = max(5, self.power - 2)

            if self.arrow:
                self.arrow.update()
                dist = math.hypot(self.arrow.pos[0]-self.target_pos[0], self.arrow.pos[1]-self.target_pos[1])
                if dist < 45 or not (0 < self.arrow.pos[0] < WIDTH) or self.arrow.pos[1] > HEIGHT:
                    if dist < 45:
                        if self.turn == 1: self.p1_score += 10
                        else: self.p2_score += 10
                    self.arrow = None
                    self.turn = 2 if self.turn == 1 else 1
                    self.wind = round(random.uniform(-4.0, 4.0), 1)
                    self.reset_controls()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    ArcheryGame().run()
