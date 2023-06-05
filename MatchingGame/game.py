import random
import pygame
import psycopg2
from datetime import datetime

pygame.init()

DB_NAME = "matching_game"
DB_USER = "postgres"
DB_PASSWORD = "12341234"
DB_HOST = "localhost"
DB_PORT = "5432"

# game variables and constants
WIDTH = 600
HEIGHT = 600
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
gray = (128, 128, 128)
fps = 60
timer = pygame.time.Clock()
rows = 6
cols = 8
correct = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
options_list = []
spaces = []
used = []
new_board = True
first_guess = False
second_guess = False
first_guess_num = 0
second_guess_num = 0
score = 0
session_scores = []
matches = 0
game_over = False
previous_game_over = False  # Store the previous game over state

# create screen
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Matching Game!")
title_font = pygame.font.Font("freesansbold.ttf", 56)
medium_font = pygame.font.Font("freesansbold.ttf", 23)
small_font = pygame.font.Font("freesansbold.ttf", 18)
game_num_font = pygame.font.Font("freesansbold.ttf", 27)


# generate game board
def generate_board():
    global options_list
    global spaces
    global used
    for item in range(rows * cols // 2):
        options_list.append(item)

    for item in range(rows * cols):
        piece = options_list[random.randint(0, len(options_list) - 1)]
        spaces.append(piece)
        if piece in used:
            used.remove(piece)
            options_list.remove(piece)
        else:
            used.append(piece)


# draw the game backgrounds
def draw_backgrounds():
    top_menu = pygame.draw.rect(screen, black, [0, 0, WIDTH, 100])
    title_text = title_font.render("The Matching Game!", True, white)
    screen.blit(title_text, (10, 20))
    board_space = pygame.draw.rect(screen, gray, [0, 100, WIDTH, HEIGHT - 200], 0)
    bottom_menu = pygame.draw.rect(screen, black, [0, HEIGHT - 100, WIDTH, 100], 0)
    restart_button = pygame.draw.rect(screen, gray, [10, HEIGHT - 90, 200, 80], 0, 5)
    restart_text = title_font.render("Restart", True, white)
    screen.blit(restart_text, (10, 520))
    score_text = medium_font.render(f"Current Turns: {score}", True, white)
    screen.blit(score_text, (350, 510))
    best_text = medium_font.render(f"Best Score: {best_score}", True, white)
    screen.blit(best_text, (350, 540))
    if session_scores:
        best_text2 = small_font.render(
            f"Session Best Score: {min(session_scores)}", True, white
        )
        screen.blit(best_text2, (350, 570))
    return restart_button


# draw the game board
def draw_board():
    global rows
    global cols
    global correct
    board_list = []
    for i in range(cols):
        for j in range(rows):
            piece = pygame.draw.rect(
                screen, white, [i * 75 + 12, j * 65 + 112, 50, 50], 0, 4
            )
            board_list.append(piece)

    for r in range(rows):
        for c in range(cols):
            if correct[r][c] == 1:
                pygame.draw.rect(
                    screen, green, [c * 75 + 10, r * 65 + 110, 54, 54], 3, 4
                )
                piece_text = game_num_font.render(
                    f"{spaces[c * rows + r]}", True, black
                )
                screen.blit(piece_text, (c * 75 + 18, r * 65 + 120))

    return board_list


# save game data to the database
def save_game_data(score, time, date):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cursor = connection.cursor()

        # Insert game data into the database
        query = "INSERT INTO game_history (score, time, date) VALUES (%s, %s, %s);"
        cursor.execute(query, (score, time, date))

        connection.commit()
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)


# get the best score from the database
def get_best_score():
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cursor = connection.cursor()

        # Retrieve the best score from the game history
        query = "SELECT MIN(score) FROM game_history;"
        cursor.execute(query)
        best_score = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return best_score

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL:", error)


best_score = get_best_score()


# check if the selected cards match
def check_guesses(first, second):
    global spaces
    global correct
    global score
    global matches
    if spaces[first] == spaces[second]:
        col1 = first // rows
        col2 = second // rows
        row1 = first - (col1 * rows)
        row2 = second - (col2 * rows)
        if correct[row1][col1] == 0 and correct[row2][col2] == 0:
            correct[row1][col1] = 1
            correct[row2][col2] = 1
            score += 1
            matches += 1
    else:
        score += 1


running = True
while running:
    timer.tick(fps)
    screen.fill(white)

    if new_board:
        generate_board()
        new_board = False

    restart = draw_backgrounds()
    board = draw_board()

    if first_guess and second_guess:
        check_guesses(first_guess_num, second_guess_num)
        pygame.time.delay(1000)
        first_guess = False
        second_guess = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(board)):
                button = board[i]
                if not game_over:
                    if button.collidepoint(event.pos) and not first_guess:
                        first_guess = True
                        first_guess_num = i
                    if (
                        button.collidepoint(event.pos)
                        and not second_guess
                        and first_guess
                        and i != first_guess_num
                    ):
                        second_guess = True
                        second_guess_num = i
            if restart.collidepoint(event.pos):
                options_list = []
                used = []
                spaces = []
                new_board = True
                score = 0
                matches = 0
                first_guess = False
                second_guess = False
                correct = [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0],
                ]
                game_over = False
                # Add save_game_data() here to save data after restarting the game
                current_time = (
                    pygame.time.get_ticks() // 1000
                )  # Convert milliseconds to seconds
                # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # save_game_data(score, current_time, current_date)

    if matches == rows * cols // 2 and game_over == False:
        game_over = True
        session_scores.append(score)
        winner = pygame.draw.rect(
            screen, gray, [10, HEIGHT - 300, WIDTH - 20, 80], 0, 5
        )
        winner_text = title_font.render(f"You Won in {score} moves!", True, white)
        screen.blit(winner_text, (10, HEIGHT - 290))
        pygame.display.flip()
        pygame.event.pump()

        if best_score > score or best_score == 0:
            best_score = score

        current_time = (
            pygame.time.get_ticks() // 1000
        )  # Convert milliseconds to seconds

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_game_data(score, current_time, current_date)
        pygame.time.delay(5000)

    if first_guess:
        piece_text = game_num_font.render(f"{spaces[first_guess_num]}", True, blue)
        location = (
            first_guess_num // rows * 75 + 18,
            (first_guess_num - (first_guess_num // rows * rows)) * 65 + 120,
        )
        screen.blit(piece_text, (location))

    if second_guess:
        piece_text = game_num_font.render(f"{spaces[second_guess_num]}", True, blue)
        location = (
            second_guess_num // rows * 75 + 18,
            (second_guess_num - (second_guess_num // rows * rows)) * 65 + 120,
        )
        screen.blit(piece_text, (location))

    pygame.display.flip()

pygame.quit()
