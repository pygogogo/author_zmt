def strFormatNum(num_format):
    new_num = 0
    try:
        if '亿' in num_format:
            new_num = float(num_format.replace('亿', ''))
            new_num = new_num * 100000000
            new_num = int(new_num)
            # return new_num
        elif 'w' in num_format:
            new_num = float(num_format.replace('w', ''))
            new_num = new_num * 10000
            new_num = int(new_num)
            # return new_num
        elif '万' in num_format:
             new_num = float(num_format.replace('万', ''))
             new_num = new_num * 10000
             new_num = int(new_num)
        else:
            new_num = int(num_format)
            # return new_num
    except Exception as e:
        print(e)
    finally:
        return new_num

if __name__ == '__main__':
   a = strFormatNum('1万')
   print( a)