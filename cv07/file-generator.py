import random

file_words = [
    "I",
    "am",
    "a",
    "student",
    "at",
    "the",
    "Faculty",
    "of",
    "Information",
    "Technology",
    "at",
    "the",
    "Czech",
    "Technical",
    "University",
    "in",
    "Prague",
    "I",
    "am",
    "currently",
    "studying",
    "the",
    "course",
    "Data",
    "Processing",
    "and",
    "Analysis",
    "I",
    "am",
    "learning",
    "how",
    "to",
    "use",
    "Apache",
    "Spark",
]

for i in range(3):
    word_count = random.randint(1, 50)
    path = f"data/file{i}.txt"
    words = random.choices(file_words, k=word_count)
    with open(path, "w") as file:
        file.write(" ".join(words))
