path = 'tmp.txt'

with open(path, 'r', encoding='utf8') as f:
    for line in f:
        line_list = line.strip().split(' ')
        package, level = line_list[0], line_list[-1]
        package = package.strip()
        if int(level) == 1:
            print(f'\"{package}\",')
