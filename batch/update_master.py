from .utils.make_target import make_target_main
from .utils.asset_aggregation import make_asset_main
from .utils.balance_aggregation import make_balance_main
from .utils.profit_aggregation import make_profit_main

def update_master():
    make_target_main()
    make_asset_main()
    make_balance_main()
    make_profit_main()

if __name__ == "__main__":
    update_master()