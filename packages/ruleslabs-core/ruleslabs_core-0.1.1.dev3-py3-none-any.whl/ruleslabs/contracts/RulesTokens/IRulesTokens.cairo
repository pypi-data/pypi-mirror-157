%lang starknet

from starkware.cairo.common.uint256 import Uint256

from ruleslabs.models.card import CardModel
from ruleslabs.models.metadata import Metadata

@contract_interface
namespace IRulesPacks:

  func safeTransferFrom(_from: felt, to: felt, token_id: Uint256, amount: Uint256, data_len: felt, data: felt*):
  end
end
