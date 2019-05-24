# -*- coding: UTF-8 -*-

import os


# csv文件处理
class CSVHelper(object):
    def __init__(self, file_ptah, header=None):
        self.message = ''
        self.create_csv(file_ptah, header)

    # 创建新的csv文件
    # 如果改文件是新创建文件，并且header有值，将header写入文件
    def create_csv(self, file_ptah, header=None):
        self.csv_path = file_ptah
        if self.csv_path is not None and len(file_ptah) > 0 and not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w') as fp:
                if header is not None:
                    if isinstance(header, list) or isinstance(header, tuple):
                        datas_str = ''
                        for data in header:
                            datas_str += str(data) + ','
                        fp.write(datas_str + '\n')
                    else:
                        fp.write(header + '\n')
                self.message = 'create {0} file'.format(file_ptah)

    # 写入一行数据
    # 参数可以是字符串或是字符串列表
    def write(self, datas):
        if self.csv_path is None and len(self.csv_path) == 0:
            self.message = 'file path is empty'
            return False
        if datas is None or len(datas) == 0:
            self.message = 'datas is empty'
            return False

        with open(self.csv_path, 'a+') as fp:
            if isinstance(datas, list) or isinstance(datas, tuple):
                datas_str = ''
                for data in datas:
                    datas_str += str(data) + ','
                fp.write(datas_str + '\n')
            else:
                fp.write(datas + '\n')
            self.message = 'write data finished'

        return True

    # 写多行数据
    # 参数可以是列表，但列表中的数据必须是字符串数据
    def writeLines(self, datas):
        if self.csv_path is None and len(self.csv_path) == 0:
            self.message = 'file path is empty'
            return False
        if datas is None or len(datas) == 0:
            self.message = 'datas is empty'
            return False

        with open(self.csv_path, 'a+') as fp:
            fp.writelines(datas)
            self.message = 'write data finished'

        return True

    # 写多行数据
    # 参数是可以是列表，同时列表中的数据可以是列表
    def writeList(self, data_list):
        if self.csv_path is None and len(self.csv_path) == 0:
            self.message = 'file path is empty'
            return False
        if data_list is None or len(data_list) == 0:
            self.message = 'datas is empty'
            return False

        with open(self.csv_path, 'a+') as fp:
            if isinstance(data_list, list) or isinstance(data_list, tuple):
                for datas in data_list:
                    if isinstance(datas, list) or isinstance(datas, tuple):
                        datas_str = ''
                        for data in datas:
                            datas_str += str(data) + ','
                        fp.write(datas_str + '\n')
                    else:
                        fp.write(datas + '\n')
            else:
                fp.write(data_list + '\n')
            self.message = 'write data finished'

        return True

    # 读文件数据, 未实现
    def read(self):
        raise NotImplementedError()


if __name__ == "__main__":
    csv = CSVHelper('.\\a.csv')
    csv.write('h1,h2,h3,h3,h5')
    csv.write([1,2,3,4,5])
    csv.write((11,22,33,44,55))