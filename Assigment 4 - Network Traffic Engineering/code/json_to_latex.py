# coding=utf-8
import os


class JsonToLatex:

    def __init__(self, json, title=""):
        self.json = json
        self.csv = ""
        self.final = ""
        self.title = title

    def convert_to_csv(self):
        tmp = ""
        keys = self.json[0].keys()
        tmp += ",".join(keys) + "\n"
        self.csv = tmp

        for l in self.json:
            for v in l.itervalues():
                self.csv += "\"" + str(v) + "\"" + ","
            self.csv = self.csv[:-1]
            self.csv += "\n"
        self.csv = self.csv[:-1]

    def save(self, path):
        with open(path, "w") as outfile:
            outfile.write(self.final)

    def table(self, header, body):
        self.final += """\\begin{table}[!htb]
        \centering
        \\resizebox{\\textwidth}{!}{\\begin{tabular}{"""

        for i in range(0, len(header.split(","))):
            self.final += "|l"

        self.final += "|}\n\hline\n"

        for row in header.split(","):
            self.final += ("\multicolumn{1}{|c|}{\\textbf{%s}}" % row) + " & "

        self.final = self.final[:-3] + " \\\\ \hline\n"

        for l in body:
            for w in l.split("\","):
                self.final += "%s & " % w.replace("\"", "")

            self.final = self.final[:-2] + "\\\\ \hline\n"

        self.final += "\end{tabular}}\n\caption[]{" + self.title + "}\n\end{table}\n\n"

    def convert(self):
        self.convert_to_csv()
        str_csv_contents = self.csv

        list_csv_rows = str_csv_contents.split('\n')

        lines_max = 30

        i = 1
        while len(list_csv_rows) > i:
            self.table(list_csv_rows[0], list_csv_rows[i:i+lines_max])
            i += lines_max

        # print final
        return self.final
