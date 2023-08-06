%lang starknet

from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace IRulesTokens:

  func safeTransferFrom(_from: felt, to: felt, token_id: Uint256, amount: Uint256, data_len: felt, data: felt*):
  end
end
