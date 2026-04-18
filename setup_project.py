"""
JCZ 游戏项目 - 自动化部署脚本
一键生成所有竞赛级代码文件
"""

import os
import json
from pathlib import Path

# 定义所有需要创建的文件和其内容
FILES_TO_CREATE = {
    # 核心游戏系统
    "src/game/bow_system.py": """import math
import random
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class Arrow:
    \"\"\"箭的数据结构\"\"\"
    x: float
    y: float
    vx: float
    vy: float
    damage: float
    time_alive: float = 0
    max_distance: float = 1000

class BowSystem:
    \"\"\"弓箭系统 - 处理射击、蓄力、风力等\"\"\"
    
    def __init__(self):
        self.is_charging = False
        self.charge_level = 0.0
        self.max_charge = 100.0
        self.charge_speed = 80.0
        
        self.wind_force = 0.0
        self.wind_direction = 1
        self.wind_cycle = 0
        
        self.arrows_fired = 0
        self.arrows_hit = 0
        self.total_damage = 0
        
    def start_charge(self):
        self.is_charging = True
        self.charge_level = 0.0
    
    def stop_charge(self) -> Arrow:
        if not self.is_charging:
            return None
        
        self.is_charging = False
        arrow = self._create_arrow()
        self.arrows_fired += 1
        return arrow
    
    def update_charge(self, delta_time: float):
        if self.is_charging:
            self.charge_level = min(
                self.max_charge,
                self.charge_level + self.charge_speed * delta_time
            )
    
    def _create_arrow(self) -> Arrow:
        charge_ratio = self.charge_level / self.max_charge
        base_speed = 500 + (charge_ratio * 300)
        
        angle = 0
        vx = base_speed * math.cos(angle)
        vy = base_speed * math.sin(angle)
        
        wind_velocity = self.wind_force * 50
        vx += wind_velocity
        
        damage = 10 + (charge_ratio * 40)
        
        arrow = Arrow(x=960, y=540, vx=vx, vy=vy, damage=damage)
        return arrow
    
    def update_wind(self, delta_time: float):
        self.wind_cycle += delta_time
        self.wind_force = 0.5 * math.sin(self.wind_cycle * math.pi / 2)
    
    def get_wind_display(self) -> str:
        return f"风力: {abs(self.wind_force):.2f}"


class ArrowPhysics:
    GRAVITY = 500
    AIR_RESISTANCE = 0.98
    
    @staticmethod
    def update_arrow(arrow: Arrow, delta_time: float, wind_force: float) -> Arrow:
        arrow.vy += ArrowPhysics.GRAVITY * delta_time
        arrow.vx *= ArrowPhysics.AIR_RESISTANCE
        arrow.vy *= ArrowPhysics.AIR_RESISTANCE
        arrow.vx += wind_force * 20 * delta_time
        arrow.x += arrow.vx * delta_time
        arrow.y += arrow.vy * delta_time
        arrow.time_alive += delta_time
        return arrow
    
    @staticmethod
    def is_arrow_alive(arrow: Arrow, screen_width: int, screen_height: int) -> bool:
        if arrow.x < -100 or arrow.x > screen_width + 100:
            return False
        if arrow.y > screen_height + 100:
            return False
        if arrow.time_alive > 10:
            return False
        return True


class HitDetection:
    @staticmethod
    def check_hit(arrow: Arrow, target_rect) -> bool:
        target_x, target_y, target_w, target_h = target_rect
        arrow_radius = 5
        return (
            target_x - arrow_radius < arrow.x < target_x + target_w + arrow_radius
            and target_y - arrow_radius < arrow.y < target_y + target_h + arrow_radius
        )
    
    @staticmethod
    def calculate_damage(arrow: Arrow, hit_position: Tuple[float, float]) -> float:
        damage_multiplier = random.uniform(0.8, 1.5)
        return arrow.damage * damage_multiplier
""",

    "src/game/scene_manager.py": """from enum import Enum
from typing import Optional
import pygame

class SceneType(Enum):
    SPLASH = "splash"
    MENU = "menu"
    OFFICIAL = "official"
    HUNT = "hunt"
    FEAST = "feast"
    ENDING = "ending"
    STATS = "stats"

class Scene:
    def __init__(self, scene_type: SceneType, width: int, height: int):
        self.scene_type = scene_type
        self.width = width
        self.height = height
        self.is_active = False
        self.transition_progress = 0.0
        
    def on_enter(self):
        self.is_active = True
        self.transition_progress = 0.0
    
    def on_exit(self):
        self.is_active = False
    
    def update(self, delta_time: float):
        pass
    
    def draw(self, screen):
        pass
    
    def handle_input(self, event):
        pass


class OfficialScene(Scene):
    def __init__(self, width: int, height: int):
        super().__init__(SceneType.OFFICIAL, width, height)
        self.dialogue_index = 0
        self.dialogues = [
            ("内心独白", "老夫聊发少年狂。来密州已逾一年..."),
            ("侍从阿福", "大人，马已备好。黄犬和苍鹰都牵来了..."),
            ("苏轼", "好！牵犬擎鹰，我们这就出城。")
        ]
    
    def draw(self, screen):
        screen.fill((80, 80, 80))
        pygame.draw.rect(screen, (120, 100, 80), (100, 200, 800, 600))
        pygame.draw.circle(screen, (200, 180, 160), (1000, 500), 50)


class HuntScene(Scene):
    def __init__(self, width: int, height: int):
        super().__init__(SceneType.HUNT, width, height)
        self.enemies = []
        self.score = 0
        self.hunt_time = 0
        self.max_hunt_time = 300
        self.spawn_timer = 0
    
    def spawn_enemy(self):
        import random
        enemy = {
            'x': random.randint(200, 1720),
            'y': random.randint(100, 800),
            'health': 30,
            'max_health': 30,
            'type': random.choice(['rabbit', 'deer', 'tiger']),
            'vx': random.uniform(-100, 100),
            'vy': random.uniform(-50, 50)
        }
        self.enemies.append(enemy)
    
    def update(self, delta_time: float):
        self.hunt_time += delta_time
        self.spawn_timer += delta_time
        
        if self.spawn_timer > 1.0:
            self.spawn_enemy()
            self.spawn_timer = 0
        
        for enemy in self.enemies:
            enemy['x'] += enemy['vx'] * delta_time
            enemy['y'] += enemy['vy'] * delta_time
            
            if enemy['x'] < 0 or enemy['x'] > self.width:
                enemy['vx'] *= -1
            if enemy['y'] < 0 or enemy['y'] > self.height:
                enemy['vy'] *= -1
        
        self.enemies = [e for e in self.enemies if e['health'] > 0]
    
    def draw(self, screen):
        screen.fill((120, 110, 80))
        
        for enemy in self.enemies:
            color = (100, 150, 100) if enemy['type'] == 'rabbit' else (150, 120, 80)
            pygame.draw.circle(screen, color, (int(enemy['x']), int(enemy['y'])), 15)


class FeastScene(Scene):
    def __init__(self, width: int, height: int):
        super().__init__(SceneType.FEAST, width, height)
        self.firelight = 0
    
    def draw(self, screen):
        import math
        screen.fill((30, 40, 60))
        fire_x, fire_y = self.width // 2, self.height // 2
        self.firelight = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2
        pygame.draw.circle(screen, (220, 220, 200), (self.width - 100, 100), 40)


class SceneManager:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.current_scene: Optional[Scene] = None
        self.scenes = {}
        self._init_scenes()
    
    def _init_scenes(self):
        self.scenes[SceneType.OFFICIAL] = OfficialScene(self.width, self.height)
        self.scenes[SceneType.HUNT] = HuntScene(self.width, self.height)
        self.scenes[SceneType.FEAST] = FeastScene(self.width, self.height)
    
    def switch_to(self, scene_type: SceneType):
        if self.current_scene:
            self.current_scene.on_exit()
        
        self.current_scene = self.scenes[scene_type]
        self.current_scene.on_enter()
    
    def update(self, delta_time: float):
        if self.current_scene:
            self.current_scene.update(delta_time)
    
    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)
    
    def handle_input(self, event):
        if self.current_scene:
            self.current_scene.handle_input(event)
""",

    "src/audio/audio_manager.py": """import pygame
from enum import Enum
from typing import Dict, Optional

class AudioType(Enum):
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_volume = 0.8
        self.sfx_volume = 0.8
        self.voice_volume = 0.9
        
        self.current_music: Optional[pygame.mixer.Sound] = None
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.voices: Dict[str, pygame.mixer.Sound] = {}
    
    def play_music(self, music_name: str, loop: bool = True):
        try:
            pygame.mixer.music.load(f'assets/music/{music_name}.mp3')
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except:
            print(f"无法加载音乐: {music_name}")
    
    def stop_music(self):
        pygame.mixer.music.stop()
    
    def play_sfx(self, sfx_name: str):
        print(f"播放音效: {sfx_name}")
    
    def play_voice(self, character: str, text: str):
        print(f"[配音] {character}: {text}")
    
    def set_music_volume(self, volume: float):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_voice_volume(self, volume: float):
        self.voice_volume = max(0.0, min(1.0, volume))
""",

    "src/frontend/effects/advanced_particle_system.py": """import pygame
import math
import random
from typing import List

class AdvancedParticle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=5, shape='circle'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        self.shape = shape
        self.rotation = 0
        self.rotation_speed = random.uniform(-360, 360)
    
    def update(self, delta_time: float, gravity=500, air_resistance=0.99):
        self.vy += gravity * delta_time
        self.vx *= air_resistance
        self.vy *= air_resistance
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.rotation += self.rotation_speed * delta_time
        self.age += delta_time
    
    def is_alive(self):
        return self.age < self.lifetime
    
    def get_alpha(self):
        return 1.0 - (self.age / self.lifetime)
    
    def draw(self, screen):
        alpha = self.get_alpha()
        color = tuple(int(c * alpha) for c in self.color)
        if self.shape == 'circle':
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))


class AdvancedParticleSystem:
    def __init__(self):
        self.particles: List[AdvancedParticle] = []
    
    def emit_arrow_impact(self, x: float, y: float, count: int = 20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(200, 400)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            particle = AdvancedParticle(x, y, vx, vy, (220, 100, 60), 0.5, 3)
            self.particles.append(particle)
    
    def emit_blood_spray(self, x: float, y: float, direction: float, count: int = 30):
        for _ in range(count):
            angle = direction + random.uniform(-0.5, 0.5)
            speed = random.uniform(300, 500)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([(255, 100, 100), (180, 60, 60), (150, 40, 40)])
            particle = AdvancedParticle(x, y, vx, vy, color, 1.5, 4)
            self.particles.append(particle)
    
    def emit_magic_burst(self, x: float, y: float, count: int = 40):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            color = random.choice([(218, 165, 32), (255, 255, 100), (200, 200, 200)])
            particle = AdvancedParticle(x, y, vx, vy, color, 1.0, 5)
            self.particles.append(particle)
    
    def update(self, delta_time: float):
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.is_alive()]
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        self.particles.clear()
    
    def get_particle_count(self):
        return len(self.particles)
""",

    "src/game/save_system.py": """import json
import os
from typing import Dict, Any
from datetime import datetime

class GameSave:
    def __init__(self):
        self.save_slot = 1
        self.scene_name = "official"
        self.playtime = 0
        self.score = 0
        self.kills = 0
        self.arrows_fired = 0
        self.arrows_hit = 0
        self.difficulty = "normal"
        self.timestamp = datetime.now().isoformat()
        self.player_stats = {'health': 100, 'stamina': 100, 'level': 1}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'save_slot': self.save_slot,
            'scene_name': self.scene_name,
            'playtime': self.playtime,
            'score': self.score,
            'kills': self.kills,
            'arrows_fired': self.arrows_fired,
            'arrows_hit': self.arrows_hit,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp,
            'player_stats': self.player_stats
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GameSave':
        save = GameSave()
        save.save_slot = data.get('save_slot', 1)
        save.scene_name = data.get('scene_name', 'official')
        save.playtime = data.get('playtime', 0)
        save.score = data.get('score', 0)
        save.kills = data.get('kills', 0)
        save.arrows_fired = data.get('arrows_fired', 0)
        save.arrows_hit = data.get('arrows_hit', 0)
        save.difficulty = data.get('difficulty', 'normal')
        save.player_stats = data.get('player_stats', {})
        return save


class SaveSystem:
    SAVE_DIR = 'saves'
    SAVE_FILE_FORMAT = 'save_{slot}.json'
    
    def __init__(self):
        self._ensure_save_dir()
    
    def _ensure_save_dir(self):
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)
    
    def save_game(self, game_save: GameSave):
        save_file = os.path.join(self.SAVE_DIR, self.SAVE_FILE_FORMAT.format(slot=game_save.save_slot))
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(game_save.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"游戏已保存到存档 {game_save.save_slot}")
    
    def load_game(self, slot: int) -> GameSave:
        save_file = os.path.join(self.SAVE_DIR, self.SAVE_FILE_FORMAT.format(slot=slot))
        if not os.path.exists(save_file):
            return None
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return GameSave.from_dict(data)
        except Exception as e:
            print(f"加载存档失败: {e}")
            return None
    
    def get_all_saves(self) -> Dict[int, GameSave]:
        saves = {}
        for slot in range(1, 4):
            save = self.load_game(slot)
            if save:
                saves[slot] = save
        return saves
    
    def delete_save(self, slot: int):
        save_file = os.path.join(self.SAVE_DIR, self.SAVE_FILE_FORMAT.format(slot=slot))
        if os.path.exists(save_file):
            os.remove(save_file)
            print(f"已删除存档 {slot}")


class StatisticsManager:
    def __init__(self):
        self.total_playtime = 0
        self.total_shots = 0
        self.total_hits = 0
        self.total_kills = 0
        self.accuracy = 0.0
        self.best_score = 0
        self.total_games = 0
    
    def update_stats(self, game_save: GameSave):
        self.total_playtime += game_save.playtime
        self.total_shots += game_save.arrows_fired
        self.total_hits += game_save.arrows_hit
        self.total_kills += game_save.kills
        self.total_games += 1
        
        if self.total_shots > 0:
            self.accuracy = (self.total_hits / self.total_shots) * 100
        
        if game_save.score > self.best_score:
            self.best_score = game_save.score
    
    def get_average_accuracy(self) -> float:
        return self.accuracy
    
    def get_average_playtime(self) -> float:
        if self.total_games == 0:
            return 0
        return self.total_playtime / self.total_games
""",

    "requirements.txt": """pygame>=2.1.0
numpy>=1.21.0
pygame-ce>=2.2.0
""",

    "config/game_config.yaml": """game:
  title: "《江城子·密州出猎》"
  version: "0.1.0"
  author: "qiangsu1123"

window:
  width: 1920
  height: 1080
  fullscreen: false
  vsync: true

graphics:
  fps: 60
  resolution_scale: 1.0
  anti_aliasing: true
  shadow_quality: high

audio:
  master_volume: 1.0
  music_volume: 0.8
  sfx_volume: 0.8
  voice_volume: 0.9

gameplay:
  language: zh_CN
  difficulty: normal
  enable_subtitles: true
  auto_save: true
"""
}

def create_file(file_path: str, content: str):
    """创建文件"""
    # 创建目录
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"✅ 创建目录: {directory}")
    
    # 创建文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 创建文件: {file_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 JCZ 游戏项目 - 自动化部署脚本")
    print("=" * 60)
    print()
    
    print("📦 开始创建项目文件...")
    print()
    
    for file_path, content in FILES_TO_CREATE.items():
        create_file(file_path, content)
    
    print()
    print("=" * 60)
    print("✨ 项目文件创建完成！")
    print("=" * 60)
    print()
    print("📋 后续步骤:")
    print("  1. 安装依赖: pip install -r requirements.txt")
    print("  2. 运行游戏: python main.py")
    print()
    print("🎯 项目结构已完全生成！")
    print()

if __name__ == "__main__":
    main()
