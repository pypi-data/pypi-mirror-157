import pandas as pd
import openpyxl
import warnings
from IPython.display import display
import formulas
import numpy as np
from win32com import client
import matplotlib.pyplot as plt
import os
import formulas
from pathlib import Path
import dataframe_image as dfi
import aspose.words as aw
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
from scipy import stats
from statsmodels.stats.weightstats import ztest
import imp
import wget

#help function stat test explanation
class dataFile():
    
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
    
    def __init__(self, path):
        test, ph, au=imp.find_module('Results_Analysis')
        self.to_mod=ph
        wget.download('https://docs.google.com/spreadsheets/d/1Z_KnyxvX2xT2ukVqfle70VLRJl1SnmY2/export?format=xlsx', self.to_mod+'\Short_UEQ_Data_Analysis_Tool.xlsx')

        self.resPath = str(os.path.join(self.to_mod, "resExcel", "DATAUPDATES.XLSX"))
        self.processing(path)
        
        

    def processing(self, path):
        compt=0
        row, column=4, 'A'
        
        #Quantitative analysis
        self.mentLoad,self.mentLoadSuccess, av=[[]],[[]], 0
        self.softUs, self.softUsInfo, self.softUsInterface, self.com1=[[]], [[]], [[]], [[],[],[],[]]
        self.PreSearch, self.ContentSelection, self.InteractionContent, self.PostSearch = [[]], [[]], [[]], [[]]
        self.KnowledgeGain=[[]]      
        
        #Qualitative analysis
        self.hedonicQual, self.pragmaticQual=[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]],[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.mentloadQual=[[0,0,0,0,0,0], [0,0,0,0,0,0],[0,0,0,0,0,0]]
        self.knowledgeGainQual=[[0,0,0],[0,0,0],[0,0,0]]
        self.PreSearchQual, self.ContentSelectionQual, self.InteractionContentQual, self.PostSearchQual=[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.softUs_SystemQual, self.softUs_InformationQual,self.softUs_InterfaceQual=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]], [[0,0,0,0],[0,0,0,0],[0,0,0,0]], [[0,0,0],[0,0,0],[0,0,0]]
        
        
        
        print("loading file...")
        #openning files
        pathDown=self.to_mod+'\Short_UEQ_Data_Analysis_Tool.xlsx'
        xfile = openpyxl.load_workbook(pathDown)
        sheet = xfile['Data']
        df = pd.read_excel(path)
        df = df.to_dict()
        
        print("calculating results...")
        #I loop throught all the data and separates them or their calculated mean into different tabs
        for i in df:
            
            compt=compt+1
            
            if compt==2:
                for j in df[i]:self.com1[0].append(df[i].get(j))
        
            #UX
            #I insert every data of those 8 questions into the nasa form
            if 44<=compt<=51:
                
                for j in df[i]:
                    if compt-44<4:
                        if df[i].get(j)>4:
                            self.pragmaticQual[0][compt-44]=self.pragmaticQual[0][compt-44]+1
                        elif 3<=df[i].get(j)<=4:
                            self.pragmaticQual[1][compt-44]=self.pragmaticQual[1][compt-44]+1
                        else:
                            self.pragmaticQual[2][compt-44]=self.pragmaticQual[2][compt-44]+1
                        
                        
                    else:
                        if df[i].get(j)>4:
                            self.hedonicQual[0][compt-48]=self.hedonicQual[0][compt-48]+1
                        elif  3<=df[i].get(j)<=4:
                            self.hedonicQual[1][compt-48]=self.hedonicQual[1][compt-48]+1
                        else:
                            self.hedonicQual[2][compt-48]=self.hedonicQual[2][compt-48]+1
                            
                            
                    cell=column+str(row)
                    sheet[cell] = df[i].get(j)
                    row+=1
                newCol=ord(column[0])
                newCol+=1
                column=chr(newCol)
                row=4
                
            #Cognitive Load
            #I do an average of all the data and store the result into a list
            if 52<=compt<=57:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.mentloadQual[0][compt-52]=self.mentloadQual[0][compt-52]+1
                    elif 3<=df[i].get(j)<=4:
                        self.mentloadQual[1][compt-52]=self.mentloadQual[1][compt-52]+1
                    else:
                        self.mentloadQual[2][compt-52]=self.mentloadQual[2][compt-52]+1
                if compt==55 or compt==57:
                    for j in df[i]:av+=df[i].get(j)
                    av=av/len(df[i])
                    self.mentLoadSuccess[0].append(av)
                    av=0
                else:
                    for j in df[i]:av+=df[i].get(j)
                    av=av/len(df[i])
                    self.mentLoad[0].append(av)
                    av=0
                
            #Software usabilities
            #part system
            if  58<=compt<=62 or compt==73:
                if compt!=73:
                    for j in df[i]:
                        if df[i].get(j)>4:
                            self.softUs_SystemQual[0][compt-58]=self.softUs_SystemQual[0][compt-58]+1
                        elif 3<=df[i].get(j)<=4:
                            self.softUs_SystemQual[1][compt-58]=self.softUs_SystemQual[1][compt-58]+1
                        else:
                            self.softUs_SystemQual[2][compt-58]=self.softUs_SystemQual[2][compt-58]+1
                        av+=df[i].get(j)
                else:
                    for j in df[i]:
                        if df[i].get(j)>4:
                            self.softUs_SystemQual[0][5]=self.softUs_SystemQual[0][5]+1
                        elif 3<=df[i].get(j)<=4:
                            self.softUs_SystemQual[1][5]=self.softUs_SystemQual[1][5]+1
                        else:
                            self.softUs_SystemQual[2][5]=self.softUs_SystemQual[2][5]+1
                        av+=df[i].get(j)
                    
                av=av/len(df[i])
                self.softUs[0].append(av)
                av=0
                
                
            #part information
            if 64<=compt<=67:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.softUs_InformationQual[0][compt-64]=self.softUs_InformationQual[0][compt-64]+1
                    elif 3<=df[i].get(j)<=4:
                        self.softUs_InformationQual[1][compt-64]=self.softUs_InformationQual[1][compt-64]+1
                    else:
                        self.softUs_InformationQual[2][compt-64]=self.softUs_InformationQual[2][compt-64]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.softUsInfo[0].append(av)
                av=0
            
            #commentaire
            if compt==68:
                for j in df[i]:self.com1[2].append(df[i].get(j))
            if compt==63:
                for j in df[i]:self.com1[1].append(df[i].get(j))
            if compt==72:
                for j in df[i]:self.com1[3].append(df[i].get(j))
                
            #part interface
            if 69<=compt<=71:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.softUs_InterfaceQual[0][compt-69]=self.softUs_InterfaceQual[0][compt-69]+1
                    elif 3<=df[i].get(j)<=4:
                        self.softUs_InterfaceQual[1][compt-69]=self.softUs_InterfaceQual[1][compt-69]+1
                    else:
                        self.softUs_InterfaceQual[2][compt-69]=self.softUs_InterfaceQual[2][compt-69]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.softUsInterface[0].append(av)
                av=0
                
            #Searching as learning

            #Pre-Search
            if 74<=compt<=76:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.PreSearchQual[0][compt-74]=self.PreSearchQual[0][compt-74]+1
                    elif 3<=df[i].get(j)<=4:
                        self.PreSearchQual[1][compt-74]=self.PreSearchQual[1][compt-74]+1
                    else:
                        self.PreSearchQual[2][compt-74]=self.PreSearchQual[2][compt-74]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.PreSearch[0].append(av)
                av=0
                
            #Content Selection
            if 77<=compt<=81:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.ContentSelectionQual[0][compt-77]=self.ContentSelectionQual[0][compt-77]+1
                    elif 3<=df[i].get(j)<=4:
                        self.ContentSelectionQual[1][compt-77]=self.ContentSelectionQual[1][compt-77]+1
                    else:
                        self.ContentSelectionQual[2][compt-77]=self.ContentSelectionQual[2][compt-77]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.ContentSelection[0].append(av)
                av=0
            
            #Interaction with content
            if 82<=compt<=85:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.InteractionContentQual[0][compt-82]=self.InteractionContentQual[0][compt-82]+1
                    elif 3<=df[i].get(j)<=4:
                        self.InteractionContentQual[1][compt-82]=self.InteractionContentQual[1][compt-82]+1
                    else:
                        self.InteractionContentQual[2][compt-82]=self.InteractionContentQual[2][compt-82]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.InteractionContent[0].append(av)
                av=0
            
            
            #Post-Search
            if 86<=compt<=89:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.PostSearchQual[0][compt-86]=self.PostSearchQual[0][compt-86]+1
                    elif 3<=df[i].get(j)<=4:
                        self.PostSearchQual[1][compt-86]=self.PostSearchQual[1][compt-86]+1
                    else:
                        self.PostSearchQual[2][compt-86]=self.PostSearchQual[2][compt-86]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.PostSearch[0].append(av)
                av=0
            
            #Knowledge gain
            if 90<=compt<=92:
                for j in df[i]:
                    if df[i].get(j)>4:
                        self.knowledgeGainQual[0][compt-90]=self.knowledgeGainQual[0][compt-90]+1
                    elif 3<=df[i].get(j)<=4:
                        self.knowledgeGainQual[1][compt-90]=self.knowledgeGainQual[1][compt-90]+1
                    else:
                        self.knowledgeGainQual[2][compt-90]=self.knowledgeGainQual[2][compt-90]+1
                    av+=df[i].get(j)
                    
                av=av/len(df[i])
                self.KnowledgeGain[0].append(av)
                av=0    
            
                
        print("converting data...")
        spreadsheet=self.to_mod+'\DataUpdates.xlsx'
        xfile.save(spreadsheet)

        fpath = spreadsheet
        dirname = str(os.path.join(self.to_mod, "resExcel"))
        xl_model = formulas.ExcelModel().loads(fpath).finish()
        xl_model.calculate()
        xl_model.write(dirpath=dirname)
        print("task complete")
        
        
       
    #User Experience  
    def dt(self, save='display'):
        df = pd.read_excel(self.resPath, sheet_name='DT')
        df = df.head(10).style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                             {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },

                        ])
        display(df)
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[2]
            #.head()
            path=str(os.path.join(Path.home(), "Downloads", "dt.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")
        
    def confidence_Intervals(self, save='display'):
        df = pd.read_excel(self.resPath, sheet_name='CONFIDENCE_INTERVALS')
        df = df.head(10).style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                             {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row1",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row2",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },

                        ])
        display(df)
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[4]
            path=str(os.path.join(Path.home(), "Downloads", "confidence_Intervals.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")
        
    def scale_Consistency(self, save='display'):
        df = pd.read_excel(self.resPath, sheet_name='SCALE_CONSISTENCY')
        df = df.head(10).style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                             {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;text-align: center;"
                            },
                            {
                                "selector":".row1",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row2",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },

                        ])
        display(df)
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[5]
            path=str(os.path.join(Path.home(), "Downloads", "scale_Consistency.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")

    def inconsistencies(self, save='display'):
        df = pd.read_excel(self.resPath, sheet_name='INCONSISTENCIES')
        df = df.style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                             {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row1",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },

                        ])
        display(df)
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[7]
            path=str(os.path.join(Path.home(), "Downloads", "inconsistencies.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")

    def benchmark(self, save='display'):
        df = pd.read_excel(self.resPath, sheet_name='BENCHMARK')
        tempDf =df
        df = df.head(10).style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                             {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row1",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },

                        ])
        display(df)
        plt.rcParams['figure.figsize'] = [8,5]

        cat = [tempDf.iloc[i,0] for i in range(24, 27)]
        line=[tempDf.iloc[i,7] for i in range(24, 27)]
        Excellent = np.array([tempDf.iloc[i,6] for i in range(24, 27)])
        Good = np.array([tempDf.iloc[i,5] for i in range(24, 27)])
        Above_average = np.array([tempDf.iloc[i,4] for i in range(24, 27)])
        Below_average = np.array([tempDf.iloc[i,3] for i in range(24, 27)])
        Bad = np.array([tempDf.iloc[i,2] for i in range(24, 27)])
        Lower_Border = np.array([tempDf.iloc[i,1] for i in range(24, 27)])
        ind = [x for x, _ in enumerate(cat)]

        plt.bar(ind, Excellent, width=0.8, label='Excellent', color='#3EBA24', bottom=Good+Above_average+Below_average+Bad)
        plt.bar(ind, Good, width=0.8, label='Good', color='#8EFA78', bottom=Above_average+Below_average+Bad)
        plt.bar(ind, Above_average, width=0.8, label='Above average', color='#73C362', bottom=Below_average+Bad)
        plt.bar(ind, Below_average, width=0.8, label='Below average', color='#EBC63C', bottom=Bad)
        plt.bar(ind, Bad, width=0.8, label='Bad', color='#E8281F')
        plt.bar(ind, Lower_Border, width=0.8, color='#E8281F')
        plt.plot(line, color='black',marker='o' ,ms=5)

        plt.xticks(ind, cat)
        plt.legend(loc="upper right")

        plt.show()
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[6]
            path=str(os.path.join(Path.home(), "Downloads", "benchmark.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")
        

    def results(self, save='display'):

        df = pd.read_excel(self.resPath, sheet_name='RESULTS')
        tempDf =df
        df = df.head(10).style.format(precision=2, na_rep='').hide_index().set_table_styles([
                            
                            {
                                "selector":".row0",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":".row1",
                                "props":"background-color:gray; color:white; border:3px black;"
                            },
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                            ]
                            },

                        ])
        display(df)
        item=[tempDf.iloc[i,0] for i in range(2, 10) ]
        mean=[tempDf.iloc[i,1] for i in range(2, 10) ]
        plt.barh(item, mean)
        plt.title('Mean value per item')
        plt.show()
        item=[tempDf.iloc[i,10] for i in range(2, 5) ]
        mean=[tempDf.iloc[i,11] for i in range(2, 5) ]
        plt.bar(item, mean)
        plt.show()
        
        if save=='pdf':
            print("loading pdf...")
            excel = client.Dispatch("Excel.Application")
            pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
            sheets = excel.Workbooks.Open(pathAct)
            wb = sheets.Worksheets[3]
            path=str(os.path.join(Path.home(), "Downloads", "results.pdf"))
            wb.ExportAsFixedFormat(0, path)
            excel.Application.Quit()
            print("pdf downloaded !")
        
        
        
           
    
    #Cognitive load
    def cognitive_load(self, save='display'):
        plt.rcParams["figure.figsize"] = (16,8)
        fig= plt.figure()
             
        #first bar chart/table
        
        ax1= fig.add_subplot(1,3,(1,2))
        columns = ['Mentally demanding', 'physically demanding', 'hurried or rushed pace',  'difficulty']
        mean = self.mentLoad
        
        #Color of the graph
        colorMean, colorMeanInv=[], []
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMean.append('#1CCD00')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#DC2209')
        
        ax1.bar(columns, mean[0], color=colorMean)
        ax1.axhline(y=3.5, color='black')
        ax1.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax1.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            
        ytable.auto_set_column_width(-1)
        
        #Size table
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
            
            
        
        #Second bar chart/table
        ax2= fig.add_subplot(1,3,3)
        columns = ['success','Overall easiness to use']
        mean=self.mentLoadSuccess
        roundMean=[round(mean, 1) for mean in mean[0]]
        #Color of the graph
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMeanInv.append('#DC2209') 
            if roundMean[i]==3.5:
                colorMeanInv.append('#EED238')
            if roundMean[i]>3.5:
                colorMeanInv.append('#1CCD00')
        
        ax2.bar(columns, mean[0], color=colorMeanInv)
        ax2.axhline(y=3.5, color='black')
        ax2.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        wtable = ax2.table(cellText=mean, colLabels=columns, loc='bottom')
        wtable.auto_set_column_width(-1)
        
        #Size table
        for i in range(0,len(columns)):
            cell= wtable[(0,i)]
            cell.set_height(.1)
            wtable[(1, i)].set_facecolor(colorMeanInv[i])
            for j in range(0,2):
                cell= wtable[(j,i)]
                cell.set_height(.15)
                
        fig.subplots_adjust(bottom=0.5, top=1.2)
        
        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Cognitive_Load.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
    
    
    def User_Experience_Qual_Analysis(self, save='display'):

        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=4, nrows=2)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

        coments = list(zip(self.pragmaticQual[0],self.pragmaticQual[1], self.pragmaticQual[2]))
        df = pd.DataFrame(coments, index =['Supportive', 'easiness', 'efficience', 'clearness'],columns =['Green', 'Yellow', 'Red'])
        coments = list(zip(self.hedonicQual[0],self.hedonicQual[1], self.hedonicQual[2]))
        df2 = pd.DataFrame(coments, index =['exciting', 'interesting', 'inventive', 'leading edge'],columns =['Green', 'Yellow', 'Red'])
            
        colMil = pd.DataFrame([[' ', ' ', ' ']], index =['Pragmatic qualities'],columns =['Green', 'Yellow', 'Red'])
        colMil2 = pd.DataFrame([[' ', ' ', ' ']], index =['Hedonic qualities'],columns =['Green', 'Yellow', 'Red'])
            
        #Supportive
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.pragmaticQual[0][0],self.pragmaticQual[1][0], self.pragmaticQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('supportive')
        #Easiness
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.pragmaticQual[0][1],self.pragmaticQual[1][1], self.pragmaticQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('easiness')
        #efficience
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.pragmaticQual[0][2],self.pragmaticQual[1][2], self.pragmaticQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('efficience')
        #clearness
        ax4=fig.add_subplot(spec4[0, 3])
        ax4.pie([self.pragmaticQual[0][3],self.pragmaticQual[1][3], self.pragmaticQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('clearness')
            
        #exciting
        ax1=fig.add_subplot(spec4[1, 0])
        ax1.pie([self.hedonicQual[0][0],self.hedonicQual[1][0], self.hedonicQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('exciting')
        #interesting
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.hedonicQual[0][1],self.hedonicQual[1][1],self.hedonicQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('interesting')
        #inventive
        ax3=fig.add_subplot(spec4[1, 2])
        ax3.pie([self.hedonicQual[0][2],self.hedonicQual[1][2], self.hedonicQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('inventive')
        #leading edge
        ax4=fig.add_subplot(spec4[1, 3])
        ax4.pie([self.hedonicQual[0][3],self.hedonicQual[1][3], self.hedonicQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('leading edge')
            
            
        frames = [colMil,df,colMil2, df2]
        result = pd.concat(frames)

        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "User_Experience_Qual.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
            
        
        
    
    def cognitive_load_Qual_Analysis(self, save='display'):

        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=3, nrows=2)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

        coments = list(zip(self.mentloadQual[0],self.mentloadQual[1], self.mentloadQual[2]))
        df = pd.DataFrame(coments, index =['Mentally demanding', 'physically demanding', 'hurried or rushed pace', 'success','difficulty','Overall easiness to use'],columns =['Green', 'Yellow', 'Red'])
            
            
        #Mentally demanding
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.mentloadQual[0][0],self.mentloadQual[1][0], self.mentloadQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Mentally demanding')
        #physically demanding
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.mentloadQual[0][1],self.mentloadQual[1][1], self.mentloadQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('physically demanding')
        #hurried or rushed pace
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.mentloadQual[0][2],self.mentloadQual[1][2], self.mentloadQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('hurried or rushed pace')
        #success
        ax4=fig.add_subplot(spec4[1, 0])
        ax4.pie([self.mentloadQual[0][3],self.mentloadQual[1][3], self.mentloadQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('success') 
        #difficulty
        ax5=fig.add_subplot(spec4[1, 1])
        ax5.pie([self.mentloadQual[0][4],self.mentloadQual[1][4], self.mentloadQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('difficulty')
        #Overall easiness to use
        ax6=fig.add_subplot(spec4[1, 2])
        ax6.pie([self.mentloadQual[0][5],self.mentloadQual[1][5],self.mentloadQual[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('Overall easiness to use')
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Cognitive_load_Qual.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")


    
    #Software Usability
    def Software_Usability(self, save='display'):
        
        plt.rcParams["figure.figsize"] = (16,8)
        fig= plt.figure()
        ax1 = fig.add_subplot(4,1,1)
        columns = ['simplicity to use', 'helped effectivness of my work', 'helped pace of my work', 'confortable system', 'easy recovery after mistake', 'Overall satisfaction']
        mean = self.softUs
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(mean[0])):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
        ax1.bar(columns, mean[0], color=colorMean)
        ax1.axhline(y=3.5, color='black')
        ax1.set_title('System')
        ax1.set_xticks([])    
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax1.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)             
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        
        ax2= fig.add_subplot(4,1,2)
        columns = ['Clear', 'Easy to find', 'effective', 'Organized']
        mean = self.softUsInfo
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
        ax2.bar(columns, mean[0], color=colorMean)
        ax2.axhline(y=3.5, color='black')
        ax2.set_title('Information')
        ax2.set_xticks([])    
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax2.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        
        ax3= fig.add_subplot(4,1,3)
        columns = ['Pleasant', 'I like using the interface', 'has all the functions and capabilities expected']
        mean = self.softUsInterface
        colorMean=[]
        for i in range(len(mean[0])):
            if mean[0][i]<3.5:
                colorMean.append('#DC2209')
            if round(mean[0][i], 1)==3.5:
                colorMean.append('#EED238')
            if mean[0][i]>3.5:
                colorMean.append('#1CCD00')
        ax3.bar(columns, mean[0], color=colorMean)
        ax3.axhline(y=3.5, color='black')
        ax3.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax3.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
        ax3.set_title('Interface')
        fig.subplots_adjust(bottom=2, top=4, hspace=0.5)
        
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Software_Usability.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
            
            
    def Software_Usability_Qual(self, save='display'):
        plt.rcParams["figure.figsize"] = (20,8)
        
        #System
        fig= plt.figure()
        fig.suptitle('System', fontsize=16)
        spec4 = fig.add_gridspec(ncols=3, nrows=2)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Simplicity to use
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_SystemQual[0][0],self.softUs_SystemQual[1][0], self.softUs_SystemQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Simplicity to use')
        #helped effectivness of my work
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.softUs_SystemQual[0][1],self.softUs_SystemQual[1][1], self.softUs_SystemQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('helped effectivness of my work')
        #helped pace of my work
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.softUs_SystemQual[0][2],self.softUs_SystemQual[1][2], self.softUs_SystemQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('helped pace of my work')
        fig.suptitle('Search formulation (Per-earch)', fontsize=16)
        #confortable
        ax4=fig.add_subplot(spec4[1, 0])
        ax4.pie([self.softUs_SystemQual[0][3],self.softUs_SystemQual[1][3], self.softUs_SystemQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('confortable')
        #easy recovery after mistake
        ax5=fig.add_subplot(spec4[1, 1])
        ax5.pie([self.softUs_SystemQual[0][4],self.softUs_SystemQual[1][4], self.softUs_SystemQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('easy recovery after mistake')
        #overall satisfaction
        ax6=fig.add_subplot(spec4[1, 2])
        ax6.pie([self.softUs_SystemQual[0][5],self.softUs_SystemQual[1][5], self.softUs_SystemQual[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('overall satisfaction')
        
         
            
        #Information
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=4, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #clear
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_InformationQual[0][0],self.softUs_InformationQual[1][0], self.softUs_InformationQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('clear')
        #easy to find
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.softUs_InformationQual[0][1],self.softUs_InformationQual[1][1], self.softUs_InformationQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('easy to find')
        #effective
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.softUs_InformationQual[0][2],self.softUs_InformationQual[1][2], self.softUs_InformationQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('effective')
        #organized
        ax4=fig.add_subplot(spec4[0, 3])
        ax4.pie([self.softUs_InformationQual[0][3],self.softUs_InformationQual[1][3], self.softUs_InformationQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('organized')
        fig.suptitle('Information', fontsize=16)
        
        
        
        
        #Interface
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=3, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #pleasant
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_InterfaceQual[0][0],self.softUs_InterfaceQual[1][0], self.softUs_InterfaceQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('pleasant')
        #Like using interface
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.softUs_InterfaceQual[0][1],self.softUs_InterfaceQual[1][1], self.softUs_InterfaceQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('I like using interface')
        #fonctions and capabilities
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.softUs_InterfaceQual[0][2],self.softUs_InterfaceQual[1][2], self.softUs_InterfaceQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('has all the fonctions and capabilities expected')
        fig.suptitle('Interface', fontsize=16)

        
        
        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Software_Usability_Qual.pdf"))
            pp = PdfPages(path)
            fig_nums = plt.get_fignums()
            figs = [plt.figure(n) for n in fig_nums]
            for fig in figs:
                fig.savefig(pp, format='pdf')
            pp.close()
            print("pdf downloaded !")
        
        
       
            
        
    def Software_Usability_Coments(self, save='display', type='basic'):


        if save=='WordCloud' or type=='WordCloud':
        
            fig= plt.figure(figsize=(20,20))
            spec4 = fig.add_gridspec(ncols=1, nrows=3)
            anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')
        
        
            #system com
            ax1=fig.add_subplot(spec4[0, 0])
            df = pd.DataFrame(self.com1[1])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('System: If it was difficult to recover from any mistake, please comment on the problems.')
        
            #information com
            ax1=fig.add_subplot(spec4[1, 0])
            df = pd.DataFrame(self.com1[2])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('Information:if any information was not clear, what difficulties did you face?')
        
            #interface com
            ax1=fig.add_subplot(spec4[2, 0])
            df = pd.DataFrame(self.com1[3])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('What functions and capabilities would you like to see in this system?')
            
            if save=='pdf' or type=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Usability_coments.pdf"))
                fig.savefig(path,  bbox_inches='tight')
                print("pdf downloaded !")
                
        else:
            
            coments = list(zip(self.com1[1],self.com1[2], self.com1[3]))
            df = pd.DataFrame(coments, index =self.com1[0],columns =['System: If it was difficult to recover from any mistake, please comment on the problems.', 'Information:if any information was not clear, what difficulties did you face?', 'What functions and capabilities would you like to see in this system?'])
        
            df = df.style.format(na_rep='No Coments').set_table_styles([
                                {
                                    "selector":"thead",
                                    "props": [("background-color", "gray"),
                                              ]
                                },

                            ])
            display (df)
            if save=='pdf' or type=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Coments.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Software_Usability_coments.pdf"))    
                dfi.export(df, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")
        

        
        
            
            
            
        #Software Usability
    def Searching_Learning(self, save='display'):       
        
        plt.rcParams["figure.figsize"] = (16,8)
        fig= plt.figure()
        ax1 = fig.add_subplot(4,1,1)
        columns = ['Background Knowledge', 'Interest in Topic', 'Anticipated Difficulty']
        mean = self.PreSearch
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
                
        ax1.bar(columns, mean[0], color=colorMean)
        ax1.axhline(y=3.5, color='black')
        ax1.set_title('Search Formulation (Per-Search)')
        ax1.set_xticks([])    
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax1.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)             
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        
        ax2= fig.add_subplot(4,1,2)
        columns = ['Actual Difficulty', 'Text Presentation Quality', 'Average number of docs viewed per search', 'The usefulness of Search Results', 'Text relevance']
        mean = self.ContentSelection
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(mean[0])):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
                
        ax2.bar(columns, mean[0], color=colorMean)
        ax2.axhline(y=3.5, color='black')
        ax2.set_title('Content Selection')
        ax2.set_xticks([])    
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax2.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)       
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        
        ax3= fig.add_subplot(4,1,3)
        columns = ['Cognitively engaged', 'Suggestions Skills', 'System Understanding Input', 'Average Level of Satisfaction']
        mean = self.InteractionContent
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(mean[0])):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
                
        ax3.bar(columns, mean[0], color=colorMean)
        ax3.axhline(y=3.5, color='black')
        ax3.set_title('Interaction with Content')
        ax3.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax3.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        
        
        ax4= fig.add_subplot(4,1,4)
        columns = ['Search Succes', 'Presentation of the Search Results', 'Expansion of knowledge after the search', 'Understanding about the Topic']
        mean = self.PostSearch
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
                
        ax4.bar(columns, mean[0], color=colorMean)
        ax4.axhline(y=3.5, color='black')
        ax4.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax4.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
        
        ax4.set_title('Post Search')
        fig.subplots_adjust(bottom=2, top=4, hspace=0.5)
        
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Searching_Learning.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
        
    def Searching_Learning_Qual(self, save='display'):
        
        
        plt.rcParams["figure.figsize"] = (20,8)
        
        #Search formulation (Per-earch)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=3, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Background knowledge
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.PreSearchQual[0][0],self.PreSearchQual[1][0], self.PreSearchQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Background knowledge')
        #Interest in topic
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.PreSearchQual[0][1],self.PreSearchQual[1][1], self.PreSearchQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Interest in topic')
        #Anticipated difficulty
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.PreSearchQual[0][2],self.PreSearchQual[1][2], self.PreSearchQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Anticipated difficulty')
        fig.suptitle('Search formulation (Per-earch)', fontsize=16)
         
            
        #Content selection
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=3, nrows=2)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Actual difficulty
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.ContentSelectionQual[0][0],self.ContentSelectionQual[1][0], self.ContentSelectionQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Actual difficulty')
        #Text presentation quality
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.ContentSelectionQual[0][1],self.ContentSelectionQual[1][1], self.ContentSelectionQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Text presentation quality')
        #average number of docs view/search
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.ContentSelectionQual[0][2],self.ContentSelectionQual[1][2], self.ContentSelectionQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('average number of docs view/search')
        #Usefulness of search results
        ax4=fig.add_subplot(spec4[1, 0])
        ax4.pie([self.ContentSelectionQual[0][3],self.ContentSelectionQual[1][3], self.ContentSelectionQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Usefulness of search results')
        #Text relevance
        ax5=fig.add_subplot(spec4[1,1])
        ax5.pie([self.ContentSelectionQual[0][4],self.ContentSelectionQual[1][4], self.ContentSelectionQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('average number of docs view/search')
        fig.suptitle('Content selection', fontsize=16)
        
        
        
        
        #Interaction with content
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=4, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Cognitively engaged
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.InteractionContentQual[0][0],self.InteractionContentQual[1][0], self.InteractionContentQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Cognitively engaged')
        #Suggestions skills
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.InteractionContentQual[0][1],self.InteractionContentQual[1][1], self.InteractionContentQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Suggestions skills')
        #System undersdanting input
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.InteractionContentQual[0][2],self.InteractionContentQual[1][2], self.InteractionContentQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('System undersdanting input')
        #Average leve of satisfaction
        ax4=fig.add_subplot(spec4[0, 3])
        ax4.pie([self.InteractionContentQual[0][3],self.InteractionContentQual[1][3], self.InteractionContentQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Anticipated difficulty')
        fig.suptitle('Interaction with content', fontsize=16)
        
        
        #Post Search
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=4, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Search success
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.PostSearchQual[0][0],self.PostSearchQual[1][0], self.PostSearchQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Search success')
        #Presentation of the results
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.PostSearchQual[0][1],self.PostSearchQual[1][1], self.PostSearchQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Presentation of the results')
        #Expansion of knowledge
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.PostSearchQual[0][2],self.PostSearchQual[1][2], self.PostSearchQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Expansion of knowledge')
        #Understanding about the topic
        ax4=fig.add_subplot(spec4[0, 3])
        ax4.pie([self.PostSearchQual[0][3],self.PostSearchQual[1][3], self.PostSearchQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Understanding about the topic')
        fig.suptitle('Search success', fontsize=16)
        
        
        
        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Searching_Learning_Qual.pdf"))
            pp = PdfPages(path)
            fig_nums = plt.get_fignums()
            figs = [plt.figure(n) for n in fig_nums]
            for fig in figs:
                fig.savefig(pp, format='pdf')
            pp.close()
            print("pdf downloaded !")
        
    #knowledge gain
    def Knowledge_Gain(self, save='display'):
        
        plt.rcParams["figure.figsize"] = (16,8)
        fig= plt.figure()
        
        ax1= fig.add_subplot(1,1,1)
        columns = ['Quality of facts', 'Interpretation', 'Critiques']
        mean=[[]]
        mean = self.KnowledgeGain
        #Color of the graph
        colorMean=[]
        roundMean=[round(mean, 1) for mean in mean[0]]
        for i in range(len(roundMean)):
            if roundMean[i]<3.5:
                colorMean.append('#DC2209')
            if roundMean[i]==3.5:
                colorMean.append('#EED238')
            if roundMean[i]>3.5:
                colorMean.append('#1CCD00')
        ax1.bar(columns, mean[0], color=colorMean)
        ax1.axhline(y=3.5, color='black')
        ax1.set_xticks([])
        
        mean[0]=[round(val, 3) for val in mean[0]]
        ytable = ax1.table(cellText=mean, colLabels=columns,rowLabels=['Mean'], loc='bottom')
        ytable.auto_set_column_width(-1)
        
        #Size table
        for i in range(0,len(columns)):
            cell= ytable[(0,i)]
            cell.set_height(.1)
            ytable[(1, i)].set_facecolor(colorMean[i])
            for j in range(0,2):
                cell= ytable[(j,i)]
                cell.set_height(.15)
                
        cell = ytable[1, -1]
        cell.set_height(.15)
        fig.subplots_adjust(bottom=0.5, top=1.2)
    
        
        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Knowledge_Gain.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
            
    #knowledge gain
    def Knowledge_Gain_Qual_Analysis(self, save='display'):

        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=3, nrows=1)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

        coments = list(zip(self.knowledgeGainQual[0],self.knowledgeGainQual[1], self.knowledgeGainQual[2]))
        df = pd.DataFrame(coments, index =['Quality of facts', 'Interpretation', 'Critiques'],columns =['Green', 'Yellow', 'Red'])
            
            
        #Quality of facts
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.knowledgeGainQual[0][0],self.knowledgeGainQual[1][0], self.knowledgeGainQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Quality of facts')
        #Interpretation
        ax2=fig.add_subplot(spec4[0, 1])
        ax2.pie([self.knowledgeGainQual[0][1],self.knowledgeGainQual[1][1], self.knowledgeGainQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Interpretation')
        #Critiques
        ax3=fig.add_subplot(spec4[0, 2])
        ax3.pie([self.knowledgeGainQual[0][2],self.knowledgeGainQual[1][2], self.knowledgeGainQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Critiques')
            

        
        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Knowledge_Gain_Qual.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
            
            
            
    #print all possible function
    def info(self):
        print("""
        
Quantitative analysis:
benchmark (): Display information on the benchmark 
[ex: MyFile.benchmark()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

results (): Display information on the results of the analyse of the data
[ex: MyFile. results ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

dt (): Display information on the mid-calcul
[ex: MyFile.dt()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version


confidence_Intervals (): Display information on confidence intervals
[ex: MyFile. confidence_Intervals ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version


scale_Consistency (): Display information on scale consistency
[Ex : MyFile. Scale_Consistency ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Inconsistencies () : Display information on inconsistencies
[Ex : MyFile. Inconsistencies ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

cognitive_load (format): Display results of cognitive load
[ex: MyFile.cognitive_load ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version


Software_Usability (format): Display results of software usability
[ex: MyFile.Software_Usability ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Software_Usability_Coments (format): display comments on software usability
[ex: MyFile.Software_Usability_Coments ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version
-'WordCloud': display the information on a word cloud format

Searching_Learning (format): display information on the searching as learning questionnaire
[ex: MyFile.Searching_Learning ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Knowledge_Gain (format): display information on the knowledge gain questionnaire
[ex: MyFile.Knowledge_Gain ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Qualitative analysis:

Knowledge_Gain_Qual_Analysis (): Display qualitative analysis of knowledge gain 
[ex: MyFile.Knowledge_Gain_Qual_Analysis ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version


cognitive_load_Qual_Analysis (): Display qualitative analysis of cognitive load
[ex: MyFile.cognitive_load_Qual_Analysis ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version


User_Experience_Qual_Analysis () : Display qualitative analysis of user experience
[Ex : MyFile.User_Experience_Qual_Analysis ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Software_Usability_Qual (): Display qualitative analysis of software usability
[ex: MyFile.Software_Usability_Qual ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

Searching_Learning_Qual (): Display qualitative analysis of the searching as learning questionnaire
[ex: MyFile.Searching_Learning_Qual ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version

 """)
        