import traceback
import argparse
from logger import logger
from datetime import datetime as dt
import pandas as pd
from service.backtest import Backtest

from service.collector import DartCollector, KrxCollector
from service.prepare import Transform
from service.strategy import QuantStragegy
from storage.csv import CsvStorage


def main(func, from_date, to_date):
    try:
        # NOTE 데이터 수집단계
        if func == "krx_market_cap_by_ticker":
            # python main.py --func krx_market_cap_by_ticker
            krx_api = KrxCollector()
            result = krx_api.get_market_cap_by_ticker(from_date='20220101', to_date='20221231', market="KOSPI")
            result.to_csv("market_cap_by_ticker_kospi_2022.csv")
        if func == "sorted_result_under_50":
            # python main.py --func sorted_result_under_50
            krx_api = KrxCollector()
            result = krx_api.get_market_cap_by_ticker(from_date='20240115', to_date='20240115', market="KOSPI")
            sorted_result = result.sort_values(by='시가총액')
            extract_result = sorted_result.head(int(len(sorted_result) * 0.5))
            extract_result.to_csv("sorted_result_under_50.csv")
        if func == "krx_market_ohlcv_by_ticker":
            # python main.py --func krx_market_ohlcv_by_ticker
            krx_api = KrxCollector()
            result = krx_api.get_market_ohlcv_by_ticker(from_date='20220101', to_date='20221231', market="KOSPI")
            result.to_csv("market_ohlcv_kospi_2022.csv")
        if func == "fix_market_cap_by_ticker":
            # python main.py --func fix_market_cap_by_ticker
            pd_data = pd.read_csv('market_cap_by_ticker.csv', index_col=0 )
            pd_data = pd_data[pd_data['종가'] != 0]
            pd_data.to_csv("market_cap_by_ticker_수정.csv")
        if func == "dart_fs_by_corp":
            # python main.py --func dart_fs_by_corp
            dart_api = DartCollector()
            result = dart_api.dart_fs_by_corp(from_date='20220101', to_date='20240101')
            logger.info(result)
        if func == "dart_fs_count":
            # python main.py --func dart_fs_count
            sorted_list = pd.read_csv('연결포괄손익계산서_20220101_20240114.csv')['corp_name'].drop_duplicates().to_list()
            sorted_list2 = pd.read_csv('연결손익계산서_20240117.csv')['corp_name'].drop_duplicates().tolist()
            logger.info(f"{len(sorted_list)}:  {sorted_list}")
        if func == "dart_fs_by_day":
            # python main.py --func dart_fs_by_day
            dart_api = DartCollector()
            result = dart_api.dart_fs_by_day(from_date='20230101', to_date='20240114')
            logger.info(result)

        # NOTE 데이터 전처리
        if func == "trans_fs_bs":
            # python main.py --func trans_fs_bs
            transform = Transform()
            transform.ffill_fs_bs('연결재무상태표', '20230101', '20240101')
        if func == "trans_fs_is":
            # python main.py --func trans_fs_is
            transform = Transform()
            transform.ffill_fs_is('연결손익계산서_20240117', '20230101', '20240101')
        if func == "trans_fs_cis":
            # python main.py --func trans_fs_cis
            transform = Transform()
            transform.ffill_fs_cis('연결포괄손익계산서_20220101_20240114', '20230101', '20240101')
        if func == "bind_for_strategy":
            # python main.py --func bind_for_strategy
            transform = Transform()
            transform.bind_for_strategy()
        
        # NOTE 전략 및 추출
        if func == "extract_stock":
            # python main.py --func extract_stock
            quant_strategy = QuantStragegy()
            result = quant_strategy.extract_stock()
            logger.info(f"\n{result}")
            result.to_csv('extract_stock_by_strategy.csv', index_label=[0])

        # NOTE 백테스트
        if func == "backtest":
            from pandas.tseries.offsets import BusinessMonthEnd
            # python main.py --func backtest
            quant_strategy = QuantStragegy()
            period_data = pd.read_csv('market_cap_by_ticker_kospi_2023.csv', index_col=[0])
            start_date = "20230101"
            end_date = "20231231"
            end_of_month_dates = [date.strftime("%Y%m%d") for date in pd.date_range(start_date, end_date, freq=BusinessMonthEnd())]
            end_of_month_dates.append('20230102')

            quant_strategy.set_factor('per')
            quant_strategy.set_factor('pbr')
            quant_strategy.set_factor('roe')
            quant_strategy.set_factor('roa')
            quant_strategy.set_factor('debt_rate')

            backtest = Backtest(stragery=quant_strategy, period_data=period_data)

            daily_total_amount = backtest.execute(start_date = dt.strptime(start_date, "%Y%m%d"), 
                                                  end_date = dt.strptime(end_date, "%Y%m%d"),
                                                  rebalancing_date=end_of_month_dates)
            
    except Exception as e:
        logger.info(e)
        logger.info(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--func', type=str)
    parser.add_argument('--from_date', type=str)
    parser.add_argument('--to_date', type=str)

    args = parser.parse_args()
    func = args.func if "func" in args else ""
    from_date = args.func if "from_date" in args else ""
    to_date = args.func if "to_date" in args else ""

    main(func, from_date, to_date)