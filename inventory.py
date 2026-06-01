import pygame
from settings import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT
from items import ITEM_TYPES


class Inventory:
    def __init__(self, capacity=20):
        self.capacity = capacity
        self.items = []
        self.equipment = {"weapon": None, "armor": None, "accessory": None}
        self.is_open = False
        self.selected_index = 0
        self.buffs = []
        self.pickup_notifications = []

    def add_item(self, item):
        if item.category == "equipment":
            self._equip(item)
            self.pickup_notifications.append((item.name, 120))
            return True
        if len(self.items) >= self.capacity:
            return False
        self.items.append({"type": item.item_type, "data": item.data})
        self.pickup_notifications.append((item.name, 120))
        return True

    def _equip(self, item):
        slot = item.data["slot"]
        old = self.equipment[slot]
        if old is not None:
            self.items.append(old)
        self.equipment[slot] = {"type": item.item_type, "data": item.data}

    def use_item(self, index, player):
        if index < 0 or index >= len(self.items):
            return False
        item = self.items[index]
        data = item["data"]
        effect = data["effect"]

        if effect == "heal":
            if player.hp >= player.max_hp:
                return False
            player.heal(data["value"])
        elif effect == "buff_attack":
            self.buffs.append({"stat": "attack", "value": data["value"],
                               "remaining": data["duration"],
                               "_max_remaining": data["duration"]})
        elif effect == "buff_defense":
            self.buffs.append({"stat": "defense", "value": data["value"],
                               "remaining": data["duration"],
                               "_max_remaining": data["duration"]})
        elif effect == "buff_speed":
            self.buffs.append({"stat": "speed", "value": data["value"],
                               "remaining": data["duration"],
                               "_max_remaining": data["duration"]})
            player.speed += data["value"]
        elif data["category"] == "equipment":
            slot = data["slot"]
            old = self.equipment[slot]
            self.equipment[slot] = item
            self.items.pop(index)
            if old is not None:
                self.items.insert(index, old)
            return True
        else:
            return False

        self.items.pop(index)
        if self.selected_index >= len(self.items) and self.selected_index > 0:
            self.selected_index -= 1
        return True

    def update_buffs(self, player):
        expired = []
        for buff in self.buffs:
            buff["remaining"] -= 1
            if buff["remaining"] <= 0:
                expired.append(buff)
        for buff in expired:
            if buff["stat"] == "speed":
                player.speed -= buff["value"]
            self.buffs.remove(buff)

        new_notifs = []
        for name, timer in self.pickup_notifications:
            if timer > 0:
                new_notifs.append((name, timer - 1))
        self.pickup_notifications = new_notifs

    def get_equipment_bonuses(self):
        bonuses = {"attack": 0, "defense": 0, "speed": 0}
        for slot, item in self.equipment.items():
            if item is None:
                continue
            effect = item["data"]["effect"]
            value = item["data"]["value"]
            if effect == "equip_attack":
                bonuses["attack"] += value
            elif effect == "equip_defense":
                bonuses["defense"] += value
            elif effect == "equip_speed":
                bonuses["speed"] += value
        return bonuses

    def handle_input(self, event):
        if not self.is_open:
            return False
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_index = max(0, self.selected_index - 1)
            return True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_index = min(len(self.items) - 1, self.selected_index)
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
            return True
        elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
            return True
        elif event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
            self.is_open = False
            return True
        return False

    def draw(self, screen, font_medium, font_small, player):
        if not self.is_open:
            self._draw_notifications(screen, font_small)
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS["black"])
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))

        panel_w, panel_h = 500, 500
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2

        pygame.draw.rect(screen, (30, 30, 40), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, COLORS["white"], (panel_x, panel_y, panel_w, panel_h), 2)

        title = font_medium.render("背包 (TAB关闭 | Enter使用/装备)", True, COLORS["yellow"])
        screen.blit(title, (panel_x + 10, panel_y + 10))

        eq_y = panel_y + 45
        eq_title = font_small.render("-- 装备栏 --", True, COLORS["light_blue"])
        screen.blit(eq_title, (panel_x + 10, eq_y))
        eq_y += 22
        slot_names = {"weapon": "武器", "armor": "护甲", "accessory": "饰品"}
        for slot, label in slot_names.items():
            item = self.equipment[slot]
            if item:
                text = f"[{label}] {item['data']['name']} - {item['data']['description']}"
                color = item["data"]["color"]
            else:
                text = f"[{label}] 空"
                color = COLORS["gray"]
            line = font_small.render(text, True, color)
            screen.blit(line, (panel_x + 20, eq_y))
            eq_y += 22

        inv_y = eq_y + 15
        inv_title = font_small.render(
            f"-- 物品 ({len(self.items)}/{self.capacity}) --", True, COLORS["light_blue"]
        )
        screen.blit(inv_title, (panel_x + 10, inv_y))
        inv_y += 22

        if not self.items:
            empty = font_small.render("背包为空", True, COLORS["gray"])
            screen.blit(empty, (panel_x + 20, inv_y))
        else:
            max_visible = 12
            start = max(0, self.selected_index - max_visible + 1)
            for i in range(start, min(len(self.items), start + max_visible)):
                item = self.items[i]
                prefix = "> " if i == self.selected_index else "  "
                text = f"{prefix}{item['data']['name']} - {item['data']['description']}"
                color = item["data"]["color"] if i == self.selected_index else COLORS["white"]
                line = font_small.render(text, True, color)
                screen.blit(line, (panel_x + 20, inv_y))
                inv_y += 22

        if self.buffs:
            buff_y = panel_y + panel_h - 60
            buff_title = font_small.render("-- 当前增益 --", True, COLORS["green"])
            screen.blit(buff_title, (panel_x + 10, buff_y))
            buff_y += 22
            for buff in self.buffs[:3]:
                secs = buff["remaining"] // 60
                text = f"{buff['stat']}+{buff['value']} ({secs}s)"
                line = font_small.render(text, True, COLORS["green"])
                screen.blit(line, (panel_x + 20, buff_y))
                buff_y += 20

    def _draw_notifications(self, screen, font_small):
        y = SCREEN_HEIGHT // 2 - 50
        for name, timer in self.pickup_notifications[-5:]:
            alpha = min(255, timer * 4)
            text = font_small.render(f"拾取: {name}", True, COLORS["green"])
            text.set_alpha(alpha)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y -= 25
