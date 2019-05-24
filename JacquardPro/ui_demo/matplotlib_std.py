# -*- coding:utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core import frame
from matplotlib.ticker import FuncFormatter
from numpy import ndarray


print __name__
# matplotlib有许多不同的样式可用于渲染绘图,通过下面的可以查看样式表
# plt.style.available
# 简单使用一个样式：
plt.style.use('ggplot')



# Matplotlib支持许多不同格式文件的保存。 你可以用fig.canvas.get_supported_filetypes（）查看系统支持的格式：
# fig.canvas.get_supported_filetypes()

# def test1():
#
#     df = pd.read_excel(r"C:\Users\hely\Desktop\a.xlsx")
#     df.head()
#
#     print df.groupby('name')['ext price', 'quantity']
#
#     top_10 = (df.groupby('name')['ext price', 'quantity'].agg({'ext price': 'sum', 'quantity': 'count'})
#               .sort_values(by='ext price', ascending=False))[:10].reset_index()
#
#     print top_10
#     # if isinstance(top_10, frame.DataFrame):
#     #     print top_10.values
#
#
#     top_10.rename(columns={'name': 'Name', 'ext price': 'Sales', 'quantity': 'Purchases'}, inplace=True)
#     print top_10
#
#     # 使用 pandas快速绘图
#     top_10.plot(kind='barh', y="Sales", x="Name")
#     plt.show()
#
# def test2():
#     df = pd.read_excel(r"C:\Users\hely\Desktop\a.xlsx")
#     df.head()
#
#     print df.groupby('name')['ext price', 'quantity']
#
#     top_10 = (df.groupby('name')['ext price', 'quantity'].agg({'ext price': 'sum', 'quantity': 'count'})
#               .sort_values(by='ext price', ascending=False))[:10].reset_index()
#
#     print top_10
#     # if isinstance(top_10, frame.DataFrame):
#     #     print top_10.value
#
#     top_10.rename(columns={'name': 'Name', 'ext price': 'Sales', 'quantity': 'Purchases'}, inplace=True)
#     print top_10
#
#     fig, ax = plt.subplots()
#     top_10.plot(kind='barh', y="Sales", x="Name", ax=ax)
#     ax.set_xlim([-10000, 10000])
#     # ax.set_xlabel('Total Revenue')
#     # ax.set_ylabel('Customer')
#     # ax.set(title='2014 Revenue', xlabel='Total Revenue', ylabel='Customer')  同上操作
#
#     # Add a line for the average
#     avg = top_10['Sales'].mean()
#     ax.axvline(x=avg, color='b', label='Average', linestyle='--', linewidth=1)
#
#     # Annotate the new customers
#     for cust in [3, 5, 8]:
#         ax.text(115000, cust, "New Customer")
#
#     formatter = FuncFormatter(currency)
#     ax.xaxis.set_major_formatter(formatter)
#     # ax.legend().set_visible(False)
#
#     plt.show()
#
# def test3():
#     df = pd.read_excel(r"C:\Users\hely\Desktop\a.xlsx")
#     df.head()
#
#     print df.groupby('name')['ext price', 'quantity']
#
#     top_10 = (df.groupby('name')['ext price', 'quantity'].agg({'ext price': 'sum', 'quantity': 'count'})
#               .sort_values(by='ext price', ascending=False))[:10].reset_index()
#
#     print top_10
#     # if isinstance(top_10, frame.DataFrame):
#     #     print top_10.value
#
#     top_10.rename(columns={'name': 'Name', 'ext price': 'Sales', 'quantity': 'Purchases'}, inplace=True)
#     print top_10
#
#     # Get the figure and the axes
#     fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=(7, 4))
#     top_10.plot(kind='barh', y="Sales", x="Name", ax=ax0)
#     # ax0.set_xlim([-10000, 140000])
#     ax0.set(title='Revenue', xlabel='Total Revenue', ylabel='Customers')
#
#     # Plot the average as a vertical line
#     avg = top_10['Sales'].mean()
#     ax0.axvline(x=avg, color='b', label='Average', linestyle='--', linewidth=1)
#
#     # Repeat for the unit plot
#     top_10.plot(kind='barh', y="Purchases", x="Name", ax=ax1)
#     avg = top_10['Purchases'].mean()
#     ax1.set(title='Units', xlabel='Total Units', ylabel='')
#     ax1.axvline(x=avg, color='b', label='Average', linestyle='--', linewidth=1)
#
#     # Title the figure
#     fig.suptitle('2014 Sales Analysis', fontsize=14, fontweight='bold');
#
#     # Hide the legends
#     ax1.legend().set_visible(False)
#     ax0.legend().set_visible(False)
#
#     plt.show()
#
# # 格式化数据
# def currency(x, pos):
#     'The two args are the value and tick position'
#     if x >= 1000000:
#         return '${:1.1f}M'.format(x*1e-6)
#     return '${:1.0f}K'.format(x*1e-3)
#
#
# def pad_series():
#     s = pd.Series([1, 100, 2.12, 5, 9, 3, 50, 44, 22.16, 66])          # 索引从0 开始
#     print 'index', s.index
#     print 'values', s.values
#     print s.values[0]               # 通过索引访问
#     print s[0]                      # 同上
#     print 'type', type(s.values)
#     values = s.values
#     if isinstance(values, ndarray):
#         print values.round(2)            # 数字类型，四舍五入
#
#     # 自定义索引, 索引可以重复, dtype=int指定类型
#     print u'自定义索引'.center(100, '-')
#     s1 = pd.Series(data=[1, 2, 3, 4], index=['a', 'b', 'd', 'd'])
#     s2 = pd.Series(data=[1, 2, 3, 4], index=[1, 2, 3, 3])
#     print s1, s1.values
#     print 's1 index=', s1.index
#     print 's2 index=', s2.index
#     print '-'.center(100, '-')
#     aa = s1['d']   # 重复索引返回一个Series对象
#     print aa[0], aa[1],
#     print type(aa)
#     print '-'.center(100, '-')
#
#     # 字典初始化series对象
#     print u'字典初始化series对象'.center(100,'-')
#     sd = {'python': 9000, 'c++': 9001, 'c#': 9000}
#     s3 = pd.Series(sd)
#     print 's3.index', s3.index
#     print 's3.values', s3.values
#
#     # 数据和自定义索引自动对齐,应用于字典
#     print u'数据和自定义索引自动对齐'.center(100, '-')
#     s4 = pd.Series(sd, ['java', 'c++', 'c#'])
#     print s4
#     # 判断数据为空 pd.isnull 空返回true
#     print 'java is null ', pd.isnull(s4['java'])
#     print 'c++ is null ', pd.isnull(s4['c++'])
#     print pd.isnull(s4)
#     # Series对象isnull方法,同上
#     print u'Series对象isnull方法'.center(100, '-')
#     print 's4.isnull', s4.isnull()
#
#     # 对索引的名字，是可以从新定义的：
#     print u'对索引的名字，是可以从新定义的：'.center(100, '-')
#     print 'old index = ', s4.index
#     s4.index = ['a', 'b', 'c']
#     print 'new index = ', s4.index
#     print s4['a']
#     # Series 对象运算
#     print u'Series 对象运算'.center(100, '-')
#     s5 = s4 * 2           # 每个元素进行运算，并返回新的serial对象
#     print type(s5)
#     print s5
#     print s4
#
# def test_DataFrame():
#     # DataFrame
#     # DataFrame 是一种二维的数据结构，非常接近于电子表格或者类似 mysql 数据库的形式。
#     # 它的竖行称之为 columns，横行跟前面的 Series 一样，称之为 index，
#     # 也就是说可以通过 columns 和 index 来确定一个主句的位置。
#     # 定义一个 DataFrame 对象的常用方法——使用 dict 定义
#     # 字典的“键”（"name"，"marks"，"price"）就是 DataFrame 的 columns 的值（名称），
#     # 字典中每个“键”的“值”是一个列表，它们就是那一竖列中的具体填充数据
#     print 'DataFrame'.center(100, '-')
#     data = {"name": ['google', 'baidu', 'yahoo'], "marks": [100, 200, 300], "price": [1, 2, 3]}
#     # 上面的定义中没有确定索引，所以，按照惯例（Series 中已经形成的惯例）就是从 0 开始的整数。
#     # 从上面的结果中很明显表示出来，这就是一个二维的数据结构（类似 excel 或者 mysql 中的查看效果）。
#     f1 = pd.DataFrame(data)
#     print f1
#     # print type(f1.values)
#     # print type(f1.values[0])
#     print 'values=',f1.values                # numpy.ndarray类型
#     print f1.columns                      # 列名称
#     print u'获取一列数据'
#     print f1['name']                         # 获取一列数据(eg:获取name列数据)
#     # DataFrame columns 顺序可以被规定
#     print u'DataFrame columns 顺序可以被规定 '.center(100, '-')
#     f1 = pd.DataFrame(data, columns=['name', 'price', 'marks'])
#     print f1
#     # DataFrame 数据的索引也能够自定义
#     print u'DataFrame 数据的索引也能够自定义'.center(100,'-')
#     f1 = pd.DataFrame(data, index=['a','b','c'])
#     print f1
#
#     print u'下面操作是给同一列赋值'
#     newdata1 = {'username': {'first': 'wangxing', 'second': 'dadiao'}, 'age': {'first': 24, 'second': 25}}
#     f6 = pd.DataFrame(newdata1, columns=['username', 'age', 'sex'])
#     print f6
#     print u"f6['sex']赋值"
#     f6['sex'] = 'man'          # 对一列赋值(列中所有元素都统一成man)
#     print f6
#     # 列数据单独赋值， 一列是serial对象，可初始化serial对象后赋值
#     sex_value = pd.Series(['男','女'], index=['first','second'])
#     f6['sex'] = sex_value  # 对一列赋值
#     print f6
#
#     # 获取前n行
#     print u'获取前n行,f6.head(n)'.center(100,'-')
#     # 获取尾部n行
#     print u'获取尾部n行,f6.tail(n)'.center(100,'-')
#     print u'数据长度 len(f6'.center(100,'-')
#     print len(f6)
#     print u"获取一列数据,两种方式 1.通过列名，如f6['username'], 2.直接通过列名,如f6.username".center(100,'-')
#     print f6.username
#
#     print u'列中使用条件表达式, 返回新的 Series对象'.center(100,'-')
#     d = f6.age > 24
#     print type(d)
#     print d
#     print u'使用多条条件表达式来进行过滤, 返回DataFrame对象'.center(100,'-')
#     d = f6[(f6.age>24) & (f6.age == 25)]
#     print type(d)
#     print d
#
#     print u'DataFrame 行操作'.center(100, '-')
#     ddd = f6.iloc(0)   # 数字索引
#     print ddd, type(ddd)
#     print type(ddd[0]), ddd[0][1]


