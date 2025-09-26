# portfolio_game.py
# Interactive portfolio built with pygame (responsive + modern).
# Contains CV data from uploaded PDF. :contentReference[oaicite:1]{index=1}

import pygame
import math
import random
import sys
from typing import List, Tuple

pygame.init()
pygame.display.set_caption("Ibrahim Ibrahim — Interactive Portfolio")

# ------------ Settings & Responsive sizing -------------
MIN_W, MIN_H = 900, 600
WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()
FPS = 60

# Colors (modern/dark)
BG = (12, 14, 23)
CARD = (24, 26, 36)
CARD_H = (42, 85, 135)  # highlight
ACCENT = (50, 180, 255)
TEXT = (235, 238, 245)
MUTED = (160, 165, 175)
ROAD = (36, 40, 48)
LINE = (200, 200, 100)

# Fonts (responsive scale)
def get_fonts(scale=1.0):
    return {
        "title": pygame.font.SysFont("Arial", int(44 * scale), bold=True),
        "h1": pygame.font.SysFont("Arial", int(28 * scale), bold=True),
        "h2": pygame.font.SysFont("Arial", int(20 * scale), bold=False),
        "body": pygame.font.SysFont("Arial", int(16 * scale)),
        "tiny": pygame.font.SysFont("Arial", int(12 * scale)),
    }

# ---------- CV content (extracted from uploaded PDF) ----------
# Source: uploaded CV file. :contentReference[oaicite:2]{index=2}
CV = {
    "name": "Ibrahim Ibrahim",
    "title": "Software Developer | Computer Science Graduate",
    "contact": {
        "email": "ibrahimibrahimwork1@gmail.com",
        "phone": "70240848",
        "location": "Tripoli, Lebanon",
        "dob": "08/10/2001"
    },
    "education": [
        "Bachelor of Science in Computer Science",
        "Lebanese International University (LIU)",
        "2021 – 2024 | LIU - Daher al eein"
    ],
    "skills": [
        "Web Development: HTML5, CSS3, JavaScript (ES6+), Angular, PHP, RESTful APIs",
        "Mobile Development: Flutter",
        "Programming: Python, JavaScript, PHP",
        "Databases: MySQL, Microsoft Access",
        "Tools: Git, GitHub, VS Code",
        "Other: Responsive Web Design, Debugging, Performance Optimization"
    ],
    "languages": [
        "Arabic: Native",
        "English: Proficient",
        "French: Basic"
    ],
    "profile": [
        "Computer Science graduate and Software Developer with hands-on",
        "experience in web and mobile development. Skilled in HTML, CSS,",
        "JavaScript, Angular, PHP, Python, and Flutter, with strong database",
        "knowledge (MySQL, Microsoft Access). Experienced in building",
        "full-stack applications such as car dealership and mobile shop",
        "management systems, integrating REST APIs and delivering",
        "responsive, user-friendly solutions."
    ],
    "experience": [
        "Telepaty — Software Developer (2024 – 2025) | Al Mina, Tripoli",
        "- Developed and maintained web applications using Angular, HTML, CSS, JavaScript.",
        "- Built and integrated RESTful APIs with PHP for scalable backends.",
        "- Collaborated with designers and backend developers to implement features.",
        "- Optimized performance, ensured cross-browser compatibility.",
        "- Participated in code reviews, testing, and deployment.",
        "- Contributed to projects focused on car rental, sales, and maintenance."
    ],
    "projects": [
        "Car Dealer Management System (Graduation Project — 2023)",
        "- Full-stack web app for car rental, maintenance, sales. Angular frontend, PHP backend, REST APIs.",
        "- Implemented inventory, booking, maintenance tracking, and customer DB.",
        "",
        "Mobile Shop & Accessories Management System (Ibrahim Mobile Services)",
        "- Web-based system for store operations: sales, inventory, customer management.",
        "- Angular frontend, PHP backend with API integration.",
        "- Live demo: https://aliibrahimservice.great-site.net"
    ],
    "certificates": [
        "Digital Skills Training — Web Development (Front-End)",
        "American University of Beirut (AUB), World Food Programme — Jan 2021 – Mar 2021",
        "Completed 90 hours of Front-End training + 60 hours English training.",
        "",
        "Digital Skills Training — Python Programming",
        "American University of Beirut (AUB), World Food Programme — Oct 2020 – Dec 2020",
        "Completed 90 hours of Python training + 60 hours English training."
    ]
}

