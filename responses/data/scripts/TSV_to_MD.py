import csv
import time

def writeToMD(to):
    fileLoc="../../../docs/_posts/"
    filename=to[2]+".MD"
    F=open(fileLoc+filename,"w")
    F.write("---\n")
    F.write("layout: post\n")
    F.write("title: \""+to[1]+"\"\n")
    F.write("date: "+to[2]+"\n")
    F.write("nav: post\n")
    F.write("category: "+to[0]+"\n")
    F.write("tags: ["+to[3]+"]\n")
    F.write("---\n\n")
    F.write("* content\n")
    F.write("{:toc}\n\n")
    F.write(to[4]+"\n")
    F.write("<!-- more -->\n")
    F.write("<p>"+to[5]+"</p>\n")
    F.close()


if __name__ == "__main__":


    tids={"2804":"CSC258","4045":"CSC108", "4649":"CSC209","5349":"Unknow","5502":"CSC148", "7467":"CSC209", "7493":"CSC258"}

    with open("../data/2018_04_13.posts.tsv") as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        toWrite=[None]*6 #[tid,subject,dateline,tags,firstline of message, the rest of the text]
        toWrite[5]=""

        count=0
        for line in tsvreader:
            if line[0].isdigit():
                if count !=0:
                    writeToMD(toWrite); # write all the previous data before parseing the new lines
                    toWrite=[None]*6
                    toWrite[5]=""

                count=count+1
                toWrite[0]=tids[line[1]] #What course its from
                toWrite[1]=line[4] #subject of the thread, this might need to be worked on
                toWrite[2]=( time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(int(line[8])))) #time
                toWrite[3]=line[1] #should be 18 with a fully taged dataset breaks other wise
                toWrite[4]=line[9]

            else:
                toWrite[5]=toWrite[5]+line[0]






