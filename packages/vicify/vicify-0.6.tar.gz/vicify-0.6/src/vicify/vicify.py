import pandas as pd

def convert(filename):
    files = pd.read_csv(filename)
    phones = files.Phones.tolist()
    names = files.Names.tolist()
    f = open('contacts.vcf', 'w')
    for i in range(len(names)):
        vcf_string_3 = "BEGIN:VCARD"+ "\nVERSION:3.0\n" + "FN:" + str(names[i])  + "\n" + "N:"+ str(names[i]) + ";;;" +"\n" + "TEL;TYPE=CELL:"+ "+91 "+str(phones[i]) + "\n" +"CATEGORIES:myContacts" "\n"  + "END:VCARD" + "\n"
        vcf_string_4 = "BEGIN:VCARD"+ "\nVERSION:4.0\n" + "FN:" + str(names[i])  + "\n" + "N:"+ str(names[i]) + ";;;" +"\n" + "TEL;TYPE=CELL:"+ "+91 "+str(phones[i]) + "\n" +"CATEGORIES:myContacts" "\n"  + "END:VCARD" + "\n"
        f.write(vcf_string_3)
    