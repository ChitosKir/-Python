from random import shuffle
from datetime import datetime

def check_input():
    while True:
        user_input = input()
        if user_input.isdigit():
            num = int(user_input)
            if 1 <= num <= 5:
                break
            else:
                print("Должна быть введена цифра от 1 до 5!")
        else:
            print("Введено не число!")
    return num

questions = []
with open("questions.txt", "r", encoding='utf-8') as file:
    line = file.readline()
    while line:
        questions.append(list(line.strip().split("|")))
        line = file.readline()
shuffle(questions)

for quest in questions:
    options = quest[1:6]
    shuffle(options)
    quest[1:6] = options

time_start = datetime.now()
total_quest = len(questions)
correct_answers = 0
for i in range(0, total_quest):
    print(f"Вопрос {i+1}/{total_quest}: {questions[i][0]}")
    for j in range(1, 6):
        print(f"{j}. {questions[i][j]}")
    answer = check_input()
    if (questions[i][answer] == questions[i][-1]):
        correct_answers += 1
        print("Правильно!")
    else:
        print("Неправильно")
    if (i != total_quest-1):
        print("Переходим к следующему вопросу...")
print("Тестирование завершено!")
time_end = datetime.now()

print("Общее количество вопросов:", total_quest)
print("Количество правильных ответов:", correct_answers)
print(f"Процент правильных ответов: {correct_answers/total_quest*100:.2f}%")

with open("result.txt", "w", encoding='utf-8') as file:
    file.write(f"Время начала теста: {time_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
    file.write(f"Время окончания теста: {time_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
    file.write(f"Общее количество вопросов: {str(total_quest)}\n")
    file.write(f"Количество правильных ответов: {str(correct_answers)}\n")
    file.write(f"Процент правильных ответов: {correct_answers/total_quest*100:.2f}%")