# ---------- Helper UI components ----------
def draw_text(surface, text, font, color, pos, center=False):
    lines = text.split("\n")
    x, y = pos
    for i, ln in enumerate(lines):
        surf = font.render(ln, True, color)
        r = surf.get_rect()
        if center:
            r.center = (x, y + i * (r.height + 2))
            surface.blit(surf, r)
        else:
            surface.blit(surf, (x, y + i * (r.height + 2)))

class Card:
    def __init__(self, id_, title, short, x, y, w, h, color=CARD):
        self.id = id_
        self.title = title
        self.short = short
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hover = False
        self.open = False
        self.float_offset = random.uniform(0, math.pi*2)  # gentle floating

    def update(self, dt, mouse_pos):
        # Hover detection
        self.hover = self.rect.collidepoint(mouse_pos)
        # gentle floating animation
        offset = math.sin(pygame.time.get_ticks() / 600 + self.float_offset) * 6
        self.current_rect = self.rect.copy()
        self.current_rect.y += offset

    def draw(self, surf, fonts):
        r = self.current_rect
        border_col = ACCENT if self.hover or self.open else (40, 40, 50)
        pygame.draw.rect(surf, self.color, r, border_radius=14)
        pygame.draw.rect(surf, border_col, r, 3, border_radius=14)
        # Title
        draw_text(surf, self.title, fonts["h1"], TEXT, (r.x + 18, r.y + 12))
        # short text
        draw_text(surf, self.short, fonts["body"], MUTED, (r.x + 18, r.y + 48))

