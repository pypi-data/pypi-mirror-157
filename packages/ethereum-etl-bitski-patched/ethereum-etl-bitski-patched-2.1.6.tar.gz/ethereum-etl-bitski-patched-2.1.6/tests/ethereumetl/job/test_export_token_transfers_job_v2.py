import pytest
from ethereumetl.web3_utils import build_web3

import tests.resources
from ethereumetl.jobs.export_token_transfers_job_v2 import ExportTokenTransfersJobV2
from ethereumetl.jobs.exporters.token_transfers_v2_item_exporter import token_transfers_v2_item_exporter
from ethereumetl.thread_local_proxy import ThreadLocalProxy
from tests.ethereumetl.job.helpers import get_web3_provider
from tests.helpers import compare_lines_ignore_order, read_file

RESOURCE_GROUP = 'test_export_token_transfers_job_v2'


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize("start_block,end_block,batch_size,resource_group,web3_provider_type", [
    (483920, 483920, 1, 'block_with_transfers', 'mock')
])
def test_export_token_transfers_job_v2(tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type):
    output_file_token_transfer_v2 = str(tmpdir.join('token_transfers_v2.csv'))

    job = ExportTokenTransfersJobV2(
        start_block=start_block, end_block=end_block, batch_size=batch_size,
        web3=ThreadLocalProxy(
            lambda: build_web3(get_web3_provider(web3_provider_type, lambda file: read_resource(resource_group, file)))
        ),
        token_transfers_v2_exporter=token_transfers_v2_item_exporter(output_file_token_transfer_v2),
        max_workers=5
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_token_transfers_v2.csv'), read_file(output_file_token_transfer_v2)
    )
