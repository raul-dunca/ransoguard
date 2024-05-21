import ast
"""
This script transform the dictionary from (Filename,label) (key,value) pairs
to (label,cnt) where cnt is the nr of labels present
"""

def sort_and_print_dictionary(dictionary):
    labels_cnt={}
    for key in dictionary:
        if dictionary[key] in labels_cnt:
            labels_cnt[dictionary[key]]+=1
        else:
            labels_cnt[dictionary[key]] = 1

    return labels_cnt

if __name__ == "__main__":
    with open('label_class.txt', 'r',  encoding="utf-8") as file:
        file_content = file.read()
    data_dict =  ast.literal_eval(file_content)
    label_count=sort_and_print_dictionary(data_dict)

    sum=0
    for key in label_count:
        if label_count[key]==1:
            print(key)
        sum+=label_count[key]
    print(sum)

    sorted_data = dict(sorted(label_count.items(), key=lambda item: item[1], reverse=True))
    #print(str(data_dict))
    with open("cnt.txt", "w+", encoding="utf-8") as f:
        # Write the dictionary to the file
        f.write(str(sorted_data))