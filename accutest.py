from salmonberry import *


answers = load_ratings(RATING_FILENAME)

predictor = Predictor(answers.values())

mean, std = predictor.error

print(f'mean: {100 * mean:>5.2f}%')
print(f'std : {100 * std:>5.2f}%')
