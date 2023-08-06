# Example PyPI (Python Package Index) Package

from apache_beam import PTransform
import apache_beam as beam
from apache_beam.pipeline import Pipeline
from apache_beam.options.pipeline_options import PipelineOptions


class ReadFile(PTransform):
    def __init__(self, file_path):
        self.file_path = file_path
    def expand(self, pcoll):
        return pcoll | beam.io.ReadFromText(self.file_path)
    

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        dest='input',
                        required=True,
                        help='Input file to process.')
    known_args = parser.parse_known_args(argv)
    input_path = known_args[0].input
    #input_path = 'test_text.txt'
    p = beam.Pipeline(options=PipelineOptions())
    p | ReadFile(input_path)| beam.io.WriteToText('output.txt')
    p.run()

    

if __name__ == '__main__':
    main()
