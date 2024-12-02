import argparse
import logging
import sys
import re

from pyflink.common import WatermarkStrategy, Encoder, Types
from pyflink.datastream import StreamExecutionEnvironment, RuntimeExecutionMode
from pyflink.datastream.connectors import (FileSource, StreamFormat, FileSink, OutputFileConfig,
                                           RollingPolicy)

def log(letter_counts):
    letter, count = letter_counts
    logging.info(f"{letter}: {count}")

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


def count_words_by_starting_letter(input_path, output_path):
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

    if output_path is not None:
        ds.sink_to(
            sink=FileSink.for_row_format(
                base_path=output_path,
                encoder=Encoder.simple_string_encoder())
            .with_output_file_config(
                OutputFileConfig.builder()
                .with_part_prefix("prefix")
                .with_part_suffix(".ext")
                .build())
            .with_rolling_policy(RollingPolicy.default_rolling_policy())
            .build()
        )
    else:
        print("Printing result to stdout. Use --output to specify output path.")
        ds.print()

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
    parser.add_argument(
        '--output',
        dest='output',
        required=False,
        help='Output file to write results to.'
    )

    argv = sys.argv[1:]
    known_args, _ = parser.parse_known_args(argv)

    count_words_by_starting_letter(known_args.input, known_args.output)