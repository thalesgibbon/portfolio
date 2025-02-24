import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions, SetupOptions
import argparse
import json


class WriteToGCSDoFn(beam.DoFn):
    def process(self, element):
        filename, data = element
        with beam.io.gcsio.GcsIO().open(filename, 'w') as f:
            f.write(data.encode('utf-8'))
        yield filename


class PubSubToGCSPipeline:
    def __init__(self, runner: str, project_id: str, input_subscription: str, bucket: str, file_name_prefix: str = 'messages'):
        self.runner = runner
        self.project_id = project_id
        self.input_subscription = input_subscription
        self.bucket = bucket
        self.file_name_prefix = file_name_prefix
        self.pipeline_options = self._create_pipeline_options()

    def file_path_prefix(self, table) -> str:
        from datetime import datetime
        event_datetime = datetime.now()
        event_type = 'unknown' if table is None else table
        timestamp = event_datetime.strftime('%Y/%m/%d/%H/%M')
        file_name = event_datetime.strftime('%Y%m%d%H%M%S%f')[:-3]
        gcs_path = f'gs://{self.bucket}/output/{event_type}/{timestamp}/{event_type}_{file_name}.json'
        return gcs_path

    def _create_pipeline_options(self) -> PipelineOptions:
        if self.runner == 'DataflowRunner':
            print("Executando no Google Cloud Dataflow...")
            pipeline_options = PipelineOptions()

            pipeline_options.view_as(SetupOptions).save_main_session = True

            standard_options = pipeline_options.view_as(StandardOptions)
            standard_options.streaming = True
            standard_options.runner = 'DataflowRunner'

            gcloud_options = pipeline_options.view_as(GoogleCloudOptions)
            gcloud_options.temp_location = f'gs://{self.bucket}/temp'
            gcloud_options.staging_location = f'gs://{self.bucket}/staging'
            gcloud_options.project = self.project_id
            gcloud_options.region='us-central1'
            gcloud_options.job_name = 'dataflow-pubsub-to-gcs-json'
        else:
            print("Executando localmente com DirectRunner...")
            pipeline_options = PipelineOptions()
            standard_options = pipeline_options.view_as(StandardOptions)
            standard_options.streaming = True
            standard_options.runner = 'DirectRunner'

        return pipeline_options

    def run(self) -> None:
        subscription_path = f'projects/{self.project_id}/subscriptions/{self.input_subscription}'

        with beam.Pipeline(options=self.pipeline_options) as p:
            (
                p
                | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription=subscription_path, with_attributes=True)
                | 'DecodeMessage' >> beam.Map(lambda msg: self.decode_element(msg))
                | 'PrintMessage1' >> beam.Map(lambda msg: self.print_element(msg))
                | 'FormatToJson' >> beam.Map(lambda msg: (self.file_path_prefix(msg['table']), json.dumps(msg['data'])))
                | 'Write to GCS' >> beam.ParDo(WriteToGCSDoFn())
            )

    @staticmethod
    def print_element(element):
        print(f"Received message: {element}")
        return element

    @staticmethod
    def decode_element(element):
        new_element = {
            'table': element.attributes['type'],
            'data': element.data.decode('utf-8')
        }
        return new_element


if __name__ == '__main__':
    project_id = 'prj-tg-portfolio-00000'
    input_subscription = "backend-events-topic-sub"
    bucket = 'tg-portfolio-datalake-bucket'

    parser = argparse.ArgumentParser(description='Apache Beam Pub/Sub Reader')
    parser.add_argument(
        '--runner',
        dest='runner',
        default='DirectRunner',
        choices=['DirectRunner', 'DataflowRunner'],
        help='Executar DirectRunner ou DataflowRunner'
    )
    args, _ = parser.parse_known_args()

    pipeline = PubSubToGCSPipeline(
        runner=args.runner,
        project_id=project_id,
        input_subscription=input_subscription,
        bucket=bucket,
    )
    pipeline.run()
