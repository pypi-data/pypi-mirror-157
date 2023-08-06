from ethereumetl.domain.receipt_log import EthReceiptLog
from ethereumetl.service.token_transfer_v2_extractor import EthTokenTransferV2Extractor, word_to_address
from ethereumetl.service.token_transfer_v2_extractor import TRANSFER_EVENT_TOPICS, ERC1155_TRANSFER_SINGLE_TOPIC, ERC721_ERC_20_TRANSFER_TOPIC, ERC1155_TRANSFER_BATCH_TOPIC
from ethereumetl.utils import to_normalized_address

token_transfer_extractor = EthTokenTransferV2Extractor()


#https://etherscan.io/tx/0x5ec4c69bcff7ec3f9fbe33b93573c0e81357e36689e606fc070a52831e3586b8#eventlog
def test_extract_transfer_from_receipt_log_erc20():
    log = EthReceiptLog()
    log.address = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
    log.block_number = 14051054
    log.log_index = 0
    log.topics = [ERC721_ERC_20_TRANSFER_TOPIC,
                  '0x0000000000000000000000007a686933fc67023aabd424f35ad0b883332e2222',
                  '0x00000000000000000000000016011b51e022766c352b29b0c1ed423489f4d3ca']
    log.data = '0x0000000000000000000000000000000000000000000000000000000002faf080'
    log.transaction_hash = '0x5ec4c69bcff7ec3f9fbe33b93573c0e81357e36689e606fc070a52831e3586b8'

    token_transfers = token_transfer_extractor.extract_transfer_from_log(log)
    assert len(token_transfers) == 1
    assert token_transfers[0].token_id == '0x0000000000000000000000000000000000000000000000000000000000000001'
    assert token_transfers[0].amount == '0x0000000000000000000000000000000000000000000000000000000002faf080'
    assert token_transfers[0].block_number == 14051054
    assert token_transfers[0].from_address == word_to_address('0x0000000000000000000000007a686933fc67023aabd424f35ad0b883332e2222')
    assert token_transfers[0].to_address == word_to_address('0x00000000000000000000000016011b51e022766c352b29b0c1ed423489f4d3ca')
    assert token_transfers[0].token_type == "ERC20"
    assert token_transfers[0].contract_address == to_normalized_address('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')
    assert token_transfers[0].transaction_hash == '0x5ec4c69bcff7ec3f9fbe33b93573c0e81357e36689e606fc070a52831e3586b8'
    assert token_transfers[0].log_index == 0
    
#https://etherscan.io/tx/0x9fb4dd639dd74a24c8b1253a6199da294d08ce7587ada810c72fe89bc2225510#eventlog
def test_extract_transfer_from_receipt_log_erc721():
    log = EthReceiptLog()
    log.address = '0x716039ab9ce2780e35450b86dc6420f22460c380'
    log.block_number = 14051620
    log.log_index = 0
    log.topics = [ERC721_ERC_20_TRANSFER_TOPIC,
                  '0x000000000000000000000000b5fdfbbddc872d08d0203cd6d69d5ce67eb4c761',
                  '0x00000000000000000000000040b060a0ac95db3d5211b687511632b46c5d3bb7',
                  '0x0000000000000000000000000000000000000000000000000000000000000735']
    log.data = '0x'
    log.transaction_hash = '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'

    token_transfers = token_transfer_extractor.extract_transfer_from_log(log)
    assert len(token_transfers) == 1
    assert token_transfers[0].token_id == '0x0000000000000000000000000000000000000000000000000000000000000735'
    assert token_transfers[0].amount == '0x0000000000000000000000000000000000000000000000000000000000000001'
    assert token_transfers[0].block_number == 14051620
    assert token_transfers[0].from_address == word_to_address('0x000000000000000000000000b5fdfbbddc872d08d0203cd6d69d5ce67eb4c761')
    assert token_transfers[0].to_address == word_to_address('0x00000000000000000000000040b060a0ac95db3d5211b687511632b46c5d3bb7')
    assert token_transfers[0].token_type == "ERC721"
    assert token_transfers[0].contract_address == to_normalized_address('0x716039ab9ce2780e35450b86dc6420f22460c380')
    assert token_transfers[0].transaction_hash == '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    assert token_transfers[0].log_index == 0
    

