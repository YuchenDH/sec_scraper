def str_to_lines(f):
    content = f.split('\n')
    content = [x.strip() for x in content]
    return content


def lines_to_dict(content):
    fieldpos = None
    stoppoint = None
    results = []
    for idx, line in enumerate(content):
        if line[0:7] == 'Company':
            fieldpos = line.find('Fo')
            if not fieldpos:
                raise ValueError('No column name found')
            stoppoint = idx
            break

    content = content[stoppoint+3:]

    for line in content:
        companyname = line[:fieldpos]
        fields = line[fieldpos:].split(" ")
        fields = [x.strip() for x in fields if x != '']
        if fields and fields[0] == 'D':
            obj = {
                'company': companyname.strip(),
                'form_type': fields[0],
                'CIK': fields[1],
                'date_filed': fields[2],
                'file_name': fields[3]
                }
            results.append(obj)
    return results


def read_file(f):
    content = str_to_lines(f)
    return lines_to_dict(content)


def main():
    import sys
    try:
        lines = str_to_lines(sys.argv[1])
        data = lines_to_dict(lines)
        for item in data:
            print item['file_name']
        
    except:
        raise
    return


if __name__ == '__main__':
    main()
    