# csv文件处理
def test_csv():
    print u'csv文件处理'.center(100,'-')
    power_datas = pd.read_csv(r'.\dut1_power.csv')
    print type(power_datas)
    print u'维度', power_datas.shape, u'行数，列数', u'不包含表头'
    print u'数据表基本信息（维度、列名称、数据格式、所占空间等）'.center(100, '-')
    print power_datas.info()
    print u'每一列数据的格式'.center(100, '-')
    dttyes = power_datas.dtypes
    print 'pandas.core.series.Series ->', type(dttyes)
    print dttyes
    print dttyes['pos']
    print u'空值 isnull()'.center(100, '-')
    # print power_datas.isnull()
    print u'查看数据表的值 power_datas.values'.center(100, '-')
    print power_datas.values
    print u'查看列名称'.center(100, '-')
    p_columns = power_datas.columns
    print p_columns
    print 'index = 0', p_columns[0]
    print u'查看前10行数据'.center(100, '-')
    print power_datas.head(10)
    print u'查看后10行数据'.center(100, '-')
    print power_datas.tail(10)
    print u'获取一列数据'.center(100, '-')
    pos_col = power_datas['pos']
    print type(pos_col)
    print pos_col.head(10)
    print u'空数据替换 fillna, 并生成新的dataframe对象'.center(100, '-')
    new_datas = power_datas.fillna(value=1)
    print new_datas.tail(10)
    print u'下面是原数据'.center(100, '-')
    print power_datas.tail(10)
    print u'使用列prince的均值对NA进行填充, df[‘prince’].fillna(df[‘prince’].mean())'.center(100, '-')
    print u'清除city字段的字符空格 df[‘city’]=df[‘city’].map(str.strip)'.center(100, '-')
    print u'大小写转换 df[‘city’]=df[‘city’].str.lower()'.center(100, '-')
    print u'更改数据格式 df[‘price’].astype(‘int’) '.center(100, '-')
    print u'更改列名称 df.rename(columns={‘category’: ‘category-size’}) '.center(100, '-')
    print u'删除后出现的重复值 f[‘city’].drop_duplicates()'.center(100, '-')
    print u'删除先出现的重复值 df[‘city’].drop_duplicates(keep=’last’)'.center(100, '-')
    print u'数据替换 df[‘city’].replace(‘sh’, ‘shanghai’)'.center(100, '-')
    print u'数据表合并 merge'.center(100,'-')
    df = pd.DataFrame({"id": [1001, 1002, 1003, 1004, 1005, 1006],
                       "date": pd.date_range('20130102', periods=6),
                       "city": ['Beijing', 'Beijing', 'guangzhou', 'Shenzhen', 'shanghai', 'BEIJING'],
                       "age": [23, 44, 54, 32, 34, 32],
                       "category": ['100-A', '100-B', '110-A', '110-C', '210-A', '130-F'],
                       "price": [1200, np.nan, 2133, 5433, np.nan, 4432]},
                      columns=['id', 'date', 'city', 'category', 'age', 'price'])
    df1 = pd.DataFrame({"id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
                        "gender": ['male', 'female', 'male', 'female', 'male', 'female', 'male', 'female'],
                        "pay": ['Y', 'N', 'Y', 'Y', 'N', 'Y', 'N', 'Y', ],
                        "m-point": [10, 12, 20, 40, 40, 40, 30, 20]})
    print df
    print df1
    print u"df_inner=pd.merge(df,df1,how='inner') 匹配合并，交集".center(100, '-')
    df_inner = pd.merge(df, df1, how='inner')  # 匹配合并，交集
    print df_inner
    print u"df_left=pd.merge(df,df1,how='left')".center(100, '-')
    df_left = pd.merge(df, df1, how='left')
    print df_left
    print u"df_right=pd.merge(df,df1,how='right')".center(100, '-')
    df_right = pd.merge(df, df1, how='right')
    print df_right
    print u"df_outer=pd.merge(df,df1,how='outer')  #并集".center(100, '-')
    df_outer = pd.merge(df, df1, how='outer')  # 并集
    print df_outer
    print u'append 添加到集合'.center(100, '-')
    print df.append(df1)
    print u'join 连接'.center(100, '-')
    print u'数据提取'.center(100, '-')
    print u'按索引提取单行的数值,loc,iloc和ix，loc函数按标签值进行提取，iloc按位置进行提取，ix可以同时按标签和位置进行提取'.center(100, '-')
    print df_inner.loc[3]
    print u'按索引提取区域行数值'.center(100, '-').center(100, '-')
    print df_inner.iloc[0:1]
    print u'重设索引 reset_index'.center(100, '-')
    print u'设置日期为索引 df_inner=df_inner.set_index(‘date’) '.center(100, '-')
    df_inner = df_inner.set_index('date')
    print df_inner
    print u'提取4日之前的所有数据'.center(100, '-')
    print df_inner[:'2013-01-04']
    print u'使用iloc按位置区域提取数据'.center(100, '-')
    print df_inner.iloc[:3, :2]  # 冒号前后的数字不再是索引的标签名称，而是数据所在的位置，从0开始，前三行，前两列。
    print df_inner.iloc[0, 1]   # 第1行，第2列
    print u'适应iloc按位置单独提起数据'.center(100, '-')
    print df_inner.iloc[[0, 2, 5], [4, 5]]  # 提取第0、2、5行，4、5列
    print u'使用ix按索引标签和位置混合提取数据'.center(100, '-')
    print df_inner.ix[:'2013-01-03', :4]        # 2013-01-03号之前，前四列数据
    print u'判断city列的值是否为北京, 字符串判断'.center(100, '-')
    print df_inner['city'].isin(['beijing'])
    print u'判断city列里是否包含beijing和shanghai，然后将符合条件的数据提取出来'.center(100, '-')
    print df_inner.loc[df_inner['city'].isin(['beijing', 'shanghai'])]
    print u'数据筛选'.center(100, '-')
    print df
    print u'使用与、或、非三个条件配合大于、小于、等于对数据进行筛选，并进行计数和求和'
    print u'1、使用“与”进行筛选'.center(100, '-')
    print df.loc[(df['age'] > 25) & (df['city'] == 'Beijing'), ['id', 'city', 'age']]
    print u'2、使用“或”进行筛选'.center(100, '-')
    print df.loc[(df['age'] > 25) | (df['city'] == 'Beijing'), ['id', 'city', 'age']]
    print u'3、使用“非”条件进行筛选'.center(100, '-')
    print df.loc[(df['city'] != 'Beijing'), ['id', 'city', 'age']]
    print u'4、对筛选后的数据按city列进行计数'.center(100, '-')
    print 'count=', df.loc[(df['city'] == 'Beijing'), ['id', 'city', 'age']].city.count()
    print u'5、使用query函数进行筛选, 参数为表达式'.center(100, '-')
    print df.query('city == ["Beijing", "shanghai"]')
    print df.query('age > 40')
    print u'对筛选后的结果按price进行求和'.center(100, '-')
    print 'price sum = ', df.query('age > 40').price.sum()
    print u'数据汇总, 主要函数是groupby和pivote_table '.center(100, '-')
    print u'1、对所有的列进行计数汇总'.center(100, '-')
    print df.groupby('city').count()
    print u'2、按城市对id字段进行计数'.center(100, '-')
    print df.groupby('city')['id'].count()
    print u'3、对两个字段进行汇总计数'.center(100, '-')
    print df.groupby(['city', 'age'])['id'].count()
    print u'4、对city字段进行汇总，并分别计算prince的合计和均值'.center(100, '-')
    print type(df_inner.groupby('city'))
    print df_inner.groupby('city')['price'].agg([len, np.sum, np.mean])


if __name__ == '__main__':
    test_csv()
    # pad_series()
    # test_DataFrame()