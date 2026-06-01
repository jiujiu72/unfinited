import pygame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class UI:
    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self._init_fonts()

    def _init_fonts(self):
        font_candidates = [
            "microsoftyahei", "simhei", "simsun",
            "dengxian", "fangsong",
        ]
        self.font_large = None
        for name in font_candidates:
            try:
                font = pygame.font.SysFont(name, 48)
                if font.get_height() > 0:
                    self.font_large = font
                    self.font_medium = pygame.font.SysFont(name, 28)
                    self.font_small = pygame.font.SysFont(name, 20)
                    break
            except Exception:
                continue

        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 20)

    def draw_hud(self, screen, player, inventory=None):
        bar_width = 200
        bar_height = 20
        x, y = 20, 20

        hp_ratio = max(0, player.hp / player.max_hp)
        pygame.draw.rect(screen, COLORS["dark_gray"], (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, COLORS["red"], (x, y, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(screen, COLORS["white"], (x, y, bar_width, bar_height), 1)
        hp_text = self.font_small.render(
            f"HP: {player.hp}/{player.max_hp}", True, COLORS["white"]
        )
        screen.blit(hp_text, (x + 5, y))

        exp_ratio = player.exp / player.exp_to_next if player.exp_to_next > 0 else 0
        ey = y + 30
        pygame.draw.rect(screen, COLORS["dark_gray"], (x, ey, bar_width, bar_height))
        pygame.draw.rect(screen, COLORS["yellow"],
                         (x, ey, int(bar_width * exp_ratio), bar_height))
        pygame.draw.rect(screen, COLORS["white"], (x, ey, bar_width, bar_height), 1)
        exp_text = self.font_small.render(
            f"EXP: {player.exp}/{player.exp_to_next}", True, COLORS["white"]
        )
        screen.blit(exp_text, (x + 5, ey))

        info_y = ey + 30
        level_text = self.font_small.render(
            f"Lv.{player.level}  ATK:{player.attack}  DEF:{player.defense}",
            True, COLORS["white"]
        )
        screen.blit(level_text, (x, info_y))

        score_y = info_y + 25
        score_text = self.font_small.render(
            f"分数: {player.score}  击杀: {player.kills}",
            True, COLORS["yellow"]
        )
        screen.blit(score_text, (x, score_y))

        tab_text = self.font_small.render(
            "TAB: 背包", True, COLORS["gray"]
        )
        screen.blit(tab_text, (x, score_y + 25))

        if inventory and inventory.buffs:
            self._draw_buff_bar(screen, inventory)

        pos_text = self.font_small.render(
            f"坐标: ({int(player.world_x)}, {int(player.world_y)})",
            True, COLORS["gray"]
        )
        screen.blit(pos_text, (SCREEN_WIDTH - 200, 20))

    def _draw_buff_bar(self, screen, inventory):
        buffs = inventory.buffs
        if not buffs:
            return

        buff_labels = {"attack": "攻击", "defense": "防御", "speed": "速度"}
        buff_colors = {
            "attack": (255, 160, 0),
            "defense": (100, 200, 255),
            "speed": (0, 255, 180),
        }

        panel_w = 180
        item_h = 36
        padding = 6
        panel_h = len(buffs) * item_h + padding * 2 + 20
        px = SCREEN_WIDTH - panel_w - 15
        py = 50

        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((10, 10, 20, 200))
        screen.blit(bg, (px, py))
        pygame.draw.rect(screen, COLORS["yellow"], (px, py, panel_w, panel_h), 1)

        title = self.font_small.render("增益效果", True, COLORS["yellow"])
        screen.blit(title, (px + (panel_w - title.get_width()) // 2, py + 2))

        for i, buff in enumerate(buffs):
            by = py + 20 + padding + i * item_h
            stat = buff["stat"]
            secs = buff["remaining"] // 60
            frac = buff["remaining"] % 60
            color = buff_colors.get(stat, COLORS["green"])
            label = buff_labels.get(stat, stat)

            text = f"{label}+{buff['value']}  {secs}.{frac * 100 // 60:02d}s"
            txt_surf = self.font_small.render(text, True, color)
            screen.blit(txt_surf, (px + 8, by))

            bar_y = by + 20
            bar_w = panel_w - 16
            duration = buff.get("_max_remaining", buff["remaining"])
            ratio = buff["remaining"] / duration if duration > 0 else 0
            pygame.draw.rect(screen, (40, 40, 50), (px + 8, bar_y, bar_w, 6))
            pygame.draw.rect(screen, color, (px + 8, bar_y, int(bar_w * ratio), 6))

    def draw_menu(self, screen, high_score=0):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS["black"])
        overlay.set_alpha(200)
        screen.blit(overlay, (0, 0))

        title = self.font_large.render("程序员无限肉鸽游戏", True, COLORS["yellow"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title, title_rect)

        start_text = self.font_medium.render(
            "按 Enter 开始游戏", True, COLORS["white"]
        )
        start_rect = start_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        screen.blit(start_text, start_rect)

        if high_score > 0:
            hs_text = self.font_medium.render(
                f"最高分: {high_score}", True, COLORS["orange"]
            )
            hs_rect = hs_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)
            )
            screen.blit(hs_text, hs_rect)

        help_text = self.font_small.render(
            "WASD移动 | 自动射击 | TAB背包 | 击杀升级 | ESC暂停",
            True, COLORS["gray"]
        )
        help_rect = help_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        )
        screen.blit(help_text, help_rect)

    def draw_pause(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS["black"])
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render("游戏暂停", True, COLORS["white"])
        pause_rect = pause_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )
        screen.blit(pause_text, pause_rect)

        resume_text = self.font_medium.render(
            "按 ESC 继续 | 按 Q 返回主菜单", True, COLORS["gray"]
        )
        resume_rect = resume_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        screen.blit(resume_text, resume_rect)

    def draw_gameover(self, screen, player, high_score=0):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS["black"])
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        over_text = self.font_large.render("游戏结束", True, COLORS["red"])
        over_rect = over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        )
        screen.blit(over_text, over_rect)

        score_text = self.font_medium.render(
            f"分数: {player.score}  等级: {player.level}  击杀: {player.kills}",
            True, COLORS["white"]
        )
        score_rect = score_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
        )
        screen.blit(score_text, score_rect)

        hs_text = self.font_medium.render(
            f"最高分: {high_score}", True, COLORS["orange"]
        )
        hs_rect = hs_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)
        )
        screen.blit(hs_text, hs_rect)

        restart_text = self.font_medium.render(
            "按 R 重新开始 | 按 Q 返回主菜单", True, COLORS["gray"]
        )
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        )
        screen.blit(restart_text, restart_rect)
