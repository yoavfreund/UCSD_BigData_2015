import re
file=open(dir+'/Moby-Dick.txt','r')
hash_list=[] # a table that holds the min-hash sketch for each paragraph
offset_list=[] # a table that holds the offset to the start of each paragraph.

count=0
paragraph=''
minhash=MinHash()
line_offset=0
paragraph_start_offset=0
for line in file.readlines():
    if len(line)<3:   # found end of paragraph
        if len(paragraph)>50:  # ignore paragraphs shorter than 50 chars
            offset_list.append(paragraph_start_offset)
            words=re.split('\W+',paragraph)
            words=[word.lower() for word in words]
            hash_list.append(minhash.Compute_sketch(words))
        paragraph_start_offset=line_offset+len(line)
    if count % 1000==0:
        print count,line_offset,len(offset_list),len(hash_list)
    count += 1
    line_offset += len(line)
            
