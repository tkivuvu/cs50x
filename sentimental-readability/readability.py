from cs50 import get_string

text = get_string("Text: ")

length = len(text)
counter_l = 0
counter_w = 0
counter_s = 0

for i in range(length):
    if text[i].isalpha():
        counter_l += 1
    elif text[i].isspace():
        counter_w += 1
    elif text[i] in ".!?":
        counter_s += 1

avg_letters = float(counter_l / (counter_w + 1) * 100)
avg_sentences = float(counter_s / (counter_w + 1) * 100)
coleman_liau_i = 0.0588 * avg_letters - 0.296 * avg_sentences - 15.8

if coleman_liau_i < 1:
    print("Before Grade 1")
elif coleman_liau_i > 15:
    print("Grade 16+")
else:
    result = round(coleman_liau_i)
    print("Grade:", result)
