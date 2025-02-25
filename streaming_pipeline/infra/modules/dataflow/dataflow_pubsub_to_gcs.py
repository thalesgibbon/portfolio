import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions, GoogleCloudOptions, SetupOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition
import argparse
import json
import ast


class PrintElement(beam.DoFn):
    def __init__(self, etc=None):
        self.etc = etc

    def process(self, element):
        print(f"{f'{self.etc}, ' if self.etc else ''}Received message: {element}")
        yield element


class WriteToGCSDoFn(beam.DoFn):
    def process(self, element):
        filename = element['gcs_path']
        data = json.dumps(element['data'])
        with beam.io.gcsio.GcsIO().open(filename, 'w') as f:
            f.write(data.encode('utf-8'))
        yield element


class TransformData(beam.DoFn):
    def __init__(self, bucket):
        self.bucket = bucket

    def process(self, element):
        table = element.attributes['type']
        gcs_path = self._file_path_prefix(table, self.bucket)
        new_element = {
            'table': table,
            'data': ast.literal_eval(element.data.decode('utf-8')),
            'gcs_path': gcs_path
        }
        yield new_element

    def _file_path_prefix(self, table, bucket) -> str:
        from datetime import datetime
        event_datetime = datetime.now()
        event_type = 'unknown' if table is None else table
        timestamp = event_datetime.strftime('%Y/%m/%d/%H/%M')
        file_name = event_datetime.strftime('%Y%m%d%H%M%S%f')[:-3]
        gcs_path = f'gs://{bucket}/output/{event_type}/{timestamp}/{event_type}_{file_name}.json'
        return gcs_path


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
        tables = ['order', 'inventory', 'user_activity']

        with beam.Pipeline(options=self.pipeline_options) as p:
            transformed_data  = (
                p
                | 'ReadFromPubSub' >> beam.io.ReadFromPubSub(subscription=subscription_path, with_attributes=True)
                | 'Transform Data' >> beam.ParDo(TransformData(self.bucket))
                | 'Print Element' >> beam.ParDo(PrintElement())
                | 'Write to GCS' >> beam.ParDo(WriteToGCSDoFn())
            )

            # todo workaround to select table_name from message and send to WriteToBigQuery
            for table_name in tables:
                (
                    transformed_data
                    | f'Filter for {table_name}' >> beam.Filter(lambda element, table=table_name: element['table'] == table)
                    | f'Extract Data {table_name}' >> beam.Map(lambda element: element['data'])
                    | f'Write to BigQuery {table_name}' >> WriteToBigQuery(
                        table=table_name,
                        dataset='raw_events',
                        project=self.project_id,
                        write_disposition=BigQueryDisposition.WRITE_APPEND,
                        create_disposition=BigQueryDisposition.CREATE_IF_NEEDED
                    )
                )


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
