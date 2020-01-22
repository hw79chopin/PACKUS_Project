import pandas as pd
import numpy as np
import dateutil
from dateutil.parser import parse
import datetime
from datetime import timedelta

class Customer:
    def __init__(self, data, name):
        self.name = name
        self.receipt = data[data['주문자ID']==self.name].sort_values(by=['주문일시'])
        
    # 총 몇 번 주문했는지
    def order_count(self):
        return self.receipt.shape[0]

    # 마지막 주문은 언제인지
    def last_order(self):
        df_cst = self.receipt[self.receipt['주문자ID']==self.name]
        last_order = df_cst['주문일시'].iloc[-1]
        print('{}년 {}월 {}일'.format(last_order.year, last_order.month, last_order.day))
        
    # 특정 기간동안 샀던 품목들과 평균구매주기를 반환
    def purchase_product(self, yyyymmdd = pd.Timestamp.now(), month = 3):
        if type(month) != int:
            raise ValueError("month must be a int")
        self.month = month
        self.start_point = yyyymmdd
        if type(yyyymmdd) is not pd.Timestamp:
            self.start_point = datetime.datetime(year=int(yyyymmdd[:4]), month=int(yyyymmdd[4:6]), day=int(yyyymmdd[6:]))
        elif type(yyyymmdd) is pd.Timestamp:
            self.start_point = yyyymmdd
            
        back_point = self.start_point-timedelta(days=self.month*30)
        print('시작일시 :', back_point)
        print('종료일시 :', self.start_point)
        receipt_limited = self.receipt[self.receipt['주문일시']>back_point]
        receipt_limited = receipt_limited[receipt_limited['주문일시']<self.start_point]
        self.receipt_limited = receipt_limited

        print('기간 내 결제금액 :', self.receipt_limited.drop_duplicates(['주문일시'])['총 결제금액'].sum())
        product_list = [product for product in list(receipt_limited['세부분류사이즈'].unique()) if type(product) is str]  
        product_list = list(set(product_list))
        
        list_product_average_order_period = []
        list_product_total_using_period = []
        for product in product_list:
            list_collect_product_order_period = []
            df_specific_product = receipt_limited[receipt_limited['세부분류사이즈']==product].drop_duplicates(['주문일시']).sort_values(by='주문일시') # 해당 품목만 있는 데이터프레임 만들어주기
            
            # 먼저 상품구매경험이 2회 이상인 품목들의 구매주기 모아주기
            if (df_specific_product.shape[0] > 1):
                for i in range(df_specific_product.shape[0]-1):
                    product_order_period = df_specific_product['주문일시'].iloc[i+1] - df_specific_product['주문일시'].iloc[i]
                    if product_order_period.days == 0:    # 하루 내 여러 차례 주문한 것들은 한 번 주문한 것으로 간주
                        list_collect_product_order_period.append([product, 0]) # 구매주기를 품목과 같이 append
                    else:
                        list_collect_product_order_period.append([product, product_order_period]) # 구매주기를 품목과 같이 append
                        
            # 상품구매경험이 1회밖에 없는 사람들의 구매주기는 0으로 계산
            else:  
                for i in range(df_specific_product.shape[0]):
                    list_collect_product_order_period.append([product, 0])

            # 구매주기의 평균 구하기
            total_timedelta = datetime.timedelta(days=0, seconds=0)
            for i in list_collect_product_order_period:
                if type(i[1]) is timedelta:
                    total_timedelta = total_timedelta + i[1]
            average_order_period = round(total_timedelta.days/len(list_collect_product_order_period),2)
            list_product_average_order_period.append([product, average_order_period])    # 품목별 평균구매주기 구했음

            # 상품 누적사용일 구하기
            if (df_specific_product.shape[0] > 1):
                product_1st_end_period = (df_specific_product['주문일시'].iloc[-1] - df_specific_product['주문일시'].iloc[0]).days
                list_product_total_using_period.append([product, product_1st_end_period + average_order_period])
            else:
                list_product_total_using_period.append([product, 0])
        
        # 전체 사용주기에서 제품이랑 누적사용일 zip해줘서 dictionary로 만들고
        product = []
        days = []
        for i in list_product_total_using_period:
            product.append(i[0])
            days.append(i[1])
        day_dict = dict(zip(product, days))

        df_pivot = self.receipt_limited.pivot_table(index='주문연월', columns='세부분류사이즈',
                               values='총주문량', aggfunc=np.sum)
        df_pivot = df_pivot.T.fillna(0).reset_index()
        df_pivot['총합'] = df_pivot.sum(axis=1)
        df_pivot['전체사용일'] = df_pivot['세부분류사이즈'].map(day_dict)
        df_pivot['하루당 사용량'] = round((df_pivot['총합'] / df_pivot['전체사용일']),2)
        final_pivot = df_pivot[['세부분류사이즈','총합','전체사용일','하루당 사용량']]
        final_pivot = final_pivot.dropna(axis=0)
        final_pivot['하루당 사용량'] = final_pivot['하루당 사용량'].replace(np.inf, 0)
        final_pivot = final_pivot.sort_values(by=['총합'], ascending=False)
        self.final_pivot = final_pivot
        return final_pivot

    # 하루 수요량 계산
    def daily_demand(self, yyyymmdd = pd.Timestamp.now(), month = 3):
        self.yyyymmdd = yyyymmdd
        self.month = month
        final_pivot = self.purchase_product(self.yyyymmdd, self.month)
        baby_data = dict(zip(final_pivot['세부분류사이즈'].values, final_pivot['하루당 사용량'].values))
        baby_data['주문자ID'] = self.name
        baby_df = pd.DataFrame(baby_data, columns=list(baby_data.keys()), index=[0])
        baby_df = baby_df.dropna(axis=0)
        cols = list(baby_df.columns)
        cols = [cols[-1]]+cols[:-1]
        return baby_df[cols]
    
    # 회원등급 파악하기
    def membership(self):
        if self.receipt['군집_5'].iloc[0] == 2:
            return 'Level.5 대상인'
        if self.receipt['군집_5'].iloc[0] == 4:
            return 'Level.4 장사 잘 되는 중소상인'
        if self.receipt['군집_5'].iloc[0] == 1:
            return 'Level.3 중소상인'
        if self.receipt['군집_5'].iloc[0] == 3:
            return 'Level.2 영세상인'
        if self.receipt['군집_5'].iloc[0] == 0:
            return 'Level.1 병아리'
        if self.receipt['군집_5'].iloc[0] == None:
            return 'Not Royal'
        
    # 구매주기 파악하기
    def period_cycle(self):
        period_list = []
        df = self.receipt.drop_duplicates(['주문일시'])
        for i in range(df.shape[0]-1):
            period = df['주문일시'].iloc[i+1] - df['주문일시'].iloc[i]
            if period > datetime.timedelta(days=1):
                period_list.append(period)
        total = datetime.timedelta(days=0)
        for i in period_list:
            total = total + i
        period_cycle = total/len(period_list)
        return period_cycle