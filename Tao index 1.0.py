import pandas as pd
import matplotlib.pyplot as plt
import fxcmpy

class Plot_index:
    def __init__(self, currency_index, currency_list, pair_plot, period, number_data, index_type):
        """
        Parameters:
        currency_index - Dong tien dong de ve index ("USD", "EUR, .....) - dang str
        currency_list - List cac dong tien dong de tinh index (["USD", "EUR, ....]) - dang list chua cac str
        pair_plot - Cap tien dung de ve cung voi index ("EUR/USD" ....) - dang str
        period - Khung thoi gian duoc dung ('m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
        'D1', 'W1', 'M1') - dang str
        number_data - dang so int (<10.000)
        index_type: 0: kieu thong thuong, 1: kieu abs tong min, 2: kieu tong abs min, 3: kieu binh phuong min
        """
        self.currency_index = currency_index
        self.currency_list = currency_list
        self.pair_plot = pair_plot
        self.period = period
        self.number_data = number_data
        self.index_type = index_type

        self.api = fxcmpy.fxcmpy(access_token="2fc647e267d8c700bed406151751417453dbd4ff"
                                 , log_level='error', server='demo', log_file='log.txt')
        self.data_list = []
        self.data_0 = pd.DataFrame({'date': []})
        self.data_1 = None

        self.creat_data_list()
        self.price_matrix()
        self.calculation_index()
        self.index_plot()

    #Ham tao list symbol dang "USD/XXX" dung de tinh gia cac cap cheo khac
    def creat_data_list(self):
        for cur3 in self.currency_list:
            if cur3 != 'USD':
                pair2 = cur3 + "/" + 'USD'
                self.data_list.append(pair2)
        return self.data_list

    #Ham tinh ma tran gia
    def price_matrix(self):
        for pair3 in self.data_list:
            try:
                self.data_0 = pd.merge_ordered(self.data_0,
                                               self.api.get_candles(pair3,
                                                                    period=self.period, number=self.number_data,
                                                                    columns=["bidclose"]), on='date',
                                               fill_method='ffill')
            except:
                self.data_0 = pd.merge_ordered(self.data_0,
                                               1/self.api.get_candles(pair3[4:7] + pair3[3] + pair3[0:3],
                                                                      period=self.period, number=self.number_data,
                                                                      columns=["bidclose"]), on='date',
                                               fill_method='ffill')
        self.data_0.columns = ['date'] + self.data_list
        self.data_0 = self.data_0.set_index('date')
        self.data_0 = self.data_0.dropna()

        # Tao bang data chua tat ca cac cap tien
        for pair4 in self.data_list:
            for pair5 in self.data_list:
                if pair4 != pair5:
                    self.data_0[pair4[0:3] + pair4[3] + pair5[0:3]] = self.data_0[pair4] / self.data_0[pair5]
                else:
                    self.data_0[pair4[4:7] + pair4[3] + pair4[0:3]] = 1/self.data_0[pair4]
        return self.data_0

    #Ham chuyen data ve dang pct change va tinh data index
    def calculation_index(self):
        # Tao bang data theo % thay doi gia
        self.data_1 = self.data_0.pct_change().dropna()

        if self.index_type == 0:
            self.data_1['Data_used'] = 0
            for cur5 in self.currency_list:
                if cur5 != self.currency_index:
                    self.data_1['Data_used'] += self.data_1[self.currency_index + "/" + cur5] / (
                                len(self.currency_list) - self.currency_list.count(self.currency_index))
        else:
            # Them tong % bien dong cua tung dong tien vao bang du lieu
            for cur5 in self.currency_list:
                if cur5 != self.currency_index:
                    self.data_1[cur5] = 0
                for cur6 in self.currency_list:
                    if cur5 != self.currency_index and cur5 != cur6:
                        if self.index_type == 1:
                            self.data_1[cur5] += self.data_1[cur5 + "/" + cur6]
                        elif self.index_type == 2:
                            self.data_1[cur5] += self.data_1[cur5 + "/" + cur6].abs()
                        elif self.index_type == 3:
                            self.data_1[cur5] += self.data_1[cur5 + "/" + cur6] ** 2
            # Tinh tri tuyet doi cua tong bien dong
            self.data_1[[x for x in self.currency_list if x != self.currency_index]] = \
                self.data_1[[x for x in self.currency_list if x != self.currency_index]].abs()
            # Tao cot chua dong tien tot nhat
            self.data_1['Best_cur'] = self.data_1.loc[:, [x for x in self.currency_list if x != self.currency_index]]\
                .idxmin(axis="columns")
            # Tao cot chua du lieu can dung
            list_data_used = []
            for index, row in self.data_1.iterrows():
                list_data_used.append(row[self.currency_index + '/' + row['Best_cur']])
            self.data_1['Data_used'] = list_data_used
        # Tao cot chua data index
        self.data_1['Index_value'] = self.data_1['Data_used'].cumsum()
        return self.data_1

    # Ham ve do thi
    def index_plot(self):
        fig, ax = plt.subplots(2, 1)
        ax[0].plot(range(self.data_1[self.pair_plot].index.size), self.data_1[self.pair_plot].cumsum(), color='b')
        ax[1].plot(range(self.data_1["Index_value"].index.size), self.data_1["Index_value"], color='r')
        ax[0].set_ylabel(self.pair_plot, fontsize=30)
        ax[1].set_ylabel(self.currency_index, fontsize=25)
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        fig.set_size_inches([30, 20])
        plt.show()


a = Plot_index('USD', ['EUR','USD','JPY','CHF','CAD','AUD','NZD'], 'EUR/USD', 'm15', 1000, 1)