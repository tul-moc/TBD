import argparse
import logging
import sys
import re

from pyflink.common import WatermarkStrategy, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors import FileSource, StreamFormat


def log(letter_counts):
    letter, count = letter_counts
    logging.info(f"{letter}: {count}")

def extract_words_and_validate(input):
    validatedWords = re.findall(r"\b[a-zA-Z]+\b", input.lower())
    words = []
    for word in validatedWords:
        if word.isalpha():
            words.append((word[0], 1))
    return words

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


def count_words_by_starting_letter(input_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_runtime_mode(RuntimeExecutionMode.BATCH)
    env.set_parallelism(1)

    if input_path is not None:
        ds = env.from_source(
            source=FileSource.for_record_stream_format(
                StreamFormat.text_line_format(),
                input_path
            )
            .process_static_file_set()
            .build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    else:
        print("No input file specified. Please run 'python letter-count.py --input <path>'")
        return

    letter_counts = get_letter_counts(ds)
    letter_counts.map(lambda x: log(x))
    env.execute()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Input file to process.'
    )

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    count_words_by_starting_letter(known_args.input)