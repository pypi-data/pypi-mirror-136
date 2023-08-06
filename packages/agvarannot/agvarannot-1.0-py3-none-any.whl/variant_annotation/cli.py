import argparse
import logging
import os
import pathlib
import json
import csv
from consumer import VariantAnnotation


class ValidationException(Exception):
    pass


class UserCliArgs:
    def _valid_extension_file(self, param):
        base, ext = os.path.splitext(param)
        if ext.lower() not in '.txt':
            raise argparse.ArgumentTypeError('File must have a txt extension')
        return param

    def _read_cli_args(self):
        """Handles the CLI user interactions.
        Returns:
            argparse.Namespace: Populated namespace object
        """
        parser = argparse.ArgumentParser(
            description="Generate annotate variants."
        )
        parser.add_argument(
            "-i", "--input",
            type=self._valid_extension_file,
            help="Input file",
            required=True
        )
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            help="Output file",
            required=True
        )

        return parser.parse_args()

    def validate_file_content(self):
        args = self._read_cli_args()

        if not pathlib.Path(args.input).is_file():
            raise argparse.ArgumentTypeError('The file does not exist')
        else:
            with open(args.input) as file_input:
                variants = []
                for line in file_input:
                    variants.append(line.rstrip())

            if not variants:
                raise argparse.ArgumentTypeError('The file is empty')

            return variants, args.output


class BuildReport:
    def __init__(self, data, data_with_error):
        self.data = data
        self.data_with_error = data_with_error

    def _build_error_report(self, output):
        error_name = output.split('.')

        with open(error_name[0] + '_error.txt', 'w') as file:
            json_string = json.dumps(
                self.data_with_error,
                default=lambda o: o.__dict__,
                sort_keys=True,
                indent=4
            )
            file.write(json_string)

    def build_txt_report(self, output):
        try:
            with open(output, 'w') as file:
                json_string = json.dumps(
                    self.data,
                    default=lambda o: o.__dict__,
                    sort_keys=True,
                    indent=4
                )
                file.write(json_string)

            if self.data_with_error:
                self._build_error_report(output)

            print("Files generated!!")
        except IOError as io:
            print('\n', io)

    def build_csv_report(self, output):
        def merge_data():
            to_csv = []
            for values in self.data.values():
                for value in values:
                    to_csv.append(value)
            return to_csv

        data_to_csv = merge_data()
        keys = data_to_csv[0].keys()

        try:
            with open(output, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data_to_csv)

            if self.data_with_error:
                self._build_error_report(output)

            print("Files generated!!")
        except IOError as io:
            print('\n', io)


def variant_annotation_cli():
    user_cli_args = UserCliArgs()
    variants, output = user_cli_args.validate_file_content()

    variant_annotation = VariantAnnotation(list(set(variants)))
    data, data_with_error = variant_annotation.get_data()

    return data, data_with_error, output


def variant_annotation_cli_txt():
    data, data_with_error, output = variant_annotation_cli()
    report = BuildReport(data, data_with_error)
    report.build_txt_report(output)


def variant_annotation_cli_csv():
    data, data_with_error, output = variant_annotation_cli()
    report = BuildReport(data, data_with_error)
    report.build_csv_report(output)


if __name__ == "__main__":
    try:
        variant_annotation_cli_txt()
    except ValidationException as e:
        logging.error(e)
    except Exception as e:
        logging.exception(e)



