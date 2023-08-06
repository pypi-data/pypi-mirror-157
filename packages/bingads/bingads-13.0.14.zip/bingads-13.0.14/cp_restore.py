import sys
sys.stdout.reconfigure(encoding='utf-8')
import re


def main(input, output):
    rule = r'^(\d*),(\d*),(\d*),(.*),(.*)$'
    file_in = "E:\\cp\\test.csv"
    file_out = "E:\\cp\\out.csv"
    out = open(output, "w", encoding='utf-8')
    with open(input, encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            pattern = re.compile(rule, re.IGNORECASE)
            m = pattern.match(line)
            if m:
                out.write('UPDATE [AdExtensionItem] SET Properties = N\'%s\' WHERE AccountID = %s AND AdExtensionId = %s AND AdExtensionItemId = %s AND ModifiedByUserId = -14;\n' % (
                          m.group(4).replace("'", "''"), # handle the '
                          m.group(1),
                          m.group(2),
                          m.group(3))
                          )
    pass

# Main execution
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])