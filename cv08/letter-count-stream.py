import argparse
import logging
import sys
import letter_utils

from pyflink.common import WatermarkStrategy, Duration
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FileSource, StreamFormat


def log(letter_counts):
    letter, count = letter_counts
    logging.info(f"{letter}: {count}")


def count_words_by_starting_letter(input_path):
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    if input_path is not None:
        ds = env.from_source(
            source=FileSource.for_record_stream_format(
                StreamFormat.text_line_format(),
                input_path
            )
            .monitor_continuously(
                Duration.of_seconds(1)
            )
            .build(),
            watermark_strategy=WatermarkStrategy.for_monotonous_timestamps(),
            source_name="file_source"
        )
    else:
        print("No input file specified. Please run 'python letter-count.py --input <path>'")
        return

    letter_counts = letter_utils.get_letter_counts(ds)
    letter_counts.print()
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