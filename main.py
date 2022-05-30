import asyncio
from terra_sdk.client.lcd import AsyncLCDClient
from terra_sdk.key.mnemonic import MnemonicKey
from terra_sdk.client.lcd.api.tx import CreateTxOptions
from terra_sdk.core.wasm import MsgExecuteContract
from terra_sdk.core import Coins


async def main():
    denominator = 1_000_000
    luna_amount = 1_000_000     # 1 Luna

    luna_bluna_contract_addr = "terra1jxazgm67et0ce260kvrpfv50acuushpjsz2y0p"

    mnemonicKey = get_mnemonic_key()
    mk = MnemonicKey(mnemonic=mnemonicKey)

    terra = AsyncLCDClient("https://lcd.terra.dev", "columbus-5")
    wallet = terra.wallet(mk)

    print(f"welcome: {wallet.key.acc_address}")

    # Create message to swap luna->bLuna (native to cw20)
    msg = [MsgExecuteContract(
        wallet.key.acc_address,
        luna_bluna_contract_addr,
        execute_msg={
            "swap": {
                "offer_asset": {
                    "info": {
                        "native_token": {
                            "denom": "uluna"
                        }
                    },
                    "amount": str(luna_amount * denominator)
                }
            }
        },
        coins=Coins(uluna=(luna_amount*denominator))
    )]

    # Signed contract
    tx = await wallet.create_and_sign_tx(CreateTxOptions(
        msg,
        gas_prices="0.15uusd",
        gas_adjustment="1.3",
        memo=""
    ))

    # Broadcast TX
    result = await terra.tx.broadcast_async(tx=tx)
    print(result.txhash)

    # close asnyc function
    await terra.session.close()


def get_mnemonic_key() -> str:
    with open("mnemonic.txt", 'r') as reader:
        key = reader.read()
    return key


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
