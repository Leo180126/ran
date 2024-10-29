import pygame, sys, time, random, cv2
import mediapipe as mp

# Initialize pygame and check for errors
check_errors = pygame.init()
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initializing game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialized')

# Set up screen size and colors
frame_size_x = 720
frame_size_y = 480
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
pygame.display.set_caption('Snake Eater')

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
red = pygame.Color(255, 0, 0)

# Game variables
difficulty_levels = {'Easy': 10, 'Medium': 25, 'Hard': 40, 'Impossible': 60}
difficulty = 25
is_paused = False

# Set up MediaPipe and OpenCV for camera control
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# Snake variables
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
food_spawn = True
direction = 'RIGHT'
score = 0

fps_controller = pygame.time.Clock()

# Functions for the game
def game_over():
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x / 2, frame_size_y / 4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    cap.release()
    sys.exit()

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x / 10, 15)
    else:
        score_rect.midtop = (frame_size_x / 2, frame_size_y / 1.25)
    game_window.blit(score_surface, score_rect)

# Menu for difficulty selection
def menu():
    global difficulty
    while True:
        game_window.fill(black)
        menu_font = pygame.font.SysFont('times new roman', 50)
        easy_surface = menu_font.render('Nhan1: Easy', True, white)
        medium_surface = menu_font.render('Nhan2: Medium', True, white)
        hard_surface = menu_font.render('Nhan3: Hard', True, white)
        impossible_surface = menu_font.render('Nhan4: Impossible', True, white)

        game_window.blit(easy_surface, (frame_size_x / 2 - 100, frame_size_y / 2 - 100))
        game_window.blit(medium_surface, (frame_size_x / 2 - 100, frame_size_y / 2 - 50))
        game_window.blit(hard_surface, (frame_size_x / 2 - 100, frame_size_y / 2))
        game_window.blit(impossible_surface, (frame_size_x / 2 - 100, frame_size_y / 2 + 50))

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = difficulty_levels['Easy']
                    return
                elif event.key == pygame.K_2:
                    difficulty = difficulty_levels['Medium']
                    return
                elif event.key == pygame.K_3:
                    difficulty = difficulty_levels['Hard']
                    return
                elif event.key == pygame.K_4:
                    difficulty = difficulty_levels['Impossible']
                    return

# Main game loop with pause functionality
menu()
while True:
    if not is_paused:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip the frame and process hand landmarks
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x, y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])
                cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
                
                # Update direction based on finger position
                if y < frame.shape[0] // 3:
                    direction = 'UP'
                elif y > 2 * frame.shape[0] // 3:
                    direction = 'DOWN'
                elif x < frame.shape[1] // 3:
                    direction = 'LEFT'
                elif x > 2 * frame.shape[1] // 3:
                    direction = 'RIGHT'

        # Camera display
        cv2.imshow('Camera View', frame)

        # Move the snake
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Growing snake and respawning food
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (frame_size_x // 10)) * 10, random.randrange(1, (frame_size_y // 10)) * 10]
        food_spawn = True

        # Drawing the snake and food
        game_window.fill(black)
        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
        pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        # Game Over conditions
        if snake_pos[0] < 0 or snake_pos[0] > frame_size_x - 10 or snake_pos[1] < 0 or snake_pos[1] > frame_size_y - 10:
            game_over()
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over()

        show_score(1, white, 'consolas', 20)
        pygame.display.update()
        fps_controller.tick(difficulty)

    # Pause functionality
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                is_paused = not is_paused

    # Exit camera display on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
