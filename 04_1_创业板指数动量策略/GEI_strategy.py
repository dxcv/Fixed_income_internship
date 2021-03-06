# coding:utf-8
import pandas as pd
file='GE IDX.csv'
import matplotlib.pyplot as plt
import seaborn as sns
import time
tot_data=pd.read_csv(file,index_col=1,names=['','open_p','high','low','close','trade','trade_amount','earning'])
tot_data.index=pd.DatetimeIndex(tot_data.index)
price_data=tot_data[['close','earning']]

# 先不获取指数收益率了，等以后单独获取

# 我也不知道为什么要加这句话，但是不加会报错A value is trying to be set on a copy of a slice from a DataFrame
# 操作的表格转换为close_data
close_data=price_data.copy()
close_data.drop((x for x in price_data.index if price_data.loc[x][0]==0),inplace=True)

def cal_ma(long=20,short=5,l_fac=1.03,s_fac=1.03):
    # long为长的均线，short为短的均线
    # 初始化收盘价dataframe
    close_data['20avg']=close_data['close'].rolling(window=long).mean()
    close_data['5avg']=close_data['close'].rolling(window=short).mean()
    close_data['tot_return']=1 # 策略总回报
    close_data['hold_flag']=-1 # 是否持有
    # close_data['idx_return']=1 # 指数总回报
    # 455则为3年收益率,从0开始为5年收益率
    start_day=0
    for index,day  in enumerate (close_data.index[start_day:]):
        index=index+start_day
        if index==start_day:
            continue
        [close_p,earning,avg20,avg5]=close_data.loc[day][:4]
        # 主要的判断是否持有的语句
        if close_p>avg20*l_fac and close_p<avg5*s_fac:
            hold_flag=1
        else:
            hold_flag=0

        [hold_flag_,last_return]=close_data.iloc[index-1][['hold_flag','tot_return']] # 上一日是否持有,上一日的持有收益率
        if  hold_flag_==1:  # 上一日选择持有，则本日计算收益率
            tot_return = last_return*(earning/100+1) # 上日累计收益率乘本日收益率
        else:
            tot_return = last_return

        # 先暂时不考虑指数收益率，只考虑策略收益率
        # idx_r=idx_r_*(earning/100+1) # 计算指数收益率
        close_data.loc[day]=[close_p,earning,avg20,avg5]+[tot_return,hold_flag] #,idx_r]
    time_list=['2016-02-15','2017-02-14','2018-02-14','2019-02-14','2020-02-14']
    year5=[close_data['tot_return'][t] for t in time_list]
    return year5


def output(ret_list,out_file='default.csv'):
    global h_range,l_range
    out_file='.\outfile\\'+out_file
    open(out_file,'w').close()
    f = open(out_file, 'a')

    line1_list = ['{}_{}'.format(i, j) for i in l_range for j in range(16, 21)]  # 标题行
    f.write(','+','.join(line1_list) + '\n')
    for high in h_range:
        out_line=[str(high)]
        for low in l_range:
            out_line.append(str(ret_list[str(high) + '_' + str(low)])[1:-1])
        f.write(','.join(out_line)+'\n')
    f.close()


ret_list={}
# MACD指标选择的长短期为12,26
t0=time.time()

h_range=range(12,31,2)
l_range=range(3,13)

fac_range=[i/100 for i in range(96,106,2)]

for h_fac in fac_range:
    for l_fac in fac_range:
        # 取不同的上下限
        for high in h_range:
            for low in l_range:
                if high<=low:# 如果上下限不合理，跳过
                    ret_list[str(high) + '_' + str(low)] = [0 for i in range(5)]
                    continue
                tot_time = time.time() - t0
                print('\r{} min : {} sec   '.format(int(tot_time / 60), int(tot_time % 60)), end='')
                y5_r=cal_ma(high,low)
                ret_list[str(high)+'_'+str(low)]=y5_r
                print('{}_{}:{}'.format(high,low,y5_r))

        # 命名方法：长期的乘数+短期的乘数
        output(ret_list,out_file=str(h_fac)+'_'+str(l_fac)+'.csv')



def plott():
    sns.set()

    # 肯定有更好的方法，可是我不知道
    scatter=pd.DataFrame([[date,close_data['tot_return'].loc[date]] for date in close_data.index if close_data['hold_flag'].loc[date]==1])
    scatter.set_axis(['date','return'],1,inplace=True)

    scatter=scatter.set_index('date')

    fig=plt.figure()
    ax=fig.add_subplot(111)
    ax.plot(close_data[['idx_return','tot_return']])
    ax.bar(scatter.index,height=scatter['return'],width=1,linewidth=0,color='grey',alpha=0.3)
    plt.show()