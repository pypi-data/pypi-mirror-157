import json
import pendulum
from glob import glob
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Optional, Sequence, Union

from airflow.models import BaseOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow_fxiaoke.hooks.query import FxiaokeHooks


class FxiaokeToGCSOperator(BaseOperator):
    template_fields: Sequence[str] = (
        'start_ds',
        'end_ds',
        'bucket',
        'filename',
        'impersonation_chain',
    )

    def __init__(
        self,
        *,
        fxiaoke_object_name: str,
        start_ds: str,
        end_ds: str,
        bucket: str,
        filename: str,
        mime_type: str = 'application/json',
        delegate_to: Optional[str] = None,
        gzip: bool = False,
        impersonation_chain: Optional[Union[str, Sequence[str]]] = None,
        upload_metadata: bool = False,
        fxiaoke_conn_id='fxiaoke_default',
        gcp_conn_id: str = 'google_cloud_default',
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.fxiaoke_object_name = fxiaoke_object_name
        self.fxiaoke_conn_id = fxiaoke_conn_id
        self.start_ds = start_ds
        self.end_ds = end_ds

        self.bucket = bucket
        self.filename = filename
        self.gcp_conn_id = gcp_conn_id
        self.mime_type = mime_type
        self.delegate_to = delegate_to
        self.gzip = gzip
        self.impersonation_chain = impersonation_chain
        self.upload_metadata = upload_metadata

    def execute(self, context: 'Context'):
        """Uploads a file or list of files to Google Cloud Storage"""

        file_row_count = 0
        tmp_file_handle = NamedTemporaryFile(delete=True)
        file_mime_type = self.mime_type or 'application/json'

        fxk_hook = FxiaokeHooks(self.fxiaoke_conn_id)
        objects_iter = fxk_hook.query(
            object_name=self.fxiaoke_object_name,
            ds_start_ms=pendulum.parse(self.start_ds).int_timestamp()*1000,
            ds_end_ms=pendulum.parse(self.end_ds).int_timestamp()*1000
        )
        for row_dict in objects_iter:
            file_row_count += 1
            tmp_file_handle.write(
                json.dumps(row_dict, sort_keys=True,
                           ensure_ascii=False).encode("utf-8")
            )
            # Append newline to make dumps BigQuery compatible.
            tmp_file_handle.write(b'\n')

        # Flush file before uploading
        tmp_file_handle.flush()
        self.log.info('Uploading chunk file to GCS.')

        metadata = None
        if self.upload_metadata:
            metadata = {'row_count': file_row_count}

        hook = GCSHook(
            gcp_conn_id=self.gcp_conn_id,
            delegate_to=self.delegate_to,
            impersonation_chain=self.impersonation_chain,
        )
        hook.upload(
            self.bucket,
            self.filename,
            tmp_file_handle.name,
            mime_type=file_mime_type,
            gzip=self.gzip,
            metadata=metadata,
        )
        tmp_file_handle.close()

        file_meta = {
            'bucket': self.bucket,
            'files': self.filename,
            'total_row_count': file_row_count,
        }

        return file_meta
