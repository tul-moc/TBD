import re
import logging

from pyflink.common import Types

def extract_words_and_validate(input):
    validatedWords = re.findall(r"\b[\wá-ž]+\b", input.lower(), re.UNICODE)
    return [(word[0], 1) for word in validatedWords]

def get_letter_counts(ds):
    letter_counts = (
        ds.flat_map(
            extract_words_and_validate, 
            output_type=Types.TUPLE([Types.STRING(), Types.INT()])
        )
        .key_by(lambda x: x[0])
        .reduce(lambda x, y: (x[0], x[1] + y[1]))
    )

    return letter_counts