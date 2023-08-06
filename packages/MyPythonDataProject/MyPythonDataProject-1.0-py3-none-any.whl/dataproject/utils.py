"""Import necessary modules"""
from pathlib import Path
import csv
import dataproject.identifier as identifier


def files(input_file, input_file2):
    """Takes file name or path and returns two Path objects"""
    path1 = Path(input_file)
    path2 = Path(input_file2)
    file_type = identifier.identifier(path1, path2)
    return path1, path2, file_type


def datacsv(path1, path2):
    """Instructions for csv files"""
    with open(path1, 'r', encoding="utf-8") as file:
        document = file.read().split(",")
        with open(path2, 'r', encoding="utf-8") as file2:
            document2 = file2.read().split(",")
            return document, document2


def datadat(path1, path2):
    """Instructions for dat files"""
    with open(path1, 'r', encoding="utf-8") as file:
        document = file.read().split(" ")
        with open(path2, 'r', encoding="utf-8") as file2:
            document2 = file2.read().split(" ")
            return document, document2


def datajson(path1, path2):
    """Instructions for json files"""
    with open(path1, 'r', encoding="utf-8") as file:
        document = file.read()
        semiclean = document.replace("[", "")
        clean = semiclean.replace("]", "")
        semifinal = clean.replace("}", "")
        final = semifinal.replace("{", "")
        with open(path2, 'r', encoding="utf-8") as file2:
            document2 = file2.read()
            semiclean2 = document2.replace("[", "")
            clean2 = semiclean2.replace("]", "")
            semifinal2 = clean2.replace("}", "")
            final2 = semifinal2.replace("{", "")
            return final.split(","), final2.split(",")


def exporter(input1, input2, output, filename, export_path=''):
    """Exports file"""
    with open(export_path+filename+".csv", 'w', encoding='UTF-8') as exported:
        write = csv.writer(exported, delimiter=',', quotechar='|')
        write.writerow(["First Set:"])
        write.writerow("")
        for row in input1:
            write.writerow([row])
        write.writerow(["*"*250])
        write.writerow(["Second Set:"])
        write.writerow("")
        for row in input2:
            write.writerow([row])
        write.writerow(["*"*250])
        write.writerow(["Final set:"])
        write.writerow("")
        for row in output:
            write.writerow([row])