#https://etherscan.io/tx/0xd72e66497d1614eff8136898043c22ad1d7c88e2831c57866fa5683430ef37c1#eventlog
def test_extract_transfer_from_receipt_log_erc1155_single():
    log = EthReceiptLog()
    log.address = '0x25c6413359059694A7FCa8e599Ae39Ce1C944Da2'
    log.block_number = 1061946
    log.log_index = 0
    log.topics = [ERC1155_TRANSFER_SINGLE_TOPIC,
                  '0x0000000000000000000000004fee7b061c97c9c496b01dbce9cdb10c02f0a0be',
                  '0x000000000000000000000000ab3e5a900663ea8c573b8f893d540d331fbab9f5',
                  '0x0000000000000000000000006a36f56e0a1bc32e187408f1651195d58cf688bd']
    log.data = '0x00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000004'
    log.transaction_hash = '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'

    token_transfers = token_transfer_extractor.extract_transfer_from_log(log)
    assert len(token_transfers) == 1
    assert token_transfers[0].token_id == '0x0000000000000000000000000000000000000000000000000000000000000002'
    assert token_transfers[0].amount == '0x0000000000000000000000000000000000000000000000000000000000000004'
    assert token_transfers[0].block_number == 1061946
    assert token_transfers[0].from_address == word_to_address('0x000000000000000000000000ab3e5a900663ea8c573b8f893d540d331fbab9f5')
    assert token_transfers[0].to_address == word_to_address('0x0000000000000000000000006a36f56e0a1bc32e187408f1651195d58cf688bd')
    assert token_transfers[0].token_type == "ERC1155"
    assert token_transfers[0].contract_address == to_normalized_address('0x25c6413359059694A7FCa8e599Ae39Ce1C944Da2')
    assert token_transfers[0].transaction_hash == '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    assert token_transfers[0].log_index == 0

#https://etherscan.io/tx/0xca0a113c842a1305a49107ed7b9ebef69ccca9bee2a06d5c8230cedf72284498#eventlog
def test_extract_transfer_from_receipt_log_erc1155_batch():
    log = EthReceiptLog()
    log.address = '0x6cad6e1abc83068ea98924aef37e996ed02abf1c'
    log.block_number = 1061946
    log.log_index = 0
    log.topics = [ERC1155_TRANSFER_BATCH_TOPIC,
                  '0x0000000000000000000000005bd25d2f4f26bc82a34de016d34612a28a0cd492',
                  '0x0000000000000000000000000000000000000000000000000000000000000000',
                  '0x000000000000000000000000991f3775c81d6f8331b9a812eda34ea48a7ea76d']
    log.data = '0x000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000700000000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000000000000000009000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001'
    log.transaction_hash = '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
    
    token_transfers = token_transfer_extractor.extract_transfer_from_log(log)
    assert len(token_transfers) == 10
    for iter in range(len(token_transfers)):
        assert token_transfers[iter].token_id == '0x%064x' % (iter + 1)
        assert token_transfers[iter].amount == '0x0000000000000000000000000000000000000000000000000000000000000001'
        assert token_transfers[iter].block_number == 1061946
        assert token_transfers[iter].from_address == word_to_address('0x0000000000000000000000000000000000000000000000000000000000000000')
        assert token_transfers[iter].to_address == word_to_address('0x000000000000000000000000991f3775c81d6f8331b9a812eda34ea48a7ea76d')
        assert token_transfers[iter].token_type == "ERC1155"
        assert token_transfers[iter].contract_address == to_normalized_address('0x6cad6e1abc83068ea98924aef37e996ed02abf1c')
        assert token_transfers[iter].transaction_hash == '0xd62a74c7b04e8e0539398f6ba6a5eb11ad8aa862e77f0af718f0fad19b0b0480'
        assert token_transfers[iter].log_index == 0


def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)