# ---------- Main Application ----------
class PortfolioApp:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.scale = self.width / 1200
        self.fonts = get_fonts(self.scale)
        self.cards: List[Card] = []
        self.init_cards()
        # Car/player
        self.car_x = self.width * 0.5
        self.car_y = self.height * 0.85
        self.car_angle = 0
        self.car_speed = 0
        self.max_speed = 6 * self.scale
        # state
        self.active_card = None
        self.particles = []
        self.bg_offset = 0

    def init_cards(self):
        w = int(300 * self.scale)
        h = int(120 * self.scale)
        spacing_x = int(60 * self.scale)
        top = int(120 * self.scale)
        # arrange cards in 2 rows
        titles = [
            ("Profile", "about me"),
            ("Education", "academic record"),
            ("Skills", "competencies"),
            ("Experience", "work history"),
            ("Projects", "sample works"),
            ("Certificates", "achievements"),
            ("Contact", "get in touch"),
        ]
        x0 = int((self.width - (w * 3 + spacing_x * 2)) / 2)
        for idx, (t, s) in enumerate(titles):
            col = idx % 3
            row = idx // 3
            x = x0 + col * (w + spacing_x)
            y = top + row * (h + int(30 * self.scale))
            self.cards.append(Card(idx, t, s, x, y, w, h))

    def resize(self, w, h):
        self.width, self.height = max(w, MIN_W), max(h, MIN_H)
        self.scale = self.width / 1200
        self.fonts = get_fonts(self.scale)
        # recompute card positions and sizes
        self.cards.clear()
        self.init_cards()
        # reposition car
        self.car_x = self.width * 0.5
        self.car_y = self.height * 0.85

    def add_particles(self, x, y, color, amount=8):
        for _ in range(amount):
            self.particles.append({
                "x": x + random.uniform(-8, 8),
                "y": y + random.uniform(-8, 8),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(-2.5, -0.3),
                "life": random.uniform(0.5, 1.2),
                "size": random.uniform(2, 6),
                "color": color
            })

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        for c in self.cards:
            c.update(dt, mouse)
        # Car controls (keyboard)
        keys = pygame.key.get_pressed()
        accel = 0.12 * self.scale
        if keys[pygame.K_UP]:
            self.car_speed = min(self.car_speed + accel, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.car_speed = max(self.car_speed - accel, -self.max_speed / 2)
        else:
            # friction
            self.car_speed *= 0.95

        if keys[pygame.K_LEFT]:
            self.car_angle += 1.8 * (self.scale)
        if keys[pygame.K_RIGHT]:
            self.car_angle -= 1.8 * (self.scale)

        # move car
        rad = math.radians(self.car_angle)
        self.car_x += math.sin(rad) * self.car_speed
        self.car_y -= math.cos(rad) * self.car_speed
        # bounds
        self.car_x = max(30 * self.scale, min(self.width - 30 * self.scale, self.car_x))
        self.car_y = max(30 * self.scale, min(self.height - 30 * self.scale, self.car_y))

        # particles from exhaust
        if abs(self.car_speed) > 0.2:
            self.add_particles(self.car_x - math.sin(rad) * 28 * self.scale,
                               self.car_y + math.cos(rad) * 28 * self.scale,
                               (180, 180, 180), amount=2)

        # update particles
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.05
            p["life"] -= dt * 0.003
            p["size"] *= 0.995
            if p["life"] <= 0 or p["size"] < 0.5:
                self.particles.remove(p)

        # check proximity to cards -> open panel if close
        self.active_card = None
        for c in self.cards:
            cx, cy = c.current_rect.center
            dist = math.hypot(self.car_x - cx, self.car_y - cy)
            if dist < 100 * self.scale:
                c.open = True
                self.active_card = c
            else:
                c.open = False

        # animate background offset
        self.bg_offset = (self.bg_offset + self.car_speed * 0.15) % self.height

    def handle_click(self, pos):
        # click cards to toggle open
        for c in self.cards:
            if c.current_rect.collidepoint(pos):
                # toggle open
                c.open = not c.open
                if c.open:
                    self.active_card = c
                else:
                    self.active_card = None

    def draw_background(self, surf):
        # gradient-ish background
        surf.fill(BG)
        # subtle moving 'road' stripes to give depth
        for i in range(-2, 6):
            y = (i * 180 + self.bg_offset) % (self.height + 200) - 200
            pygame.draw.rect(surf, ROAD, (0, y, self.width, 120))
            # center stripe
            cx = self.width // 2
            for s in range(-8, 9):
                sx = cx + s * 120
                pygame.draw.rect(surf, LINE, (sx - 6, y + 48, 12, 24), border_radius=6)

    def draw(self):
        surf = self.screen
        # background
        self.draw_background(surf)
        # header
        draw_text(surf, CV["name"], self.fonts["title"], TEXT, (30 * self.scale, 18 * self.scale))
        draw_text(surf, CV["title"], self.fonts["h2"], MUTED, (30 * self.scale, 62 * self.scale))
        # draw cards
        for c in self.cards:
            c.draw(surf, self.fonts)
        # draw particles under car for depth
        for p in self.particles:
            pygame.draw.circle(surf, p["color"], (int(p["x"]), int(p["y"])), int(max(1, p["size"])))

        # draw car
        self.draw_car(surf)
        # draw active panel
        if self.active_card:
            self.draw_panel_for(self.active_card)

        # footer / controls
        ctrl_text = "ARROWS to drive  •  Click card to open  •  ESC to quit"
        t_surf = self.fonts["tiny"].render(ctrl_text, True, MUTED)
        surf.blit(t_surf, (20 * self.scale, self.height - t_surf.get_height() - 12 * self.scale))

    def draw_car(self, surf):
        # simple stylized car
        w = int(56 * self.scale)
        h = int(96 * self.scale)
        car_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, ACCENT, (0, 0, w, h), border_radius=int(12 * self.scale))
        pygame.draw.rect(car_surf, (20, 22, 28), (6 * self.scale, 10 * self.scale, w - 12 * self.scale, 26 * self.scale), border_radius=int(8 * self.scale))
        pygame.draw.ellipse(car_surf, (18, 20, 24), (6 * self.scale, h - 22 * self.scale, 18 * self.scale, 18 * self.scale))
        pygame.draw.ellipse(car_surf, (18, 20, 24), (w - 24 * self.scale, h - 22 * self.scale, 18 * self.scale, 18 * self.scale))
        # rotate
        rot = pygame.transform.rotate(car_surf, self.car_angle)
        r = rot.get_rect(center=(self.car_x, self.car_y))
        surf.blit(rot, r.topleft)

    def draw_panel_for(self, card: Card):
        # big panel centered showing full content
        pad = int(18 * self.scale)
        pw = int(self.width * 0.62)
        ph = int(self.height * 0.58)
        px = int((self.width - pw) / 2)
        py = int((self.height - ph) / 2)
        panel_rect = pygame.Rect(px, py, pw, ph)
        # panel background
        pygame.draw.rect(self.screen, (20, 22, 28), panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, ACCENT, panel_rect, 3, border_radius=14)
        # title
        draw_text(self.screen, card.title, self.fonts["h1"], ACCENT, (px + pad, py + pad))
        # draw content depending on id/title
        content_x = px + pad
        content_y = py + pad + int(54 * self.scale)
        line_h = int(24 * self.scale)
        # map card.title to content
        if card.title == "Profile":
            for i, ln in enumerate(CV["profile"]):
                draw_text(self.screen, ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Education":
            for i, ln in enumerate(CV["education"]):
                draw_text(self.screen, ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Skills":
            for i, ln in enumerate(CV["skills"]):
                draw_text(self.screen, "• " + ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Experience":
            for i, ln in enumerate(CV["experience"]):
                draw_text(self.screen, ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Projects":
            for i, ln in enumerate(CV["projects"]):
                draw_text(self.screen, ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Certificates":
            for i, ln in enumerate(CV["certificates"]):
                draw_text(self.screen, ln, self.fonts["body"], TEXT, (content_x, content_y + i * line_h))
        elif card.title == "Contact":
            # contact panel with clickable-looking fields
            cx = content_x
            draw_text(self.screen, "Email: " + CV["contact"]["email"], self.fonts["body"], TEXT, (cx, content_y))
            draw_text(self.screen, "Phone: " + CV["contact"]["phone"], self.fonts["body"], TEXT, (cx, content_y + line_h))
            draw_text(self.screen, "Location: " + CV["contact"]["location"], self.fonts["body"], TEXT, (cx, content_y + 2 * line_h))
            draw_text(self.screen, "DOB: " + CV["contact"]["dob"], self.fonts["body"], TEXT, (cx, content_y + 3 * line_h))
            draw_text(self.screen, "Languages: " + ", ".join(CV["languages"]), self.fonts["body"], TEXT, (cx, content_y + 4 * line_h))
        # small hint
        hint = "(Press SPACE to close panel)"
        hs = self.fonts["tiny"].render(hint, True, MUTED)
        self.screen.blit(hs, (px + pw - hs.get_width() - pad, py + ph - hs.get_height() - pad))

    def close_active(self):
        for c in self.cards:
            c.open = False
        self.active_card = None

# ---------- Run the app ----------
app = PortfolioApp(screen)

def main_loop():
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                app.resize(event.w, event.h)
                pygame.display.set_mode((app.width, app.height), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                app.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    app.close_active()

        app.update(dt)
        app.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    
    main_loop()
