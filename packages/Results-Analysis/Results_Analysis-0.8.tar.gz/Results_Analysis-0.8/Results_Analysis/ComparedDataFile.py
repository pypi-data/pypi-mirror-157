import pandas as pd
import openpyxl
import warnings
from IPython.display import display
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



class ComparedDataFile():
    
    warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
    
    #the type of test that can be used is either welsh-test, t-test or z-test
    
        
    def __init__(self, path, path2, link='independant', test_diff_size='welsh-test'):
        self.test_diff_size=test_diff_size
        self.link=link
        test, ph, au=imp.find_module('Results_Analysis')
        self.to_mod=ph
        wget.download('https://docs.google.com/spreadsheets/d/1Z_KnyxvX2xT2ukVqfle70VLRJl1SnmY2/export?format=xlsx', self.to_mod+'\Short_UEQ_Data_Analysis_Tool.xlsx')
        self.processing(path)
        self.resPath = str(os.path.join(self.to_mod, "resExcel", "DATAUPDATES.XLSX"))
        self.processing2(path2)
        self.resPath2 = str(os.path.join(self.to_mod, "resExcel", "DATAUPDATES2.XLSX"))
        self.diff_size=self.size==self.size2
        self.parameter=False
        if self.test_diff_size!='welsh-test':
            self.diff_size= False
        if self.test_diff_size=='z-test':
            self.parameter=True
        
    
       
        

    def processing(self, path):
        compt=0
        row, column=4, 'A'
        
        #Quantitative analysis
        self.mentLoad,self.mentLoadSuccess, av=[[]],[[]], 0
        self.softUs, self.softUsInfo, self.softUsInterface, self.com1=[[]], [[]], [[]], [[],[],[],[]]
        self.PreSearch, self.ContentSelection, self.InteractionContent, self.PostSearch = [[]], [[]], [[]], [[]]
        self.KnowledgeGain=[[]]
        
        #T-test
        self.hedonicQualData, self.pragmaticQualData=[[],[],[],[]], [[],[],[],[]]
        self.mentLoadData, self.KnowledgeGainData=[[],[],[],[],[],[]], [[],[],[]]
        self.softUsInfoData, self.softUsInterfaceData, self.softUsInterSysData=[[],[],[],[]],[[],[],[]],[[],[],[],[],[],[]]
        self.PreSearchData, self.ContentSelectionData, self.InteractionContentData, self.PostSearchData=[[],[],[]], [[],[],[],[],[]], [[],[],[],[]],[[],[],[],[]]
        
        #Qualitative analysis
        self.hedonicQual, self.pragmaticQual=[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]],[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.mentloadQual=[[0,0,0,0,0,0], [0,0,0,0,0,0],[0,0,0,0,0,0]]
        self.KnowledgeGainQual=[[0,0,0],[0,0,0],[0,0,0]]
        self.PreSearchQual, self.ContentSelectionQual, self.InteractionContentQual, self.PostSearchQual=[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.softUs_SystemQual, self.softUs_InformationQual,self.softUs_InterfaceQual=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]], [[0,0,0,0],[0,0,0,0],[0,0,0,0]], [[0,0,0],[0,0,0],[0,0,0]]
        
        
        
        print("loading first file...")
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
                self.size=len(df[i])
        
            #UX
            #I insert every data of those 8 questions into the nasa form
            if 44<=compt<=51:
                
                for j in df[i]:
                    if compt-44<4:
                        self.pragmaticQualData[compt-44].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.pragmaticQual[0][compt-44]=self.pragmaticQual[0][compt-44]+1
                        elif 3<=df[i].get(j)<=4:
                            self.pragmaticQual[1][compt-44]=self.pragmaticQual[1][compt-44]+1
                        else:
                            self.pragmaticQual[2][compt-44]=self.pragmaticQual[2][compt-44]+1
                        
                        
                    else:
                        self.hedonicQualData[compt-48].append(df[i].get(j))
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
                    self.mentLoadData[compt-52].append(df[i].get(j))
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
            #partie system
            if  58<=compt<=62 or compt==73:
                
                if compt!=73:
                    for j in df[i]:
                        self.softUsInterSysData[compt-58].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.softUs_SystemQual[0][compt-58]=self.softUs_SystemQual[0][compt-58]+1
                        elif 3<=df[i].get(j)<=4:
                            self.softUs_SystemQual[1][compt-58]=self.softUs_SystemQual[1][compt-58]+1
                        else:
                            self.softUs_SystemQual[2][compt-58]=self.softUs_SystemQual[2][compt-58]+1
                        av+=df[i].get(j)
                else:
                    for j in df[i]:
                        self.softUsInterSysData[5].append(df[i].get(j))
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
                
                
            #partie information
            if 64<=compt<=67:
                for j in df[i]:
                    self.softUsInfoData[compt-64].append(df[i].get(j))
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
                
            #partie interface
            if 69<=compt<=71:
                for j in df[i]:
                    self.softUsInterfaceData[compt-69].append(df[i].get(j))
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
                    self.PreSearchData[compt-74].append(df[i].get(j))
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
                    self.ContentSelectionData[compt-77].append(df[i].get(j))
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
                    self.InteractionContentData[compt-82].append(df[i].get(j))
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
                    self.PostSearchData[compt-86].append(df[i].get(j))
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
                    self.KnowledgeGainData[compt-90].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.KnowledgeGainQual[0][compt-90]=self.KnowledgeGainQual[0][compt-90]+1
                    elif 3<=df[i].get(j)<=4:
                        self.KnowledgeGainQual[1][compt-90]=self.KnowledgeGainQual[1][compt-90]+1
                    else:
                        self.KnowledgeGainQual[2][compt-90]=self.KnowledgeGainQual[2][compt-90]+1
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
        print("first file complete")
        
    def processing2(self, path):
        compt=0
        row, column=4, 'A'
        
        #Quantitative analysis
        self.mentLoad2,self.mentLoadSuccess2, av=[[]],[[]], 0
        self.softUs2, self.softUsInfo2, self.softUsInterface2, self.com12=[[]], [[]], [[]], [[],[],[],[]]
        self.PreSearch2, self.ContentSelection2, self.InteractionContent2, self.PostSearch2 = [[]], [[]], [[]], [[]]
        self.KnowledgeGain2=[[]]
        
        #T-test
        self.hedonicQualData2, self.pragmaticQualData2=[[],[],[],[]], [[],[],[],[]]
        self.mentLoadData2, self.KnowledgeGainData2=[[],[],[],[],[],[]], [[],[],[]]
        self.softUsInfoData2, self.softUsInterfaceData2, self.softUsInterSysData2=[[],[],[],[]],[[],[],[]],[[],[],[],[],[],[]]
        self.PreSearchData2, self.ContentSelectionData2, self.InteractionContentData2, self.PostSearchData2=[[],[],[]], [[],[],[],[],[]], [[],[],[],[]],[[],[],[],[]]
        
        #Qualitative analysis
        self.hedonicQual2, self.pragmaticQual2=[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]],[[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.mentloadQual2=[[0,0,0,0,0,0], [0,0,0,0,0,0],[0,0,0,0,0,0]]
        self.KnowledgeGainQual2=[[0,0,0],[0,0,0],[0,0,0]]
        self.PreSearchQual2, self.ContentSelectionQual2, self.InteractionContentQual2, self.PostSearchQual2=[[0,0,0],[0,0,0],[0,0,0]],[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.softUs_SystemQual2, self.softUs_InformationQual2,self.softUs_InterfaceQual2=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]], [[0,0,0,0],[0,0,0,0],[0,0,0,0]], [[0,0,0],[0,0,0],[0,0,0]]
        
        
        
        print("loading second file...")
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
                for j in df[i]:self.com12[0].append(df[i].get(j))
                self.size2=len(df[i])
        
            #UX
            #I insert every data of those 8 questions into the nasa form
            if 44<=compt<=51:
                
                for j in df[i]:
                    if compt-44<4:
                        self.pragmaticQualData2[compt-44].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.pragmaticQual2[0][compt-44]=self.pragmaticQual2[0][compt-44]+1
                        elif 3<=df[i].get(j)<=4:
                            self.pragmaticQual2[1][compt-44]=self.pragmaticQual2[1][compt-44]+1
                        else:
                            self.pragmaticQual2[2][compt-44]=self.pragmaticQual2[2][compt-44]+1
                        
                        
                    else:
                        self.hedonicQualData2[compt-48].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.hedonicQual2[0][compt-48]=self.hedonicQual2[0][compt-48]+1
                        elif  3<=df[i].get(j)<=4:
                            self.hedonicQual2[1][compt-48]=self.hedonicQual2[1][compt-48]+1
                        else:
                            self.hedonicQual2[2][compt-48]=self.hedonicQual2[2][compt-48]+1
                            
                            
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
                    self.mentLoadData2[compt-52].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.mentloadQual2[0][compt-52]=self.mentloadQual2[0][compt-52]+1
                    elif 3<=df[i].get(j)<=4:
                        self.mentloadQual2[1][compt-52]=self.mentloadQual2[1][compt-52]+1
                    else:
                        self.mentloadQual2[2][compt-52]=self.mentloadQual2[2][compt-52]+1
                if compt==55 or compt==57:
                    for j in df[i]:av+=df[i].get(j)
                    av=av/len(df[i])
                    self.mentLoadSuccess2[0].append(av)
                    av=0
                else:
                    for j in df[i]:av+=df[i].get(j)
                    av=av/len(df[i])
                    self.mentLoad2[0].append(av)  
                    av=0

                
            #Software usabilities
            #partie system
            if  58<=compt<=62 or compt==73:
                if compt!=73:
                    for j in df[i]:
                        self.softUsInterSysData2[compt-58].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.softUs_SystemQual2[0][compt-58]=self.softUs_SystemQual2[0][compt-58]+1
                        elif 3<=df[i].get(j)<=4:
                            self.softUs_SystemQual2[1][compt-58]=self.softUs_SystemQual2[1][compt-58]+1
                        else:
                            self.softUs_SystemQual2[2][compt-58]=self.softUs_SystemQual2[2][compt-58]+1
                        av+=df[i].get(j)
                else:
                    for j in df[i]:
                        self.softUsInterSysData2[5].append(df[i].get(j))
                        if df[i].get(j)>4:
                            self.softUs_SystemQual2[0][5]=self.softUs_SystemQual2[0][5]+1
                        elif 3<=df[i].get(j)<=4:
                            self.softUs_SystemQual2[1][5]=self.softUs_SystemQual2[1][5]+1
                        else:
                            self.softUs_SystemQual2[2][5]=self.softUs_SystemQual2[2][5]+1
                        av+=df[i].get(j)
                    
                av=av/len(df[i])
                self.softUs2[0].append(av)
                av=0
                
            
               
            #partie information
            if 64<=compt<=67:
                for j in df[i]:
                    self.softUsInfoData2[compt-64].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.softUs_InformationQual2[0][compt-64]=self.softUs_InformationQual2[0][compt-64]+1
                    elif 3<=df[i].get(j)<=4:
                        self.softUs_InformationQual2[1][compt-64]=self.softUs_InformationQual2[1][compt-64]+1
                    else:
                        self.softUs_InformationQual2[2][compt-64]=self.softUs_InformationQual2[2][compt-64]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.softUsInfo2[0].append(av)
                av=0
            
            #commentaire
            if compt==68:
                for j in df[i]:self.com12[2].append(df[i].get(j))
            if compt==63:
                for j in df[i]:self.com12[1].append(df[i].get(j))
            if compt==72:
                for j in df[i]:self.com12[3].append(df[i].get(j))
            
            
             
            #partie interface
            if 69<=compt<=71:
                for j in df[i]:
                    self.softUsInterfaceData2[compt-69].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.softUs_InterfaceQual2[0][compt-69]=self.softUs_InterfaceQual2[0][compt-69]+1
                    elif 3<=df[i].get(j)<=4:
                        self.softUs_InterfaceQual2[1][compt-69]=self.softUs_InterfaceQual2[1][compt-69]+1
                    else:
                        self.softUs_InterfaceQual2[2][compt-69]=self.softUs_InterfaceQual2[2][compt-69]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.softUsInterface2[0].append(av)
                av=0
                
            #Searching as learning
            #Pre-Search
            if 74<=compt<=76:
                for j in df[i]:
                    self.PreSearchData2[compt-74].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.PreSearchQual2[0][compt-74]=self.PreSearchQual2[0][compt-74]+1
                    elif 3<=df[i].get(j)<=4:
                        self.PreSearchQual2[1][compt-74]=self.PreSearchQual2[1][compt-74]+1
                    else:
                        self.PreSearchQual2[2][compt-74]=self.PreSearchQual2[2][compt-74]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.PreSearch2[0].append(av)
                av=0
                
            #Content Selection
            if 77<=compt<=81:
                for j in df[i]:
                    self.ContentSelectionData2[compt-77].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.ContentSelectionQual2[0][compt-77]=self.ContentSelectionQual2[0][compt-77]+1
                    elif 3<=df[i].get(j)<=4:
                        self.ContentSelectionQual2[1][compt-77]=self.ContentSelectionQual2[1][compt-77]+1
                    else:
                        self.ContentSelectionQual2[2][compt-77]=self.ContentSelectionQual2[2][compt-77]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.ContentSelection2[0].append(av)
                av=0
            
            #Interaction with content
            if 82<=compt<=85:
                for j in df[i]:
                    self.InteractionContentData2[compt-82].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.InteractionContentQual2[0][compt-82]=self.InteractionContentQual2[0][compt-82]+1
                    elif 3<=df[i].get(j)<=4:
                        self.InteractionContentQual2[1][compt-82]=self.InteractionContentQual2[1][compt-82]+1
                    else:
                        self.InteractionContentQual2[2][compt-82]=self.InteractionContentQual2[2][compt-82]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.InteractionContent2[0].append(av)
                av=0
            
            
            #Post-Search
            if 86<=compt<=89:
                for j in df[i]:
                    self.PostSearchData2[compt-86].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.PostSearchQual2[0][compt-86]=self.PostSearchQual2[0][compt-86]+1
                    elif 3<=df[i].get(j)<=4:
                        self.PostSearchQual2[1][compt-86]=self.PostSearchQual2[1][compt-86]+1
                    else:
                        self.PostSearchQual2[2][compt-86]=self.PostSearchQual2[2][compt-86]+1
                    av+=df[i].get(j)
                av=av/len(df[i])
                self.PostSearch2[0].append(av)
                av=0
            
            #Knowledge gain
            if 90<=compt<=92:
                for j in df[i]:
                    self.KnowledgeGainData2[compt-90].append(df[i].get(j))
                    if df[i].get(j)>4:
                        self.KnowledgeGainQual2[0][compt-90]=self.KnowledgeGainQual2[0][compt-90]+1
                    elif 3<=df[i].get(j)<=4:
                        self.KnowledgeGainQual2[1][compt-90]=self.KnowledgeGainQual2[1][compt-90]+1
                    else:
                        self.KnowledgeGainQual2[2][compt-90]=self.KnowledgeGainQual2[2][compt-90]+1
                    av+=df[i].get(j)
                    
                av=av/len(df[i])
                self.KnowledgeGain2[0].append(av)
                av=0    
            
                
        print("converting data...")
        spreadsheet=self.to_mod+'\DataUpdates2.xlsx'
        xfile.save(spreadsheet)

        fpath = spreadsheet
        dirname = str(os.path.join(self.to_mod, "resExcel"))
        xl_model = formulas.ExcelModel().loads(fpath).finish()
        xl_model.calculate()
        xl_model.write(dirpath=dirname)
        print("Second file complete")
        
       
    #User Experience  
    def dt(self, save='display'):
        print('file 1/file 2 dt')
        df = pd.read_excel(self.resPath, sheet_name='DT')
        df2 = pd.read_excel(self.resPath2, sheet_name='DT')
        
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "dt.pdf"))
            pathAct = str(os.path.join(self.to_mod, "dt.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")
        
    def confidence_Intervals(self, save='display'):
        print('file 1/file 2 confidence intervals')
        df = pd.read_excel(self.resPath, sheet_name='CONFIDENCE_INTERVALS')
        df2 = pd.read_excel(self.resPath2, sheet_name='CONFIDENCE_INTERVALS')
        
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row1",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row2",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)+1),
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)+2),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "confidence_Intervals.pdf"))
            pathAct = str(os.path.join(self.to_mod, "confidence_Intervals.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")
        
        
    def scale_Consistency(self, save='display'):
        print('file 1/file 2 scale consistency')
        df = pd.read_excel(self.resPath, sheet_name='SCALE_CONSISTENCY')
        df2 = pd.read_excel(self.resPath2, sheet_name='SCALE_CONSISTENCY')
        
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row1",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row2",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)+1),
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)+2),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "scale_consistency.pdf"))
            pathAct = str(os.path.join(self.to_mod, "scale_consistency.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")
        

    def inconsistencies(self, save='display'):
        print('file 1/file 2 inconsistencies')
        df = pd.read_excel(self.resPath, sheet_name='INCONSISTENCIES')
        df2 = pd.read_excel(self.resPath2, sheet_name='INCONSISTENCIES')
        
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "inconsistencies.pdf"))
            pathAct = str(os.path.join(self.to_mod, "inconsistencies.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")


    def benchmark(self, save='display'):
        print('file 1/file 2 benchmark')
        df = pd.read_excel(self.resPath, sheet_name='BENCHMARK')
        df2 = pd.read_excel(self.resPath2, sheet_name='BENCHMARK')
        tempDf =df
        tempDf2 =df2
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        
        plt.rcParams['figure.figsize'] = [8,5]
        fig= plt.figure()
        ax1= fig.add_subplot(2,1,1)
        cat = [tempDf.iloc[i,0] for i in range(24, 27)]
        line=[tempDf.iloc[i,7] for i in range(24, 27)]
        Excellent = np.array([tempDf.iloc[i,6] for i in range(24, 27)])
        Good = np.array([tempDf.iloc[i,5] for i in range(24, 27)])
        Above_average = np.array([tempDf.iloc[i,4] for i in range(24, 27)])
        Below_average = np.array([tempDf.iloc[i,3] for i in range(24, 27)])
        Bad = np.array([tempDf.iloc[i,2] for i in range(24, 27)])
        Lower_Border = np.array([tempDf.iloc[i,1] for i in range(24, 27)])
        ind = [x for x, _ in enumerate(cat)]

        ax1.bar(ind, Excellent, width=0.8, label='Excellent', color='#3EBA24', bottom=Good+Above_average+Below_average+Bad)
        ax1.bar(ind, Good, width=0.8, label='Good', color='#8EFA78', bottom=Above_average+Below_average+Bad)
        ax1.bar(ind, Above_average, width=0.8, label='Above average', color='#73C362', bottom=Below_average+Bad)
        ax1.bar(ind, Below_average, width=0.8, label='Below average', color='#EBC63C', bottom=Bad)
        ax1.bar(ind, Bad, width=0.8, label='Bad', color='#E8281F')
        ax1.bar(ind, Lower_Border, width=0.8, color='#E8281F')
        ax1.plot(line, color='black',marker='o' ,ms=5)
        ax1.set_xticks(ind, cat)
        ax1.legend(loc="upper right")
        ax1.set_title('file 1')
        
        plt.rcParams['figure.figsize'] = [8,5]
        ax2= fig.add_subplot(2,1,2)
        cat = [tempDf2.iloc[i,0] for i in range(24, 27)]
        line=[tempDf2.iloc[i,7] for i in range(24, 27)]
        Excellent = np.array([tempDf2.iloc[i,6] for i in range(24, 27)])
        Good = np.array([tempDf2.iloc[i,5] for i in range(24, 27)])
        Above_average = np.array([tempDf2.iloc[i,4] for i in range(24, 27)])
        Below_average = np.array([tempDf2.iloc[i,3] for i in range(24, 27)])
        Bad = np.array([tempDf2.iloc[i,2] for i in range(24, 27)])
        Lower_Border = np.array([tempDf2.iloc[i,1] for i in range(24, 27)])
        ind = [x for x, _ in enumerate(cat)]

        ax2.bar(ind, Excellent, width=0.8, label='Excellent', color='#3EBA24', bottom=Good+Above_average+Below_average+Bad)
        ax2.bar(ind, Good, width=0.8, label='Good', color='#8EFA78', bottom=Above_average+Below_average+Bad)
        ax2.bar(ind, Above_average, width=0.8, label='Above average', color='#73C362', bottom=Below_average+Bad)
        ax2.bar(ind, Below_average, width=0.8, label='Below average', color='#EBC63C', bottom=Bad)
        ax2.bar(ind, Bad, width=0.8, label='Bad', color='#E8281F')
        ax2.bar(ind, Lower_Border, width=0.8, color='#E8281F')
        ax2.plot(line, color='black',marker='o' ,ms=5)
        ax2.set_title('file 2')
        ax2.set_xticks(ind, cat)
        ax2.legend(loc="upper right")
        
        fig.subplots_adjust(bottom=2, top=4)
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "benchmark.pdf"))
            pathAct = str(os.path.join(self.to_mod, "benchmark.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")

        # if save=='pdf':
        #     print("loading pdf...")
        #     excel = client.Dispatch("Excel.Application")
        #     pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
        #     sheets = excel.Workbooks.Open(pathAct)
        #     wb = sheets.Worksheets[6]
        #     path=str(os.path.join(Path.home(), "Downloads", "benchmark.pdf"))
        #     wb.ExportAsFixedFormat(0, path)
        #     excel.Application.Quit()
        #     print("pdf downloaded !")
        

    def results(self, save='display'):
        print('file 1/file 2 results')
        df = pd.read_excel(self.resPath, sheet_name='RESULTS')
        df2 = pd.read_excel(self.resPath2, sheet_name='RESULTS')
        tempDf =df
        tempDf2 =df2
        
        frames = [df,df2]
        tab = pd.concat(frames)
        

        tab = tab.style.format(precision=2,na_rep='  ').hide_index().set_table_styles([
                            {
                                "selector":"thead",
                                "props": [("visibility", "collapse"),
                                          ]
                            },
                            {
                                "selector":".row0",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row1",
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)),
                                "props": [("background-color", "gray"),
                                          ]
                            },
                            {
                                "selector":".row"+str(len(df)+1),
                                "props": [("background-color", "gray"),
                                          ]
                            },

                        ])
        display (tab)          
        print('file 1')
        item=[tempDf.iloc[i,0] for i in range(2, 10) ]
        mean=[tempDf.iloc[i,1] for i in range(2, 10) ]
        plt.barh(item, mean)
        plt.title('Mean value per item')
        plt.show()
        item=[tempDf.iloc[i,10] for i in range(2, 5) ]
        mean=[tempDf.iloc[i,11] for i in range(2, 5) ]
        plt.bar(item, mean)
        plt.show()
        
        print('file 2')
        item=[tempDf2.iloc[i,0] for i in range(2, 10) ]
        mean=[tempDf2.iloc[i,1] for i in range(2, 10) ]
        plt.barh(item, mean)
        plt.title('Mean value per item')
        plt.show()
        item=[tempDf2.iloc[i,10] for i in range(2, 5) ]
        mean=[tempDf2.iloc[i,11] for i in range(2, 5) ]
        plt.bar(item, mean)
        plt.show()
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "inconsistencies.pdf"))
            pathAct = str(os.path.join(self.to_mod, "inconsistencies.pdf"))    
            dfi.export(tab, pathAct)
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)
            builder.insert_image(pathAct)
            doc.save(path)
            print("pdf downloaded !")
        # if save=='pdf':
        #     print("loading pdf...")
        #     excel = client.Dispatch("Excel.Application")
        #     pathAct = str(os.path.join(self.to_mod, "resExcel", "DataUpdates.xlsx"))
        #     sheets = excel.Workbooks.Open(pathAct)
        #     wb = sheets.Worksheets[3]
        #     path=str(os.path.join(Path.home(), "Downloads", "results.pdf"))
        #     wb.ExportAsFixedFormat(0, path)
        #     excel.Application.Quit()
        #     print("pdf downloaded !")
        
        
        
           
    
    #Cognitive load
    def cognitive_load(self, format,save='notActivated', alpha=0.05):
        
        if type(save) != str:alpha=save
        
        print('type of analysis: Quantitative')
        
        if format=='graph':
            
            plt.rcParams["figure.figsize"] = (16,8)
            fig= plt.figure()
            index = np.arange(4)
            width = 0.35
            #first bar chart/table

            ax1= fig.add_subplot(2,1,1)
            columns = ['mentally demanding', 'physically demanding', 'hurried or rushed pace',  'difficulty']
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

            ax1.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            mean = self.mentLoad2

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

            ax1.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)

            ax1.axhline(y=3.5, color='black')
            ax1.set_xticks([])


            colorMean=[]
            mean2=[[]]
            
            mean2[0].append(self.mentLoad[0][0])
            mean2[0].append(self.mentLoad2[0][0])
            mean2[0].append(self.mentLoad[0][1])
            mean2[0].append(self.mentLoad2[0][1])
            mean2[0].append(self.mentLoad[0][2])
            mean2[0].append(self.mentLoad2[0][2])
            mean2[0].append(self.mentLoad[0][3])
            mean2[0].append(self.mentLoad2[0][3])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#1CCD00')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#DC2209')

            columns = ['mentally demanding f1','f2', 'physically demanding f1', 'f2', 'hurried or rushed pace f1','f2',  'difficulty f1', 'f2']
            ytable = ax1.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')

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
            index = np.arange(2)
            ax2= fig.add_subplot(2,1,2)
            columns = ['success','overall easiness to use']
            mean=self.mentLoadSuccess
            colorMeanInv=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            #Color of the graph
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMeanInv.append('#DC2209') 
                if roundMean[i]==3.5:
                    colorMeanInv.append('#EED238')
                if roundMean[i]>3.5:
                    colorMeanInv.append('#1CCD00')

            ax2.bar(index- width/2, mean[0], color=colorMeanInv, width = 0.25)
            
            colorMeanInv=[]
            mean=self.mentLoadSuccess2
            roundMean=[round(mean, 1) for mean in mean[0]]
            #Color of the graph
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMeanInv.append('#DC2209') 
                if roundMean[i]==3.5:
                    colorMeanInv.append('#EED238')
                if roundMean[i]>3.5:
                    colorMeanInv.append('#1CCD00')

            ax2.bar(index+ width/2, mean[0], color=colorMeanInv, width = 0.25)

            ax2.axhline(y=3.5, color='black')
            ax2.set_xticks([])
            #enlever le diviser par deux pour plus value, mettre test_rel pour dependant test

            colorMeanInv=[]
            mean2=[[]]    
            mean2[0].append(self.mentLoadSuccess[0][0])
            mean2[0].append(self.mentLoadSuccess2[0][0])
            mean2[0].append(self.mentLoadSuccess[0][1])
            mean2[0].append(self.mentLoadSuccess2[0][1])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMeanInv.append('#DC2209') 
                if roundMean[i]==3.5:
                    colorMeanInv.append('#EED238')
                if roundMean[i]>3.5:
                    colorMeanInv.append('#1CCD00')

            columns = ['success f1','f2', 'overall easiness to use f1', 'f2']
            wtable = ax2.table(cellText=mean2, colLabels=columns, loc='bottom')
            wtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= wtable[(0,i)]
                cell.set_height(.1)
                wtable[(1, i)].set_facecolor(colorMeanInv[i])
                for j in range(0,2):
                    cell= wtable[(j,i)]
                    cell.set_height(.15)

            fig.subplots_adjust(bottom=1, top=2, hspace=0.5)
            
            #pdf download
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Cognitive_Load.pdf"))
                fig.savefig(path,  bbox_inches='tight')
                print("pdf downloaded !")
        
        if format=='tab':
            if (not self.diff_size or self.size<=30) and not self.parameter:
                print('type of test: t-test')
                print('level of significance: '+str(alpha))
                if self.link=='independant':
                    print('Sample: independant')
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[0],self.mentLoadData2[0], equal_var=self.diff_size)
                    one_tailed_p_value=p_value
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value>0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[1],self.mentLoadData2[1], equal_var=self.diff_size)
                    one_tailed_p_value2=p_value
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value>0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[2],self.mentLoadData2[2], equal_var=self.diff_size)
                    one_tailed_p_value3=p_value
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value>0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[3],self.mentLoadData2[3], equal_var=self.diff_size)
                    one_tailed_p_value4=p_value
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value>0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[4],self.mentLoadData2[4], equal_var=self.diff_size)
                    one_tailed_p_value5=p_value
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.mentLoadData[5],self.mentLoadData2[5], equal_var=self.diff_size)
                    one_tailed_p_value6=p_value
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###
                    #je veux tester si ils sont significment different et si oui si ils lequel est le meilleur
                    d = {'categories': ['mentally demanding', 'physicaly demanding', 'hurried or rushed pace','difficulty'], 'file 1': [self.mentLoad[0][0], self.mentLoad[0][1],self.mentLoad[0][2],self.mentLoad[0][3]], 'file 2': [self.mentLoad2[0][0], self.mentLoad2[0][1],self.mentLoad2[0][2],self.mentLoad2[0][3]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4], 'significant diff': [res1, res2, res3, res4], 'best file': [best1, best2, best3, best4]}
                    df = pd.DataFrame(data=d)
                    
                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = [' '], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    
                    d = {'categories': ['success', 'overall easiness to use'], 'file 1': [self.mentLoadSuccess[0][0], self.mentLoadSuccess[0][1]], 'file 2': [self.mentLoadSuccess2[0][0], self.mentLoadSuccess2[0][1]], 'p-value': [one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res5, res6], 'best file': [best5, best6]}
                    df2 = pd.DataFrame(data=d)
                    frames = [df, dfmid, df2]
                    tab = pd.concat(frames)
                    display (tab)
                    
                if self.link=='dependant':
                    print('Sample: dependant')
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[0],self.mentLoadData2[0])
                    one_tailed_p_value=p_value/2
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value>0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[1],self.mentLoadData2[1])
                    one_tailed_p_value2=p_value/2
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value>0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[2],self.mentLoadData2[2])
                    one_tailed_p_value3=p_value/2
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value>0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[3],self.mentLoadData2[3])
                    one_tailed_p_value4=p_value/2
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value>0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[4],self.mentLoadData2[4])
                    one_tailed_p_value5=p_value/2
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.mentLoadData[5],self.mentLoadData2[5])
                    one_tailed_p_value6=p_value/2
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###
                    #je veux tester si ils sont significment different et si oui si ils lequel est le meilleur
                    d = {'categories': ['mentally demanding', 'physicaly demanding', 'hurried or rushed pace','difficulty'], 'file 1': [self.mentLoad[0][0], self.mentLoad[0][1],self.mentLoad[0][2],self.mentLoad[0][3]], 'file 2': [self.mentLoad2[0][0], self.mentLoad2[0][1],self.mentLoad2[0][2],self.mentLoad2[0][3]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4], 'significant diff': [res1, res2, res3, res4], 'best file': [best1, best2, best3, best4]}
                    df = pd.DataFrame(data=d)
                    
                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = [' '], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    
                    d = {'categories': ['success', 'overall easiness to use'], 'file 1': [self.mentLoadSuccess[0][0], self.mentLoadSuccess[0][1]], 'file 2': [self.mentLoadSuccess2[0][0], self.mentLoadSuccess2[0][1]], 'p-value': [one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res5, res6], 'best file': [best5, best6]}
                    df2 = pd.DataFrame(data=d)
                    frames = [df, dfmid, df2]
                    tab = pd.concat(frames)
                    display (tab)
                    
                    
            else: 
                print("type of test: z-test")
                    
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[0], x2=self.mentLoadData2[0], value=0)
                one_tailed_p_value=p_value
                if one_tailed_p_value>alpha:
                    res1 = 'No'
                    best1 = '/'
                else:
                    res1 = 'Yes'
                    if ztest_Score>0:
                        best1 = 'file 2'
                    else:
                        best1 = 'file 1'
                ###   
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[1], x2=self.mentLoadData2[1], value=0)
                one_tailed_p_value2=p_value
                if one_tailed_p_value2>alpha:
                    res2 = 'No'
                    best2 = '/'
                else:
                    res2 = 'Yes'
                    if ztest_Score>0:
                        best2 = 'file 2'
                    else:
                        best2 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[2], x2=self.mentLoadData2[2], value=0)
                one_tailed_p_value3=p_value
                if one_tailed_p_value3>alpha:
                    res3 = 'No'
                    best3 = '/'
                else:
                    res3 = 'Yes'
                    if ztest_Score>0:
                        best3 = 'file 2'
                    else:
                        best3 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[3], x2=self.mentLoadData2[3], value=0)
                one_tailed_p_value4=p_value
                if one_tailed_p_value4>alpha:
                    res4 = 'No'
                    best4 = '/'
                else:
                    res4 = 'Yes'
                    if ztest_Score>0:
                        best4 = 'file 2'
                    else:
                        best4 = 'file 1'

                    
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[4], x2=self.mentLoadData2[4], value=0)
                one_tailed_p_value5=p_value
                if one_tailed_p_value5>alpha:
                    
                    res5 = 'No'
                    best5 = '/'
                else:
                    res5 = 'Yes'
                    if ztest_Score<0:
                        best5 = 'file 2'
                    else:
                        best5 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.mentLoadData[5], x2=self.mentLoadData2[5], value=0)
                one_tailed_p_value6=p_value
                if one_tailed_p_value6>alpha:
                    res6 = 'No'
                    best6 = '/'
                else:
                    res6 = 'Yes'
                    if ztest_Score<0:
                        best6 = 'file 2'
                    else:
                        best6 = 'file 1'
                ###
                d = {'categories': ['mentally demanding', 'physicaly demanding', 'hurried or rushed pace','difficulty'], 'file 1': [self.mentLoad[0][0], self.mentLoad[0][1],self.mentLoad[0][2],self.mentLoad[0][3]], 'file 2': [self.mentLoad2[0][0], self.mentLoad2[0][1],self.mentLoad2[0][2],self.mentLoad2[0][3]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4], 'significant diff': [res1, res2, res3, res4], 'best file': [best1, best2, best3, best4]}
                df = pd.DataFrame(data=d)

                dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = [' '], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])

                d = {'categories': ['success', 'overall easiness to use'], 'file 1': [self.mentLoadSuccess[0][0], self.mentLoadSuccess[0][1]], 'file 2': [self.mentLoadSuccess2[0][0], self.mentLoadSuccess2[0][1]], 'p-value': [one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res5, res6], 'best file': [best5, best6]}
                df2 = pd.DataFrame(data=d)
                frames = [df, dfmid, df2]
                tab = pd.concat(frames)
                display (tab)

            #pdf download
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Cognitive_Load.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Cognitive_Load.pdf"))    
                dfi.export(tab, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")
    
    
    def User_Experience_Qual_Analysis(self, save='display'):
        
        print('type of analysis: Qualitative')
        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=8)
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
        ax1.set_title('supportive file 1')
        #Supportive
        ax1v2=fig.add_subplot(spec4[0, 1])
        ax1v2.pie([self.pragmaticQual2[0][0],self.pragmaticQual2[1][0], self.pragmaticQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1v2.set_title('supportive file 2')
        #Easiness
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.pragmaticQual[0][1],self.pragmaticQual[1][1], self.pragmaticQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('easiness file 1')
        #Easiness
        ax2v2=fig.add_subplot(spec4[1, 1])
        ax2v2.pie([self.pragmaticQual2[0][1],self.pragmaticQual2[1][1], self.pragmaticQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2v2.set_title('easiness file 2')
        #efficience
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.pragmaticQual[0][2],self.pragmaticQual[1][2], self.pragmaticQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('efficience file 1')
        #efficience
        ax3v2=fig.add_subplot(spec4[2, 1])
        ax3v2.pie([self.pragmaticQual2[0][2],self.pragmaticQual2[1][2], self.pragmaticQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3v2.set_title('efficience file 2')
        #clearness
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.pragmaticQual[0][3],self.pragmaticQual[1][3], self.pragmaticQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('clearness file 1')
        #clearness
        ax4v2=fig.add_subplot(spec4[3, 1])
        ax4v2.pie([self.pragmaticQual2[0][3],self.pragmaticQual2[1][3], self.pragmaticQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4v2.set_title('clearness file 2')
            
        #exciting
        ax1=fig.add_subplot(spec4[4, 0])
        ax1.pie([self.hedonicQual[0][0],self.hedonicQual[1][0], self.hedonicQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('exciting file 1')
        #exciting
        ax1v2=fig.add_subplot(spec4[4, 1])
        ax1v2.pie([self.hedonicQual2[0][0],self.hedonicQual2[1][0], self.hedonicQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1v2.set_title('exciting file 2')
        #interesting
        ax2=fig.add_subplot(spec4[5, 0])
        ax2.pie([self.hedonicQual[0][1],self.hedonicQual[1][1],self.hedonicQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('interesting file 1')
        #interesting
        ax2v2=fig.add_subplot(spec4[5, 1])
        ax2v2.pie([self.hedonicQual2[0][1],self.hedonicQual2[1][1],self.hedonicQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2v2.set_title('interesting file 2')
        #inventive
        ax3=fig.add_subplot(spec4[6, 0])
        ax3.pie([self.hedonicQual[0][2],self.hedonicQual[1][2], self.hedonicQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('inventive file 1')
        #inventive
        ax3v2=fig.add_subplot(spec4[6, 1])
        ax3v2.pie([self.hedonicQual2[0][2],self.hedonicQual2[1][2], self.hedonicQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3v2.set_title('inventive file 2')
        #leading edge
        ax4=fig.add_subplot(spec4[7, 0])
        ax4.pie([self.hedonicQual[0][3],self.hedonicQual[1][3], self.hedonicQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('leading edge file 1')
        #leading edge
        ax4v2=fig.add_subplot(spec4[7, 1])
        ax4v2.pie([self.hedonicQual2[0][3],self.hedonicQual2[1][3], self.hedonicQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4v2.set_title('leading edge file 2')
            
        fig.subplots_adjust(bottom=4, top=8)
        frames = [colMil,df,colMil2, df2]
        result = pd.concat(frames)


        #pdf download
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "User_Experience_Qual.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")
            
        
        
    
    def cognitive_load_Qual_Analysis(self, save='display'):
        print('type of analysis: Qualitative')
        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=6)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

        coments = list(zip(self.mentloadQual[0],self.mentloadQual[1], self.mentloadQual[2]))
        df = pd.DataFrame(coments, index =['Mentally demanding', 'physically demanding', 'hurried or rushed pace', 'success','difficulty','Overall easiness to use'],columns =['Green', 'Yellow', 'Red'])
            
            
        #Mentally demanding
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.mentloadQual[0][0],self.mentloadQual[1][0], self.mentloadQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Mentally demanding')
        #Mentally demanding
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.mentloadQual2[0][0],self.mentloadQual2[1][0], self.mentloadQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Mentally demanding file 2')
        #physically demanding
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.mentloadQual[0][1],self.mentloadQual[1][1], self.mentloadQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('physically demanding')
        #physically demanding
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.mentloadQual2[0][1],self.mentloadQual2[1][1], self.mentloadQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('physically demanding file 2')
        #hurried or rushed pace
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.mentloadQual[0][2],self.mentloadQual[1][2], self.mentloadQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('hurried or rushed pace')
        #hurried or rushed pace
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.mentloadQual2[0][2],self.mentloadQual2[1][2], self.mentloadQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('hurried or rushed pace file 2')
        #success
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.mentloadQual[0][3],self.mentloadQual[1][3], self.mentloadQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('success') 
        #success
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.mentloadQual2[0][3],self.mentloadQual2[1][3], self.mentloadQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('success file 2') 
        #difficulty
        ax5=fig.add_subplot(spec4[4, 0])
        ax5.pie([self.mentloadQual[0][4],self.mentloadQual[1][4], self.mentloadQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('difficulty')
        #difficulty
        ax5=fig.add_subplot(spec4[4, 1])
        ax5.pie([self.mentloadQual2[0][4],self.mentloadQual2[1][4], self.mentloadQual2[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('difficulty file 2')
        #Overall easiness to use
        ax6=fig.add_subplot(spec4[5, 0])
        ax6.pie([self.mentloadQual[0][5],self.mentloadQual[1][5],self.mentloadQual[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('Overall easiness to use')
        #Overall easiness to use
        ax6=fig.add_subplot(spec4[5, 1])
        ax6.pie([self.mentloadQual2[0][5],self.mentloadQual2[1][5],self.mentloadQual2[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('Overall easiness to use file 2')
        
        fig.subplots_adjust(bottom=4, top=8)
        
        if save=='pdf':
            print("loading pdf...")
            path=str(os.path.join(Path.home(), "Downloads", "Cognitive_load_Qual.pdf"))
            fig.savefig(path,  bbox_inches='tight')
            print("pdf downloaded !")


    
    #Software Usability
    def Software_Usability(self, format,save='notActivated', alpha=0.05):
        
        if type(save) != str:alpha=save
        print('type of analysis: Quantitative')
        
        if format=='graph':
            plt.rcParams["figure.figsize"] = (16,8)
            fig= plt.figure()
            index = np.arange(6)
            width = 0.35

            #First bar chart/table
            ax1 = fig.add_subplot(3,1,1)
            columns = ['simplicity to use', 'helped effectivness of my work', 'helped pace of my work', 'confortable system', 'easy recovery after mistake', 'Overall satisfaction']
            mean = self.softUs
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]                   
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            ax1.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            ax1.axhline(y=3.5, color='black')
            ax1.set_title('System')
            ax1.set_xticks([])


            mean = self.softUs2
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]                   
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')
            ax1.bar(index+ width/2, mean[0], color=colorMean, width = 0.25) 
            ax1.axhline(y=3.5, color='black')
            ax1.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.softUs[0][0])
            mean2[0].append(self.softUs2[0][0])
            mean2[0].append(self.softUs[0][1])
            mean2[0].append(self.softUs2[0][1])
            mean2[0].append(self.softUs[0][2])
            mean2[0].append(self.softUs2[0][2])
            mean2[0].append(self.softUs[0][3])
            mean2[0].append(self.softUs2[0][3])
            mean2[0].append(self.softUs[0][4])
            mean2[0].append(self.softUs2[0][4])
            mean2[0].append(self.softUs[0][5])
            mean2[0].append(self.softUs2[0][5])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['simplicity to use f1','f2', 'helped effectivness of my work f1','f2', 'helped pace of my work f1','f2', 'confortable system f1','f2', 'easy recovery after mistake f1','f2', 'Overall satisfaction f1','f2']

            ytable = ax1.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
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


            #Second bar chart/table
            index = np.arange(4)
            ax2= fig.add_subplot(3,1,2)
            columns = ['clear', 'easy to find', 'effective', 'organized']
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

            ax2.bar(index- width/2, mean[0], color=colorMean, width = 0.25)

            mean=self.softUsInfo2                  
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]                   
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')                 
            ax2.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax2.axhline(y=3.5, color='black')
            ax2.set_title('Information')
            ax2.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.softUsInfo[0][0])
            mean2[0].append(self.softUsInfo2[0][0])
            mean2[0].append(self.softUsInfo[0][1])
            mean2[0].append(self.softUsInfo2[0][1])
            mean2[0].append(self.softUsInfo[0][2])
            mean2[0].append(self.softUsInfo2[0][2])
            mean2[0].append(self.softUsInfo[0][3])
            mean2[0].append(self.softUsInfo2[0][3])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['clear f1','f2', 'easy to find f1', 'f2', 'effective f1', 'f2', 'organized f1', 'f2']

            wtable = ax2.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            wtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= wtable[(0,i)]
                cell.set_height(.1)
                wtable[(1, i)].set_facecolor(colorMean[i])
                for j in range(0,2):
                    cell= wtable[(j,i)]
                    cell.set_height(.15)

            cell = wtable[1, -1]
            cell.set_height(.15)

            #Third bar chart/table
            index = np.arange(3)
            ax3= fig.add_subplot(3,1,3)
            columns = ['pleasant', '"I like using the interface"', 'has all the functions and capabilities expected']


            mean = self.softUsInterface
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            ax3.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            ax3.axhline(y=3.5, color='black')
            ax3.set_xticks([])


            mean=self.softUsInterface2                  
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')                
            ax3.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax3.axhline(y=3.5, color='black')
            ax3.set_title('Interface')
            ax3.set_xticks([])


            colorMean=[]
            mean2=[[]]
            mean2[0].append(self.softUsInterface[0][0])
            mean2[0].append(self.softUsInterface2[0][0])
            mean2[0].append(self.softUsInterface[0][1])
            mean2[0].append(self.softUsInterface2[0][1])
            mean2[0].append(self.softUsInterface[0][2])
            mean2[0].append(self.softUsInterface2[0][2])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['pleasant f1','f2', 'I like using the interface f1','f2', 'has all the functions and capabilities expected f1', 'f2']
            xtable = ax3.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            xtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= xtable[(0,i)]
                cell.set_height(.1)
                xtable[(1, i)].set_facecolor(colorMean[i])
                for j in range(0,2):
                    cell= xtable[(j,i)]
                    cell.set_height(.15)

            cell = xtable[1, -1]
            cell.set_height(.15)    

            fig.subplots_adjust(bottom=4, top=5.5, hspace=0.5)
            
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Usability.pdf"))
                fig.savefig(path,  bbox_inches='tight')
                print("pdf downloaded !")
        
        if format=='tab':
            if (not self.diff_size or self.size<=30) and not self.parameter:
                print('type of test: t-test')
                print("level of significance: "+str(alpha))
                if self.link=='independant':
                    print('Sample: independant')
                    
                    #####################################################################################################################"
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[0],self.softUsInterSysData2[0], equal_var=self.diff_size)
                    one_tailed_p_value=p_value
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    total=0
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[1],self.softUsInterSysData2[1], equal_var=self.diff_size)
                    one_tailed_p_value2=p_value
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[2],self.softUsInterSysData2[2], equal_var=self.diff_size)
                    one_tailed_p_value3=p_value
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[3],self.softUsInterSysData2[3], equal_var=self.diff_size)
                    one_tailed_p_value4=p_value
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value<0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[4],self.softUsInterSysData2[4], equal_var=self.diff_size)
                    one_tailed_p_value5=p_value
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterSysData[5],self.softUsInterSysData2[5], equal_var=self.diff_size)
                    one_tailed_p_value6=p_value
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###
                    ################################################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInfoData[0],self.softUsInfoData2[0], equal_var=self.diff_size)
                    one_tailed_p_value7=p_value
                    if one_tailed_p_value7>alpha:
                        res7 = 'No'
                        best7 = '/'
                    else:
                        res7 = 'Yes'
                        if t_value<0:
                            best7 = 'file 2'
                        else:
                            best7 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInfoData[1],self.softUsInfoData2[1], equal_var=self.diff_size)
                    one_tailed_p_value8=p_value
                    if one_tailed_p_value8>alpha:
                        res8 = 'No'
                        best8 = '/'
                    else:
                        res8 = 'Yes'
                        if t_value<0:
                            best8 = 'file 2'
                        else:
                            best8 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInfoData[2],self.softUsInfoData2[2], equal_var=self.diff_size)
                    one_tailed_p_value9=p_value
                    if one_tailed_p_value9>alpha:
                        res9 = 'No'
                        best9 = '/'
                    else:
                        res9 = 'Yes'
                        if t_value<0:
                            best9 = 'file 2'
                        else:
                            best9 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInfoData[3],self.softUsInfoData2[3], equal_var=self.diff_size)
                    one_tailed_p_value0=p_value
                    if one_tailed_p_value0>alpha:
                        res0 = 'No'
                        best0 = '/'
                    else:
                        res0 = 'Yes'
                        if t_value<0:
                            best0 = 'file 2'
                        else:
                            best0 = 'file 1'
                    ###
                    ##############################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterfaceData[0],self.softUsInterfaceData2[0], equal_var=self.diff_size)
                    one_tailed_p_value11=p_value
                    if one_tailed_p_value11>alpha:
                        res11 = 'No'
                        best11 = '/'
                    else:
                        res11 = 'Yes'
                        if t_value<0:
                            best11 = 'file 2'
                        else:
                            best11 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterfaceData[1],self.softUsInterfaceData2[1], equal_var=self.diff_size)
                    one_tailed_p_value12=p_value
                    if one_tailed_p_value12>alpha:
                        res12 = 'No'
                        best12 = '/'
                    else:
                        res12 = 'Yes'
                        if t_value<0:
                            best12 = 'file 2'
                        else:
                            best12 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.softUsInterfaceData[2],self.softUsInterfaceData2[2], equal_var=self.diff_size)
                    one_tailed_p_value13=p_value
                    if one_tailed_p_value13>alpha:
                        res13 = 'No'
                        best13 = '/'
                    else:
                        res13 = 'Yes'
                        if t_value<0:
                            best13 = 'file 2'
                        else:
                            best13 = 'file 1'
                    ###
                    #################################################################################################################################
                
                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['System'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                    d = {'categories': ['simplicity to use', 'helped effectivness of my work', 'helped pace of my work','confortable system', 'easy recovery after mistake', 'overall satisfaction'], 'file 1': [self.softUs[0][0], self.softUs[0][1],self.softUs[0][2], self.softUs[0][3], self.softUs[0][4], self.softUs[0][5]], 'file 2': [self.softUs2[0][0], self.softUs2[0][1],self.softUs2[0][2], self.softUs2[0][3], self.softUs2[0][4], self.softUs2[0][5]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res1, res2, res3, res4, res5, res6], 'best file': [best1, best2, best3, best4, best5, best6]}

                    df = pd.DataFrame(data=d)


                    dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Information'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff','best file' ])
                    d = {'categories': ['clear', 'easy to find', 'effective','organized'], 'file 1': [self.softUsInfo[0][0], self.softUsInfo[0][1],self.softUsInfo[0][2], self.softUsInfo[0][3]], 'file 2': [self.softUsInfo2[0][0], self.softUsInfo2[0][1],self.softUsInfo2[0][2], self.softUsInfo2[0][3]], 'p-value': [one_tailed_p_value7, one_tailed_p_value8, one_tailed_p_value9, one_tailed_p_value0],'significant diff': [res7, res8, res9, res0], 'best file': [best7, best8, best9, best0]}

                    df1 = pd.DataFrame(data=d)


                    dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interface'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                    d = {'categories': ['pleasant', 'I like using the interface', 'has all the functions and capabilities excpeted'], 'file 1': [self.softUsInterface[0][0], self.softUsInterface[0][1],self.softUsInterface[0][2]], 'file 2': [self.softUsInterface2[0][0], self.softUsInterface2[0][1],self.softUsInterface2[0][2]], 'p-value': [one_tailed_p_value11, one_tailed_p_value12, one_tailed_p_value13], 'significant diff': [res11, res12, res13], 'best file': [best11, best12, best13]}

                    df2 = pd.DataFrame(data=d)
                    frames = [dfmid, df, dfmid2,df1, dfmid3, df2]
                    tab = pd.concat(frames)
                    display(tab)

                if self.link=='dependant':
                    print('Sample: dependant')
                    #####################################################################################################################"
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[0],self.softUsInterSysData2[0])
                    one_tailed_p_value=p_value/2
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[1],self.softUsInterSysData2[1])
                    one_tailed_p_value2=p_value/2
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[2],self.softUsInterSysData2[2])
                    one_tailed_p_value3=p_value/2
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[3],self.softUsInterSysData2[3])
                    one_tailed_p_value4=p_value/2
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value<0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[4],self.softUsInterSysData2[4])
                    one_tailed_p_value5=p_value/2
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterSysData[5],self.softUsInterSysData2[5])
                    one_tailed_p_value6=p_value/2
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###
                    ################################################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInfoData[0],self.softUsInfoData2[0])
                    one_tailed_p_value7=p_value/2
                    if one_tailed_p_value7>alpha:
                        res7 = 'No'
                        best7 = '/'
                    else:
                        res7 = 'Yes'
                        if t_value<0:
                            best7 = 'file 2'
                        else:
                            best7 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInfoData[1],self.softUsInfoData2[1])
                    one_tailed_p_value8=p_value/2
                    if one_tailed_p_value8>alpha:
                        res8 = 'No'
                        best8 = '/'
                    else:
                        res8 = 'Yes'
                        if t_value<0:
                            best8 = 'file 2'
                        else:
                            best8 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInfoData[2],self.softUsInfoData2[2])
                    one_tailed_p_value9=p_value/2
                    if one_tailed_p_value9>alpha:
                        res9 = 'No'
                        best9 = '/'
                    else:
                        res9 = 'Yes'
                        if t_value<0:
                            best9 = 'file 2'
                        else:
                            best9 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInfoData[3],self.softUsInfoData2[3])
                    one_tailed_p_value0=p_value/2
                    if one_tailed_p_value0>alpha:
                        res0 = 'No'
                        best0 = '/'
                    else:
                        res0 = 'Yes'
                        if t_value<0:
                            best0 = 'file 2'
                        else:
                            best0 = 'file 1'
                    ###
                    ##############################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterfaceData[0],self.softUsInterfaceData2[0])
                    one_tailed_p_value11=p_value/2
                    if one_tailed_p_value11>alpha:
                        res11 = 'No'
                        best11 = '/'
                    else:
                        res11 = 'Yes'
                        if t_value<0:
                            best11 = 'file 2'
                        else:
                            best11 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterfaceData[1],self.softUsInterfaceData2[1])
                    one_tailed_p_value12=p_value/2
                    if one_tailed_p_value12>alpha:
                        res12 = 'No'
                        best12 = '/'
                    else:
                        res12 = 'Yes'
                        if t_value<0:
                            best12 = 'file 2'
                        else:
                            best12 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.softUsInterfaceData[2],self.softUsInterfaceData2[2])
                    one_tailed_p_value13=p_value/2
                    if one_tailed_p_value13>alpha:
                        res13 = 'No'
                        best13 = '/'
                    else:
                        res13 = 'Yes'
                        if t_value<0:
                            best13 = 'file 2'
                        else:
                            best13 = 'file 1'
                    ###
                    #################################################################################################################################
                
                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['System'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                    d = {'categories': ['simplicity to use', 'helped effectivness of my work', 'helped pace of my work','confortable system', 'easy recovery after mistake', 'overall satisfaction'], 'file 1': [self.softUs[0][0], self.softUs[0][1],self.softUs[0][2], self.softUs[0][3], self.softUs[0][4], self.softUs[0][5]], 'file 2': [self.softUs2[0][0], self.softUs2[0][1],self.softUs2[0][2], self.softUs2[0][3], self.softUs2[0][4], self.softUs2[0][5]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res1, res2, res3, res4, res5, res6], 'best file': [best1, best2, best3, best4, best5, best6]}

                    df = pd.DataFrame(data=d)


                    dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Information'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['clear', 'easy to find', 'effective','organized'], 'file 1': [self.softUsInfo[0][0], self.softUsInfo[0][1],self.softUsInfo[0][2], self.softUsInfo[0][3]], 'file 2': [self.softUsInfo2[0][0], self.softUsInfo2[0][1],self.softUsInfo2[0][2], self.softUsInfo2[0][3]], 'p-value': [one_tailed_p_value7, one_tailed_p_value8, one_tailed_p_value9, one_tailed_p_value0],'significant diff': [res7, res8, res9, res0], 'best file': [best7, best8, best9, best0]}

                    df1 = pd.DataFrame(data=d)


                    dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interface'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['pleasant', 'I like using the interface', 'has all the functions and capabilities excpeted'], 'file 1': [self.softUsInterface[0][0], self.softUsInterface[0][1],self.softUsInterface[0][2]], 'file 2': [self.softUsInterface2[0][0], self.softUsInterface2[0][1],self.softUsInterface2[0][2]], 'p-value': [one_tailed_p_value11, one_tailed_p_value12, one_tailed_p_value13], 'significant diff': [res11, res12, res13], 'best file': [best11, best12, best13]} 

                    df2 = pd.DataFrame(data=d)
                    frames = [dfmid, df, dfmid2,df1, dfmid3, df2]
                    tab = pd.concat(frames)
                    display(tab)      
            else: 
                print('type of test: z-test')
                
                #####################################################################################################################"
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[0],self.softUsInterSysData2[0])
                one_tailed_p_value=p_value
                if one_tailed_p_value<alpha:
                    res1 = 'No'
                    best1 = '/'
                else:
                    res1 = 'Yes'
                    if ztest_Score<0:
                        best1 = 'file 2'
                    else:
                        best1 = 'file 1'
                ###   
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[1],self.softUsInterSysData2[1])
                one_tailed_p_value2=p_value
                if one_tailed_p_value2<alpha:
                    res2 = 'No'
                    best2 = '/'
                else:
                    res2 = 'Yes'
                    if ztest_Score<0:
                        best2 = 'file 2'
                    else:
                        best2 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[2],self.softUsInterSysData2[2])
                one_tailed_p_value3=p_value
                if one_tailed_p_value3<alpha:
                    res3 = 'No'
                    best3 = '/'
                else:
                    res3 = 'Yes'
                    if ztest_Score<0:
                        best3 = 'file 2'
                    else:
                        best3 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[3],self.softUsInterSysData2[3])
                one_tailed_p_value4=p_value
                if one_tailed_p_value4<alpha:
                    res4 = 'No'
                    best4 = '/'
                else:
                    res4 = 'Yes'
                    if ztest_Score<0:
                        best4 = 'file 2'
                    else:
                        best4 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[4],self.softUsInterSysData2[4])
                one_tailed_p_value5=p_value
                if one_tailed_p_value5<alpha:
                    res5 = 'No'
                    best5 = '/'
                else:
                    res5 = 'Yes'
                    if ztest_Score<0:
                        best5 = 'file 2'
                    else:
                        best5 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterSysData[5],self.softUsInterSysData2[5])
                one_tailed_p_value6=p_value
                if one_tailed_p_value6<alpha:
                    res6 = 'No'
                    best6 = '/'
                else:
                    res6 = 'Yes'
                    if ztest_Score<0:
                        best6 = 'file 2'
                    else:
                        best6 = 'file 1'
                ###
                ################################################################################################################################################
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInfoData[0],self.softUsInfoData2[0])
                one_tailed_p_value7=p_value
                if one_tailed_p_value7<alpha:
                    res7 = 'No'
                    best7 = '/'
                else:
                    res7 = 'Yes'
                    if ztest_Score<0:
                        best7 = 'file 2'
                    else:
                        best7 = 'file 1'
                ###   
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInfoData[1],self.softUsInfoData2[1])
                one_tailed_p_value8=p_value
                if one_tailed_p_value8<alpha:
                    res8 = 'No'
                    best8 = '/'
                else:
                    res8 = 'Yes'
                    if ztest_Score<0:
                        best8 = 'file 2'
                    else:
                        best8 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInfoData[2],self.softUsInfoData2[2])
                one_tailed_p_value9=p_value
                if one_tailed_p_value9<alpha:
                    res9 = 'No'
                    best9 = '/'
                else:
                    res9 = 'Yes'
                    if ztest_Score<0:
                        best9 = 'file 2'
                    else:
                        best9 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInfoData[3],self.softUsInfoData2[3])
                one_tailed_p_value0=p_value
                if one_tailed_p_value0<alpha:
                    res0 = 'No'
                    best0 = '/'
                else:
                    res0 = 'Yes'
                    if ztest_Score<0:
                        best0 = 'file 2'
                    else:
                        best0 = 'file 1'
                ###
                ##############################################################################################################################
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterfaceData[0],self.softUsInterfaceData2[0])
                one_tailed_p_value11=p_value
                if one_tailed_p_value11<alpha:
                    res11 = 'No'
                    best11 = '/'
                else:
                    res11 = 'Yes'
                    if ztest_Score<0:
                        best11 = 'file 2'
                    else:
                        best11 = 'file 1'
                ###   
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterfaceData[1],self.softUsInterfaceData2[1])
                one_tailed_p_value12=p_value
                if one_tailed_p_value12<alpha:
                    res12 = 'No'
                    best12 = '/'
                else:
                    res12 = 'Yes'
                    if ztest_Score<0:
                        best12 = 'file 2'
                    else:
                        best12 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(self.softUsInterfaceData[2],self.softUsInterfaceData2[2])
                one_tailed_p_value13=p_value
                if one_tailed_p_value13<alpha:
                    res13 = 'No'
                    best13 = '/'
                else:
                    res13 = 'Yes'
                    if ztest_Score<0:
                        best13 = 'file 2'
                    else:
                        best13 = 'file 1'
                ###
                #################################################################################################################################

                dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['System'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                d = {'categories': ['simplicity to use', 'helped effectivness of my work', 'helped pace of my work','confortable system', 'easy recovery after mistake', 'overall satisfaction'], 'file 1': [self.softUs[0][0], self.softUs[0][1],self.softUs[0][2], self.softUs[0][3], self.softUs[0][4], self.softUs[0][5]], 'file 2': [self.softUs2[0][0], self.softUs2[0][1],self.softUs2[0][2], self.softUs2[0][3], self.softUs2[0][4], self.softUs2[0][5]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3, one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6], 'significant diff': [res1, res2, res3, res4, res5, res6], 'best file': [best1, best2, best3, best4, best5, best6]}

                df = pd.DataFrame(data=d)


                dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Information'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                d = {'categories': ['clear', 'easy to find', 'effective','organized'], 'file 1': [self.softUsInfo[0][0], self.softUsInfo[0][1],self.softUsInfo[0][2], self.softUsInfo[0][3]], 'file 2': [self.softUsInfo2[0][0], self.softUsInfo2[0][1],self.softUsInfo2[0][2], self.softUsInfo2[0][3]], 'p-value': [one_tailed_p_value7, one_tailed_p_value8, one_tailed_p_value9, one_tailed_p_value0],'significant diff': [res7, res8, res9, res0], 'best file': [best7, best8, best9, best0]}

                df1 = pd.DataFrame(data=d)


                dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interface'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                d = {'categories': ['pleasant', 'I like using the interface', 'has all the functions and capabilities excpeted'], 'file 1': [self.softUsInterface[0][0], self.softUsInterface[0][1],self.softUsInterface[0][2]], 'file 2': [self.softUsInterface2[0][0], self.softUsInterface2[0][1],self.softUsInterface2[0][2]], 'p-value': [one_tailed_p_value11, one_tailed_p_value12, one_tailed_p_value13], 'significant diff': [res11, res12, res13], 'best file': [best11, best12, best13]}

                df2 = pd.DataFrame(data=d)
                frames = [dfmid, df, dfmid2,df1, dfmid3, df2]
                tab = pd.concat(frames)
                display(tab)
            #pdf
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Usability.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Software_Usability.pdf"))    
                dfi.export(tab, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")

                
            
            
    def Software_Usability_Qual(self, save='display'):
        plt.rcParams["figure.figsize"] = (20,8)
        print('type of analysis: Qualitative')
        #System
        fig= plt.figure()
        fig.suptitle('System', fontsize=16)
        spec4 = fig.add_gridspec(ncols=2, nrows=6)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')
        
        
        #Simplicity to use
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_SystemQual[0][0],self.softUs_SystemQual[1][0], self.softUs_SystemQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Simplicity to use')
        #Simplicity to use
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.softUs_SystemQual2[0][0],self.softUs_SystemQual2[1][0], self.softUs_SystemQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Simplicity to use file 2')
        #helped effectivness of my work
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.softUs_SystemQual[0][1],self.softUs_SystemQual[1][1], self.softUs_SystemQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('helped effectivness of my work')
        #helped effectivness of my work
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.softUs_SystemQual2[0][1],self.softUs_SystemQual2[1][1], self.softUs_SystemQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('helped effectivness of my work file 2')
        #helped pace of my work
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.softUs_SystemQual[0][2],self.softUs_SystemQual[1][2], self.softUs_SystemQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('helped pace of my work')
        #helped pace of my work
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.softUs_SystemQual2[0][2],self.softUs_SystemQual2[1][2], self.softUs_SystemQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('helped pace of my work file 2')
        #confortable
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.softUs_SystemQual[0][3],self.softUs_SystemQual[1][3], self.softUs_SystemQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('confortable')
        #confortable
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.softUs_SystemQual2[0][3],self.softUs_SystemQual2[1][3], self.softUs_SystemQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('confortable file 2')
        #easy recovery after mistake
        ax5=fig.add_subplot(spec4[4, 0])
        ax5.pie([self.softUs_SystemQual[0][4],self.softUs_SystemQual[1][4], self.softUs_SystemQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('easy recovery after mistake')
        #easy recovery after mistake
        ax5=fig.add_subplot(spec4[4, 1])
        ax5.pie([self.softUs_SystemQual2[0][4],self.softUs_SystemQual2[1][4], self.softUs_SystemQual2[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('easy recovery after mistake file 2')
        #overall satisfaction
        ax6=fig.add_subplot(spec4[5, 0])
        ax6.pie([self.softUs_SystemQual[0][5],self.softUs_SystemQual[1][5], self.softUs_SystemQual[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('overall satisfaction')
        #overall satisfaction
        ax6=fig.add_subplot(spec4[5, 1])
        ax6.pie([self.softUs_SystemQual2[0][5],self.softUs_SystemQual2[1][5], self.softUs_SystemQual2[2][5]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax6.set_title('overall satisfaction file 2')
        
        fig.subplots_adjust(bottom=2, top=6)
         
        #######################################################################################################################################   
        #Information
        fig.suptitle('Information', fontsize=16)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=4)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')
        fig.subplots_adjust(bottom=2, top=5)
        
        #clear
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_InformationQual[0][0],self.softUs_InformationQual[1][0], self.softUs_InformationQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('clear')
        #clear
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.softUs_InformationQual2[0][0],self.softUs_InformationQual2[1][0], self.softUs_InformationQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('clear file 2')
        #easy to find
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.softUs_InformationQual[0][1],self.softUs_InformationQual[1][1], self.softUs_InformationQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('easy to find')
        #easy to find
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.softUs_InformationQual2[0][1],self.softUs_InformationQual2[1][1], self.softUs_InformationQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('easy to find file 2')
        #effective
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.softUs_InformationQual[0][2],self.softUs_InformationQual[1][2], self.softUs_InformationQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('effective')
        #effective
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.softUs_InformationQual2[0][2],self.softUs_InformationQual2[1][2], self.softUs_InformationQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('effective file 2')
        #organized
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.softUs_InformationQual[0][3],self.softUs_InformationQual[1][3], self.softUs_InformationQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('organized')
        #organized
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.softUs_InformationQual2[0][3],self.softUs_InformationQual2[1][3], self.softUs_InformationQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('organized file 2')
        
        
        
        
        ######################################################################################################################################
        #Interface
        fig.suptitle('Interface', fontsize=16)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=3)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')
            
        #pleasant
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.softUs_InterfaceQual[0][0],self.softUs_InterfaceQual[1][0], self.softUs_InterfaceQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('pleasant')
        #pleasant
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.softUs_InterfaceQual2[0][0],self.softUs_InterfaceQual2[1][0], self.softUs_InterfaceQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('pleasant file 2')
        #Like using interface
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.softUs_InterfaceQual[0][1],self.softUs_InterfaceQual[1][1], self.softUs_InterfaceQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('I like using interface')
         #Like using interface
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.softUs_InterfaceQual2[0][1],self.softUs_InterfaceQual2[1][1], self.softUs_InterfaceQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('I like using interface file 2')
        #fonctions and capabilities
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.softUs_InterfaceQual[0][2],self.softUs_InterfaceQual[1][2], self.softUs_InterfaceQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('has all the fonctions and capabilities expected')
        #fonctions and capabilities
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.softUs_InterfaceQual2[0][2],self.softUs_InterfaceQual2[1][2], self.softUs_InterfaceQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('has all the fonctions and capabilities expected file 2')
        
        fig.subplots_adjust(bottom=1, top=5)

        
        
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
            spec4 = fig.add_gridspec(ncols=1, nrows=6)
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
            
            #system com
            ax1=fig.add_subplot(spec4[1, 0])
            df = pd.DataFrame(self.com12[1])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('File 2: System: If it was difficult to recover from any mistake, please comment on the problems.')
        
            #information com
            ax1=fig.add_subplot(spec4[2, 0])
            df = pd.DataFrame(self.com1[2])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('Information:if any information was not clear, what difficulties did you face?')
            
            #information com
            ax1=fig.add_subplot(spec4[3, 0])
            df = pd.DataFrame(self.com12[2])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('File 2: Information:if any information was not clear, what difficulties did you face?')
            
            #interface com
            ax1=fig.add_subplot(spec4[4, 0])
            df = pd.DataFrame(self.com1[3])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('What functions and capabilities would you like to see in this system?')
            
            #interface com
            ax1=fig.add_subplot(spec4[5, 0])
            df = pd.DataFrame(self.com12[3])
            df = df.fillna(' ')
            stopwords = set(STOPWORDS)
            wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(str(df))
            ax1.imshow(wordcloud, interpolation='bilinear')
            ax1.axis("off")
            ax1.set_title('File 2: What functions and capabilities would you like to see in this system?')
            
            if save=='pdf' or type=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Usability_coments.pdf"))
                fig.savefig(path,  bbox_inches='tight')
                print("pdf downloaded !")
                
        else:
            
            coments = list(zip(self.com1[1],self.com1[2], self.com1[3]))
            df = pd.DataFrame(coments, index =self.com1[0],columns =['System: If it was difficult to recover from any mistake, please comment on the problems.', 'Information:if any information was not clear, what difficulties did you face?', 'What functions and capabilities would you like to see in this system?'])
            
            coments = list(zip(self.com12[1],self.com12[2], self.com12[3]))
            df1 = pd.DataFrame(coments, index =self.com12[0],columns =['System: If it was difficult to recover from any mistake, please comment on the problems.', 'Information:if any information was not clear, what difficulties did you face?', 'What functions and capabilities would you like to see in this system?'])
            dfmid = pd.DataFrame([[' ', ' ', ' ']], index = ['file 2'], columns =['System: If it was difficult to recover from any mistake, please comment on the problems.', 'Information:if any information was not clear, what difficulties did you face?', 'What functions and capabilities would you like to see in this system?'])
            frames = [df,dfmid ,df1]
            tab = pd.concat(frames)
            
            tab = tab.style.format(na_rep='No Coments').set_table_styles([
                                {
                                    "selector":"thead",
                                    "props": [("background-color", "gray"),
                                              ]
                                },
                                {
                                    "selector":".row"+str(len(df)),
                                    "props": [("background-color", "gray"),
                                              ]
                                },

                            ])
            display (tab)
            

            
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Software_Coments.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Software_Usability_coments.pdf"))    
                dfi.export(tab, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")
        


            
        #Software Usability
    def Searching_Learning(self, format,save='notActivated', alpha=0.05 ):      
        if type(save) != str:alpha=save
        print('type of analysis: Quantitative')
        if format=='graph':
            plt.rcParams["figure.figsize"] = (16,8)
            fig= plt.figure()
            index = np.arange(3)
            width = 0.35

            #First bar chart/table
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

            ax1.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            ax1.axhline(y=3.5, color='black')
            ax1.set_title('Search formulation (Per Search)')
            ax1.set_xticks([])    


            mean = self.PreSearch2
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]                   
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')
            ax1.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax1.axhline(y=3.5, color='black')
            ax1.set_xticks([])


            colorMean=[]
            mean2=[[]]
            mean2[0].append(self.PreSearch[0][0])
            mean2[0].append(self.PreSearch2[0][0])
            mean2[0].append(self.PreSearch[0][1])
            mean2[0].append(self.PreSearch2[0][1])
            mean2[0].append(self.PreSearch[0][2])
            mean2[0].append(self.PreSearch2[0][2])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['Background Knowledge','file2', 'Interest in Topic','file 2', 'Anticipated Difficulty', 'file 2']        
            ytable = ax1.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
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



            ###
            #Second bar chart/table
            index = np.arange(5)
            ax2= fig.add_subplot(4,1,2)
            columns = ['actual Difficulty', 'text presentation quality', 'average number of docs viewed per search', 'the usefulness of Search Results', 'text relevance']
            mean = self.ContentSelection
            colorMean=[]                     
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            ax2.bar(index- width/2, mean[0], color=colorMean, width = 0.25)

            mean=self.ContentSelection2                  
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]                   
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')                 
            ax2.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax2.axhline(y=3.5, color='black')
            ax2.set_title('Content Selection')
            ax2.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.ContentSelection[0][0])
            mean2[0].append(self.ContentSelection2[0][0])
            mean2[0].append(self.ContentSelection[0][1])
            mean2[0].append(self.ContentSelection2[0][1])
            mean2[0].append(self.ContentSelection[0][2])
            mean2[0].append(self.ContentSelection2[0][2])
            mean2[0].append(self.ContentSelection[0][3])
            mean2[0].append(self.ContentSelection2[0][3])
            mean2[0].append(self.ContentSelection[0][4])
            mean2[0].append(self.ContentSelection2[0][4])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['actual difficulty f1', 'f2','text presentation quality f1','f2', 'average number of docs viewed per search f1','f2', 'the usefulness of search results f1','f2', 'text relevance f1', 'f2']
            wtable = ax2.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            wtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= wtable[(0,i)]
                cell.set_height(.1)
                wtable[(1, i)].set_facecolor(colorMean[i])
                for j in range(0,2):
                    cell= wtable[(j,i)]
                    cell.set_height(.15)

            cell = wtable[1, -1]
            cell.set_height(.15)        

            ###
            #Third bar chart/table
            index = np.arange(4)
            ax3= fig.add_subplot(4,1,3)
            columns = ['cognitively engaged', 'suggestions skills', 'system understanding input', 'average level of satisfaction']
            mean = self.InteractionContent
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            ax3.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            ax3.axhline(y=3.5, color='black')
            ax3.set_xticks([])


            mean=self.InteractionContent2                  
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')                
            ax3.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax3.axhline(y=3.5, color='black')
            ax3.set_title('Interaction with content')
            ax3.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.InteractionContent[0][0])
            mean2[0].append(self.InteractionContent2[0][0])
            mean2[0].append(self.InteractionContent[0][1])
            mean2[0].append(self.InteractionContent2[0][1])
            mean2[0].append(self.InteractionContent[0][2])
            mean2[0].append(self.InteractionContent2[0][2])
            mean2[0].append(self.InteractionContent[0][3])
            mean2[0].append(self.InteractionContent2[0][3])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')

            columns = ['cognitively engaged f1', 'f2', 'suggestions skills f1','f2', 'system understanding input f1','f2', 'average level of satisfaction f1', 'f2']
            xtable = ax3.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            xtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= xtable[(0,i)]
                cell.set_height(.1)
                xtable[(1, i)].set_facecolor(colorMean[i])
                for j in range(0,2):
                    cell= xtable[(j,i)]
                    cell.set_height(.15)

            cell = xtable[1, -1]
            cell.set_height(.15) 

            ###

            #
            index = np.arange(4)
            ax4= fig.add_subplot(4,1,4)
            columns = ['search succes', 'presentation of the search results', 'expansion of Knowledge after the search', 'understanding about the topic']
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

            ax4.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            ax4.axhline(y=3.5, color='black')
            ax4.set_xticks([])


            mean=self.PostSearch2                  
            colorMean=[]
            roundMean=[round(mean, 1) for mean in mean[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')                
            ax4.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)
            ax4.axhline(y=3.5, color='black')
            ax4.set_title('Post Search')
            ax4.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.PostSearch[0][0])
            mean2[0].append(self.PostSearch2[0][0])
            mean2[0].append(self.PostSearch[0][1])
            mean2[0].append(self.PostSearch2[0][1])
            mean2[0].append(self.PostSearch[0][2])
            mean2[0].append(self.PostSearch2[0][2])
            mean2[0].append(self.PostSearch[0][3])
            mean2[0].append(self.PostSearch2[0][3])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')


            columns = ['search success f1','f2',  'presentation of the search results f1','f2', 'expansion of Knowledge after the search f1', 'f2', 'understanding about the topic f1', 'f2']
            xtable = ax4.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')
            xtable.auto_set_column_width(-1)

            #Size table
            for i in range(0,len(columns)):
                cell= xtable[(0,i)]
                cell.set_height(.1)
                xtable[(1, i)].set_facecolor(colorMean[i])
                for j in range(0,2):
                    cell= xtable[(j,i)]
                    cell.set_height(.15)

            cell = xtable[1, -1]
            cell.set_height(.15)
            fig.subplots_adjust(bottom=2, top=4, hspace=0.5)
            
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Searching_Learning.pdf"))
                fig.savefig(path,  bbox_inches='tight')
                print("pdf downloaded !")
        
        if format=='tab':
            #if test arn't the same size, one of the sample is inferieur to 30 and parameter arn't changed
            if (not self.diff_size or self.size<=30) and not self.parameter:
                print('type of test: t-test')
                print("level of significance: "+str(alpha))
                if self.link=='independant':
                    print('Sample: independant')
                    ###################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PreSearchData[0],self.PreSearchData2[0], equal_var=self.diff_size)
                    one_tailed_p_value=p_value
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PreSearchData[1],self.PreSearchData2[1], equal_var=self.diff_size)
                    one_tailed_p_value2=p_value
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PreSearchData[2],self.PreSearchData2[2], equal_var=self.diff_size)
                    one_tailed_p_value3=p_value
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    #######################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.ContentSelectionData[0],self.ContentSelectionData2[0], equal_var=self.diff_size)
                    one_tailed_p_value4=p_value
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value<0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.ContentSelectionData[1],self.ContentSelectionData2[1], equal_var=self.diff_size)
                    one_tailed_p_value5=p_value
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.ContentSelectionData[2],self.ContentSelectionData2[2], equal_var=self.diff_size)
                    one_tailed_p_value6=p_value
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###

                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.ContentSelectionData[3],self.ContentSelectionData2[3], equal_var=self.diff_size)
                    one_tailed_p_value7=p_value
                    if one_tailed_p_value7>alpha:
                        res7 = 'No'
                        best7 = '/'
                    else:
                        res7 = 'Yes'
                        if t_value<0:
                            best7 = 'file 2'
                        else:
                            best7 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.ContentSelectionData[4],self.ContentSelectionData2[4], equal_var=self.diff_size)
                    one_tailed_p_value8=p_value
                    if one_tailed_p_value8>alpha:
                        res8 = 'No'
                        best8 = '/'
                    else:
                        res8 = 'Yes'
                        if t_value<0:
                            best8 = 'file 2'
                        else:
                            best8 = 'file 1'
                    ###
                    #####################################################################################################################"
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.InteractionContentData[0],self.InteractionContentData2[0], equal_var=self.diff_size)
                    one_tailed_p_value9=p_value
                    if one_tailed_p_value9>alpha:
                        res9 = 'No'
                        best9 = '/'
                    else:
                        res9 = 'Yes'
                        if t_value<0:
                            best9 = 'file 2'
                        else:
                            best9 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.InteractionContentData[1],self.InteractionContentData2[1], equal_var=self.diff_size)
                    one_tailed_p_value0=p_value
                    if one_tailed_p_value0>alpha:
                        res0 = 'No'
                        best0 = '/'
                    else:
                        res0 = 'Yes'
                        if t_value<0:
                            best0 = 'file 2'
                        else:
                            best0 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.InteractionContentData[2],self.InteractionContentData2[2], equal_var=self.diff_size)
                    one_tailed_p_value11=p_value
                    if one_tailed_p_value11>alpha:
                        res11 = 'No'
                        best11 = '/'
                    else:
                        res11 = 'Yes'
                        if t_value<0:
                            best11 = 'file 2'
                        else:
                            best11 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.InteractionContentData[3],self.InteractionContentData2[3], equal_var=self.diff_size)
                    one_tailed_p_value12=p_value
                    if one_tailed_p_value12>alpha:
                        res12 = 'No'
                        best12 = '/'
                    else:
                        res12 = 'Yes'
                        if t_value<0:
                            best12 = 'file 2'
                        else:
                            best12 = 'file 1'
                    ###
                    ##############################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PostSearchData[0],self.PostSearchData2[0], equal_var=self.diff_size)
                    one_tailed_p_value13=p_value
                    if one_tailed_p_value13>alpha:
                        res13 = 'No'
                        best13 = '/'
                    else:
                        res13 = 'Yes'
                        if t_value<0:
                            best13 = 'file 2'
                        else:
                            best13 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PostSearchData[1],self.PostSearchData2[1], equal_var=self.diff_size)
                    one_tailed_p_value14=p_value
                    if one_tailed_p_value14>alpha:
                        res14 = 'No'
                        best14 = '/'
                    else:
                        res14 = 'Yes'
                        if t_value<0:
                            best14 = 'file 2'
                        else:
                            best14 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PostSearchData[2],self.PostSearchData2[2], equal_var=self.diff_size)
                    one_tailed_p_value15=p_value
                    if one_tailed_p_value15>alpha:
                        res15 = 'No'
                        best15 = '/'
                    else:
                        res15 = 'Yes'
                        if t_value<0:
                            best15 = 'file 2'
                        else:
                            best15 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.PostSearchData[3],self.PostSearchData2[3], equal_var=self.diff_size)
                    one_tailed_p_value16=p_value
                    if one_tailed_p_value16>alpha:
                        res16 = 'No'
                        best16 = '/'
                    else:
                        res16 = 'Yes'
                        if t_value<0:
                            best16 = 'file 2'
                        else:
                            best16 = 'file 1'
                    ###
                    
                    t_value,p_value=stats.ttest_ind(self.PostSearchData[3],self.PostSearchData2[3], equal_var=self.diff_size)
                    print(str(p_value))

                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Search Formulation'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['background Knowledge', 'interest in topic', 'anticipated difficulty'], 'file 1': [self.PreSearch[0][0], self.PreSearch[0][1],self.PreSearch[0][2]], 'file 2': [self.PreSearch2[0][0], self.PreSearch2[0][1],self.PreSearch2[0][2]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                    df = pd.DataFrame(data=d)

                    dfmid1 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Content Selection'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['actual difficulty', 'text presentation quality', 'average number of doc view per search','the usefullness of search results', 'text relevance'], 'file 1': [self.ContentSelection[0][0], self.ContentSelection[0][1],self.ContentSelection[0][2],self.ContentSelection[0][3],self.ContentSelection[0][4]], 'file 2': [self.ContentSelection2[0][0], self.ContentSelection2[0][1],self.ContentSelection2[0][2],self.ContentSelection2[0][3],self.ContentSelection2[0][4]], 'p-value': [one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6,one_tailed_p_value7, one_tailed_p_value8], 'significant diff': [res4, res5, res6, res7, res8], 'best file': [best4, best5, best6, best7, best8] }
                    df1 = pd.DataFrame(data=d)

                    dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interaction with content'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                    d = {'categories': ['cognitively engaged', 'suggestion skills', 'system understanding input', 'average level of satisfaction'], 'file 1': [self.InteractionContent[0][0], self.InteractionContent[0][1],self.InteractionContent[0][2],self.InteractionContent[0][3]], 'file 2': [self.InteractionContent2[0][0], self.InteractionContent2[0][1],self.InteractionContent2[0][2],self.InteractionContent2[0][3]], 'p-value': [one_tailed_p_value9, one_tailed_p_value0,one_tailed_p_value11, one_tailed_p_value12], 'significant diff': [res9, res0, res11, res12], 'best file': [best9, best0, best11, best12] }
                    df2 = pd.DataFrame(data=d)

                    dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Post-Search'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff','best file' ])
                    d = {'categories': ['search success', 'presentation of the search results', 'expansion of Knowledge after the search', 'understanding about the topic'], 'file 1': [self.PostSearch[0][0], self.PostSearch[0][1],self.PostSearch[0][2],self.PostSearch[0][3]], 'file 2': [self.PostSearch2[0][0], self.PostSearch2[0][1],self.PostSearch2[0][2],self.PostSearch2[0][3]], 'p-value': [one_tailed_p_value13, one_tailed_p_value14,one_tailed_p_value15, one_tailed_p_value16], 'significant diff': [res13, res14, res15, res16], 'best file': [best13, best14, best15, best16]}
                    df3 = pd.DataFrame(data=d)


                    frames = [dfmid, df, dfmid1,df1, dfmid2, df2,  dfmid3, df3]
                    tab = pd.concat(frames)
                    display(tab)
                    
                if self.link=='dependant':
                    print('Sample: dependant')
                    ###################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PreSearchData[0],self.PreSearchData2[0])
                    one_tailed_p_value=p_value/2
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PreSearchData[1],self.PreSearchData2[1])
                    one_tailed_p_value2=p_value/2
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PreSearchData[2],self.PreSearchData2[2])
                    one_tailed_p_value3=p_value/2
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    #######################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.ContentSelectionData[0],self.ContentSelectionData2[0])
                    one_tailed_p_value4=p_value/2
                    if one_tailed_p_value4>alpha:
                        res4 = 'No'
                        best4 = '/'
                    else:
                        res4 = 'Yes'
                        if t_value<0:
                            best4 = 'file 2'
                        else:
                            best4 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.ContentSelectionData[1],self.ContentSelectionData2[1])
                    one_tailed_p_value5=p_value/2
                    if one_tailed_p_value5>alpha:
                        res5 = 'No'
                        best5 = '/'
                    else:
                        res5 = 'Yes'
                        if t_value<0:
                            best5 = 'file 2'
                        else:
                            best5 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.ContentSelectionData[2],self.ContentSelectionData2[2])
                    one_tailed_p_value6=p_value/2
                    if one_tailed_p_value6>alpha:
                        res6 = 'No'
                        best6 = '/'
                    else:
                        res6 = 'Yes'
                        if t_value<0:
                            best6 = 'file 2'
                        else:
                            best6 = 'file 1'
                    ###

                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.ContentSelectionData[3],self.ContentSelectionData2[3])
                    one_tailed_p_value7=p_value/2
                    if one_tailed_p_value7>alpha:
                        res7 = 'No'
                        best7 = '/'
                    else:
                        res7 = 'Yes'
                        if t_value<0:
                            best7 = 'file 2'
                        else:
                            best7 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.ContentSelectionData[4],self.ContentSelectionData2[4])
                    one_tailed_p_value8=p_value/2
                    if one_tailed_p_value8>alpha:
                        res8 = 'No'
                        best8 = '/'
                    else:
                        res8 = 'Yes'
                        if t_value<0:
                            best8 = 'file 2'
                        else:
                            best8 = 'file 1'
                    ###
                    #####################################################################################################################"
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.InteractionContentData[0],self.InteractionContentData2[0])
                    one_tailed_p_value9=p_value/2
                    if one_tailed_p_value9>alpha:
                        res9 = 'No'
                        best9 = '/'
                    else:
                        res9 = 'Yes'
                        if t_value<0:
                            best9 = 'file 2'
                        else:
                            best9 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.InteractionContentData[1],self.InteractionContentData2[1])
                    one_tailed_p_value0=p_value/2
                    if one_tailed_p_value0>alpha:
                        res0 = 'No'
                        best0 = '/'
                    else:
                        res0 = 'Yes'
                        if t_value<0:
                            best0 = 'file 2'
                        else:
                            best0 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.InteractionContentData[2],self.InteractionContentData2[2])
                    one_tailed_p_value11=p_value/2
                    if one_tailed_p_value11>alpha:
                        res11 = 'No'
                        best11 = '/'
                    else:
                        res11 = 'Yes'
                        if t_value<0:
                            best11 = 'file 2'
                        else:
                            best11 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.InteractionContentData[3],self.InteractionContentData2[3])
                    one_tailed_p_value12=p_value/2
                    if one_tailed_p_value12>alpha:
                        res12 = 'No'
                        best12 = '/'
                    else:
                        res12 = 'Yes'
                        if t_value<0:
                            best12 = 'file 2'
                        else:
                            best12 = 'file 1'
                    ###
                    ##############################################################################################################################
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PostSearchData[0],self.PostSearchData2[0])
                    one_tailed_p_value13=p_value/2
                    if one_tailed_p_value13>alpha:
                        res13 = 'No'
                        best13 = '/'
                    else:
                        res13 = 'Yes'
                        if t_value<0:
                            best13 = 'file 2'
                        else:
                            best13 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PostSearchData[1],self.PostSearchData2[1])
                    one_tailed_p_value14=p_value/2
                    if one_tailed_p_value14>alpha:
                        res14 = 'No'
                        best14 = '/'
                    else:
                        res14 = 'Yes'
                        if t_value<0:
                            best14 = 'file 2'
                        else:
                            best14 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PostSearchData[2],self.PostSearchData2[2])
                    one_tailed_p_value15=p_value/2
                    if one_tailed_p_value15>alpha:
                        res15 = 'No'
                        best15 = '/'
                    else:
                        res15 = 'Yes'
                        if t_value<0:
                            best15 = 'file 2'
                        else:
                            best15 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.PostSearchData[3],self.PostSearchData2[3])
                    one_tailed_p_value16=p_value/2
                    if one_tailed_p_value16>alpha:
                        res16 = 'No'
                        best16 = '/'
                    else:
                        res16 = 'Yes'
                        if t_value<0:
                            best16 = 'file 2'
                        else:
                            best16 = 'file 1'
                    ###

                    dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Search formulation'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['background Knowledge', 'interest in topic', 'anticipated difficulty'], 'file 1': [self.PreSearch[0][0], self.PreSearch[0][1],self.PreSearch[0][2]], 'file 2': [self.PreSearch2[0][0], self.PreSearch2[0][1],self.PreSearch2[0][2]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                    df = pd.DataFrame(data=d)

                    dfmid1 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Content Selection'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                    d = {'categories': ['actual difficulty', 'text presentation quality', 'average number of doc view per search','the usefullness of search results', 'text relevance'], 'file 1': [self.ContentSelection[0][0], self.ContentSelection[0][1],self.ContentSelection[0][2],self.ContentSelection[0][3],self.ContentSelection[0][4]], 'file 2': [self.ContentSelection2[0][0], self.ContentSelection2[0][1],self.ContentSelection2[0][2],self.ContentSelection2[0][3],self.ContentSelection2[0][4]], 'p-value': [one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6,one_tailed_p_value7, one_tailed_p_value8], 'significant diff': [res4, res5, res6, res7, res8], 'best file': [best4, best5, best6, best7, best8] }
                    df1 = pd.DataFrame(data=d)

                    dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interaction with content'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                    d = {'categories': ['cognitively engaged', 'suggestion skills', 'system understanding input', 'average level of satisfaction'], 'file 1': [self.InteractionContent[0][0], self.InteractionContent[0][1],self.InteractionContent[0][2],self.InteractionContent[0][3]], 'file 2': [self.InteractionContent2[0][0], self.InteractionContent2[0][1],self.InteractionContent2[0][2],self.InteractionContent2[0][3]], 'p-value': [one_tailed_p_value9, one_tailed_p_value0,one_tailed_p_value11, one_tailed_p_value12], 'significant diff': [res9, res0, res11, res12], 'best file': [best9, best0, best11, best12] }
                    df2 = pd.DataFrame(data=d)

                    dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Post-Search'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff','best file' ])
                    d = {'categories': ['search success', 'presentation of the search results', 'expansion of Knowledge after the search', 'understanding about the topic'], 'file 1': [self.PostSearch[0][0], self.PostSearch[0][1],self.PostSearch[0][2],self.PostSearch[0][3]], 'file 2': [self.PostSearch2[0][0], self.PostSearch2[0][1],self.PostSearch2[0][2],self.PostSearch2[0][3]], 'p-value': [one_tailed_p_value13, one_tailed_p_value14,one_tailed_p_value15, one_tailed_p_value16], 'significant diff': [res13, res14, res15, res16], 'best file': [best13, best14, best15, best16]}
                    df3 = pd.DataFrame(data=d)


                    frames = [dfmid, df, dfmid1,df1, dfmid2, df2,  dfmid3, df3]
                    tab = pd.concat(frames)
                    display(tab)



            else:
                ### z-test 
                print('type of test: z-test')
                ztest_Score, p_value= ztest(x1=self.PreSearchData[0], x2=self.PreSearchData2[0])
                one_tailed_p_value1=p_value
                if one_tailed_p_value1<alpha:
                    res1 = 'No'
                    best1 = '/'
                else:
                    res1 = 'Yes'
                    if ztest_Score<0:
                        best1 = 'file 2'
                    else:
                        best1 = 'file 1'
                ###   
                ### z-test 
                ztest_Score, p_value= ztest(x1=self.PreSearchData[1], x2=self.PreSearchData2[1])
                one_tailed_p_value2=p_value
                if one_tailed_p_value2<alpha:
                    res2 = 'No'
                    best2 = '/'
                else:
                    res2 = 'Yes'
                    if ztest_Score<0:
                        best2 = 'file 2'
                    else:
                        best2 = 'file 1'
                ###   
                ### z test 
                ztest_Score, p_value= ztest(x1=self.PreSearchData[2], x2=self.PreSearchData2[2])
                one_tailed_p_value3=p_value
                if one_tailed_p_value3<alpha:
                    res3 = 'No'
                    best3 = '/'
                else:
                    res3 = 'Yes'
                    if ztest_Score<0:
                        best3 = 'file 2'
                    else:
                        best3 = 'file 1'
                ###
                #######################################################################################################################
                ### z test 
                ztest_Score, p_value= ztest(x1=self.ContentSelectionData[0], x2=self.ContentSelectionData2[0])
                one_tailed_p_value4=p_value
                if one_tailed_p_value4<alpha:
                    res4 = 'No'
                    best4 = '/'
                else:
                    res4 = 'Yes'
                    if ztest_Score<0:
                        best4 = 'file 2'
                    else:
                        best4 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.ContentSelectionData[1], x2=self.ContentSelectionData2[1])
                one_tailed_p_value5=p_value
                if one_tailed_p_value5<alpha:
                    res5 = 'No'
                    best5 = '/'
                else:
                    res5 = 'Yes'
                    if ztest_Score<0:
                        best5 = 'file 2'
                    else:
                        best5 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.ContentSelectionData[2], x2=self.ContentSelectionData2[2])
                one_tailed_p_value6=p_value
                if one_tailed_p_value6<alpha:
                    res6 = 'No'
                    best6 = '/'
                else:
                    res6 = 'Yes'
                    if ztest_Score<0:
                        best6 = 'file 2'
                    else:
                        best6 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.ContentSelectionData[3], x2=self.ContentSelectionData2[3])
                one_tailed_p_value7=p_value
                if one_tailed_p_value7<alpha:
                    res7 = 'No'
                    best7 = '/'
                else:
                    res7 = 'Yes'
                    if ztest_Score<0:
                        best7 = 'file 2'
                    else:
                        best7 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.ContentSelectionData[4], x2=self.ContentSelectionData2[4])
                one_tailed_p_value8=p_value
                if one_tailed_p_value8<alpha:
                    res8 = 'No'
                    best8 = '/'
                else:
                    res8 = 'Yes'
                    if ztest_Score<0:
                        best8 = 'file 2'
                    else:
                        best8 = 'file 1'
                ###
                #######################################################################################################################################
                ### z test 
                ztest_Score, p_value= ztest(x1=self.InteractionContentData[0], x2=self.InteractionContentData2[0])
                one_tailed_p_value9=p_value
                if one_tailed_p_value9<alpha:
                    res9 = 'No'
                    best9 = '/'
                else:
                    res9 = 'Yes'
                    if ztest_Score<0:
                        best9 = 'file 2'
                    else:
                        best9 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.InteractionContentData[1], x2=self.InteractionContentData2[1])
                one_tailed_p_value0=p_value
                if one_tailed_p_value0<alpha:
                    res0 = 'No'
                    best0 = '/'
                else:
                    res0 = 'Yes'
                    if ztest_Score<0:
                        best0 = 'file 2'
                    else:
                        best0 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.InteractionContentData[2], x2=self.InteractionContentData2[2])
                one_tailed_p_value11=p_value
                if one_tailed_p_value11<alpha:
                    res11 = 'No'
                    best11 = '/'
                else:
                    res11 = 'Yes'
                    if ztest_Score<0:
                        best11 = 'file 2'
                    else:
                        best11 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.InteractionContentData[3], x2=self.InteractionContentData2[3])
                one_tailed_p_value12=p_value
                if one_tailed_p_value12<alpha:
                    res12 = 'No'
                    best12 = '/'
                else:
                    res12 = 'Yes'
                    if ztest_Score<0:
                        best12 = 'file 2'
                    else:
                        best12 = 'file 1'
                ###
                #################################################################################################################################
                ### z test 
                ztest_Score, p_value= ztest(x1=self.PostSearchData[0], x2=self.PostSearchData2[0])
                one_tailed_p_value13=p_value
                if one_tailed_p_value13<alpha:
                    res13 = 'No'
                    best13 = '/'
                else:
                    res13 = 'Yes'
                    if ztest_Score<0:
                        best13 = 'file 2'
                    else:
                        best13 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.PostSearchData[1], x2=self.PostSearchData2[1])
                one_tailed_p_value14=p_value
                if one_tailed_p_value14<alpha:
                    res14 = 'No'
                    best14 = '/'
                else:
                    res14 = 'Yes'
                    if ztest_Score<0:
                        best14 = 'file 2'
                    else:
                        best14 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.PostSearchData[2], x2=self.PostSearchData2[2])
                one_tailed_p_value15=p_value
                if one_tailed_p_value15<alpha:
                    res15 = 'No'
                    best15 = '/'
                else:
                    res15 = 'Yes'
                    if ztest_Score<0:
                        best15 = 'file 2'
                    else:
                        best15 = 'file 1'
                ###
                ### z test 
                ztest_Score, p_value= ztest(x1=self.PostSearchData[3], x2=self.PostSearchData2[3])
                one_tailed_p_value16=p_value
                if one_tailed_p_value16<alpha:
                    res16 = 'No'
                    best16 = '/'
                else:
                    res16 = 'Yes'
                    if ztest_Score<0:
                        best16 = 'file 2'
                    else:
                        best16 = 'file 1'
                ###
                dfmid = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Search formulation'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                d = {'categories': ['background Knowledge', 'interest in topic', 'anticipated difficulty'], 'file 1': [self.PreSearch[0][0], self.PreSearch[0][1],self.PreSearch[0][2]], 'file 2': [self.PreSearch2[0][0], self.PreSearch2[0][1],self.PreSearch2[0][2]], 'p-value': [one_tailed_p_value1, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                df = pd.DataFrame(data=d)

                dfmid1 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Content Selection'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff', 'best file' ])
                d = {'categories': ['actual difficulty', 'text presentation quality', 'average number of doc view per search','the usefullness of search results', 'text relevance'], 'file 1': [self.ContentSelection[0][0], self.ContentSelection[0][1],self.ContentSelection[0][2],self.ContentSelection[0][3],self.ContentSelection[0][4]], 'file 2': [self.ContentSelection2[0][0], self.ContentSelection2[0][1],self.ContentSelection2[0][2],self.ContentSelection2[0][3],self.ContentSelection2[0][4]], 'p-value': [one_tailed_p_value4, one_tailed_p_value5, one_tailed_p_value6,one_tailed_p_value7, one_tailed_p_value8], 'significant diff': [res4, res5, res6, res7, res8], 'best file': [best4, best5, best6, best7, best8] }
                df1 = pd.DataFrame(data=d)

                dfmid2 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Interaction with content'], columns =['categories', 'file 1', 'file 2','p-value','significant diff', 'best file' ])
                d = {'categories': ['cognitively engaged', 'suggestion skills', 'system understanding input', 'average level of satisfaction'], 'file 1': [self.InteractionContent[0][0], self.InteractionContent[0][1],self.InteractionContent[0][2],self.InteractionContent[0][3]], 'file 2': [self.InteractionContent2[0][0], self.InteractionContent2[0][1],self.InteractionContent2[0][2],self.InteractionContent2[0][3]], 'p-value': [one_tailed_p_value9, one_tailed_p_value0,one_tailed_p_value11, one_tailed_p_value12], 'significant diff': [res9, res0, res11, res12], 'best file': [best9, best0, best11, best12] }
                df2 = pd.DataFrame(data=d)

                dfmid3 = pd.DataFrame([[' ', ' ', ' ', ' ', ' ', ' ']], index = ['Post-Search'], columns =['categories', 'file 1', 'file 2','p-value', 'significant diff','best file' ])
                d = {'categories': ['search success', 'presentation of the search results', 'expansion of Knowledge after the search', 'understanding about the topic'], 'file 1': [self.PostSearch[0][0], self.PostSearch[0][1],self.PostSearch[0][2],self.PostSearch[0][3]], 'file 2': [self.PostSearch2[0][0], self.PostSearch2[0][1],self.PostSearch2[0][2],self.PostSearch2[0][3]], 'p-value': [one_tailed_p_value13, one_tailed_p_value14,one_tailed_p_value15, one_tailed_p_value16], 'significant diff': [res13, res14, res15, res16], 'best file': [best13, best14, best15, best16]}
                df3 = pd.DataFrame(data=d)


                frames = [dfmid, df, dfmid1,df1, dfmid2, df2,  dfmid3, df3]
                tab = pd.concat(frames)
                display(tab)
            
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Searching_learning.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Searching_learning.pdf"))    
                dfi.export(tab, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")

        
        
        
        
    def Searching_Learning_Qual(self, save='display'):
        
        print('type of analysis: Qualitative')
        plt.rcParams["figure.figsize"] = (20,8)
        
        #Search formulation (Per-earch)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=3)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Background Knowledge
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.PreSearchQual[0][0],self.PreSearchQual[1][0], self.PreSearchQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Background Knowledge')
        #Background Knowledge
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.PreSearchQual2[0][0],self.PreSearchQual2[1][0], self.PreSearchQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Background Knowledge file 2')
        #Interest in topic
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.PreSearchQual[0][1],self.PreSearchQual[1][1], self.PreSearchQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Interest in topic')
        #Interest in topic
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.PreSearchQual2[0][1],self.PreSearchQual2[1][1], self.PreSearchQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Interest in topic file 2')
        #Anticipated difficulty
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.PreSearchQual[0][2],self.PreSearchQual[1][2], self.PreSearchQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Anticipated difficulty')
        #Anticipated difficulty
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.PreSearchQual2[0][2],self.PreSearchQual2[1][2], self.PreSearchQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Anticipated difficulty file 2')
        fig.suptitle('Search formulation (Per-earch)', fontsize=16)
        fig.subplots_adjust(bottom=1, top=5)
            
        #Content selection
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=5)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Actual difficulty
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.ContentSelectionQual[0][0],self.ContentSelectionQual[1][0], self.ContentSelectionQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Actual difficulty')
        #Actual difficulty
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.ContentSelectionQual2[0][0],self.ContentSelectionQual2[1][0], self.ContentSelectionQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Actual difficulty file 2')
        #Text presentation quality
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.ContentSelectionQual[0][1],self.ContentSelectionQual[1][1], self.ContentSelectionQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Text presentation quality')
         #Text presentation quality
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.ContentSelectionQual2[0][1],self.ContentSelectionQual2[1][1], self.ContentSelectionQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Text presentation quality file 2')
        #average number of docs view/search
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.ContentSelectionQual[0][2],self.ContentSelectionQual[1][2], self.ContentSelectionQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('average number of docs view/search')
        #average number of docs view/search
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.ContentSelectionQual2[0][2],self.ContentSelectionQual2[1][2], self.ContentSelectionQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('average number of docs view/search file 2')
        #Usefulness of search results
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.ContentSelectionQual[0][3],self.ContentSelectionQual[1][3], self.ContentSelectionQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Usefulness of search results')
        #Usefulness of search results
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.ContentSelectionQual2[0][3],self.ContentSelectionQual2[1][3], self.ContentSelectionQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Usefulness of search results file 2')
        #Text relevance
        ax5=fig.add_subplot(spec4[4,0])
        ax5.pie([self.ContentSelectionQual[0][4],self.ContentSelectionQual[1][4], self.ContentSelectionQual[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('average number of docs view/search')
        #Text relevance
        ax5=fig.add_subplot(spec4[4,1])
        ax5.pie([self.ContentSelectionQual2[0][4],self.ContentSelectionQual2[1][4], self.ContentSelectionQual2[2][4]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax5.set_title('average number of docs view/search file 2')
        fig.suptitle('Content selection', fontsize=16)
        fig.subplots_adjust(bottom=1, top=5)
        
        
        
        #Interaction with content
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=4)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Cognitively engaged
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.InteractionContentQual[0][0],self.InteractionContentQual[1][0], self.InteractionContentQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Cognitively engaged')
        #Cognitively engaged
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.InteractionContentQual2[0][0],self.InteractionContentQual2[1][0], self.InteractionContentQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Cognitively engaged file 2')
        #Suggestions skills
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.InteractionContentQual[0][1],self.InteractionContentQual[1][1], self.InteractionContentQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Suggestions skills')
        #Suggestions skills
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.InteractionContentQual2[0][1],self.InteractionContentQual2[1][1], self.InteractionContentQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Suggestions skills file 2')
        #System undersdanting input
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.InteractionContentQual[0][2],self.InteractionContentQual[1][2], self.InteractionContentQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('System undersdanting input')
        #System undersdanting input
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.InteractionContentQual2[0][2],self.InteractionContentQual2[1][2], self.InteractionContentQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('System undersdanting input file 2')
        #Average leve of satisfaction
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.InteractionContentQual[0][3],self.InteractionContentQual[1][3], self.InteractionContentQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Anticipated difficulty')
        #Average leve of satisfaction
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.InteractionContentQual2[0][3],self.InteractionContentQual2[1][3], self.InteractionContentQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Anticipated difficulty file 2')
        fig.suptitle('Interaction with content', fontsize=16)
        fig.subplots_adjust(bottom=1, top=5)
        
        #Post Search
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=4)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

            
        #Search success
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.PostSearchQual[0][0],self.PostSearchQual[1][0], self.PostSearchQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Search success')
        #Search success
        ax1=fig.add_subplot(spec4[0, 1])
        ax1.pie([self.PostSearchQual2[0][0],self.PostSearchQual2[1][0], self.PostSearchQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('Search success file 2')
        #Presentation of the results
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.PostSearchQual[0][1],self.PostSearchQual[1][1], self.PostSearchQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Presentation of the results')
        #Presentation of the results
        ax2=fig.add_subplot(spec4[1, 1])
        ax2.pie([self.PostSearchQual2[0][1],self.PostSearchQual2[1][1], self.PostSearchQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('Presentation of the results file 2')
        #Expansion of Knowledge
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.PostSearchQual[0][2],self.PostSearchQual[1][2], self.PostSearchQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Expansion of Knowledge')
        #Expansion of Knowledge
        ax3=fig.add_subplot(spec4[2, 1])
        ax3.pie([self.PostSearchQual2[0][2],self.PostSearchQual2[1][2], self.PostSearchQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('Expansion of Knowledge file 2')
        #Understanding about the topic
        ax4=fig.add_subplot(spec4[3, 0])
        ax4.pie([self.PostSearchQual[0][3],self.PostSearchQual[1][3], self.PostSearchQual[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Understanding about the topic')
        #Understanding about the topic
        ax4=fig.add_subplot(spec4[3, 1])
        ax4.pie([self.PostSearchQual2[0][3],self.PostSearchQual2[1][3], self.PostSearchQual2[2][3]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax4.set_title('Understanding about the topic file 2')
        fig.suptitle('Search success', fontsize=16)
        fig.subplots_adjust(bottom=1, top=5)
        
        
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
        
    #Knowledge gain
    def Knowledge_Gain(self, format, save='notActivated', alpha = 0.05):
        if  type(save) != str:alpha=save
        print('type of analysis: Quantitative')
        if format=='graph':
            plt.rcParams["figure.figsize"] = (16,8)
            fig= plt.figure()
            index = np.arange(3)
            width = 0.35
            #first bar chart/table

            ax1= fig.add_subplot(1,1,1)
            columns = ['quality of facts', 'interpretation', 'critiques']
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

            ax1.bar(index- width/2, mean[0], color=colorMean, width = 0.25)
            mean = self.KnowledgeGain2

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

            ax1.bar(index+ width/2, mean[0], color=colorMean, width = 0.25)

            ax1.axhline(y=3.5, color='black')
            ax1.set_xticks([])


            colorMean=[]
            mean2=[[]]    
            mean2[0].append(self.KnowledgeGain[0][0])
            mean2[0].append(self.KnowledgeGain2[0][0])
            mean2[0].append(self.KnowledgeGain[0][1])
            mean2[0].append(self.KnowledgeGain2[0][1])
            mean2[0].append(self.KnowledgeGain[0][2])
            mean2[0].append(self.KnowledgeGain2[0][2])
            roundMean=[round(mean, 1) for mean in mean2[0]]
            for i in range(len(roundMean)):
                if roundMean[i]<3.5:
                    colorMean.append('#DC2209')
                if roundMean[i]==3.5:
                    colorMean.append('#EED238')
                if roundMean[i]>3.5:
                    colorMean.append('#1CCD00')
            columns = ['quality of facts f1','f2', 'interpretation f1','f2', 'critiques f1', 'f2']        
            ytable = ax1.table(cellText=mean2, colLabels=columns,rowLabels=['Mean'], loc='bottom')

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
            
        if format=='tab':
            if (not self.diff_size or self.size<=30) and not self.parameter:
                print('type of test: t-test')
                print("level of significance: "+str(alpha))
                if self.link=='independant':
                    print('Sample: independant')
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.KnowledgeGainData[0],self.KnowledgeGainData2[0], equal_var=self.diff_size)
                    one_tailed_p_value=p_value
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.KnowledgeGainData[1],self.KnowledgeGainData2[1], equal_var=self.diff_size)
                    one_tailed_p_value2=p_value
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_ind(self.KnowledgeGainData[2],self.KnowledgeGainData2[2], equal_var=self.diff_size)
                    one_tailed_p_value3=p_value
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    
                    #je veux tester si ils sont significment different et si oui si ils lequel est le meilleur        
                    df = {'categories': ['quality', 'interpretation', 'critiques'], 'file 1': [self.KnowledgeGain[0][0], self.KnowledgeGain[0][1],self.KnowledgeGain[0][2]], 'file 2': [self.KnowledgeGain2[0][0],self.KnowledgeGain2[0][1],self.KnowledgeGain2[0][2]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                    tab = pd.DataFrame(data=df)
                    display (tab)
                    
                    
                if self.link=='dependant':
                    print('Sample: dependant')
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.KnowledgeGainData[0],self.KnowledgeGainData2[0])
                    one_tailed_p_value=p_value/2
                    if one_tailed_p_value>alpha:
                        res1 = 'No'
                        best1 = '/'
                    else:
                        res1 = 'Yes'
                        if t_value<0:
                            best1 = 'file 2'
                        else:
                            best1 = 'file 1'
                    ###   
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.KnowledgeGainData[1],self.KnowledgeGainData2[1])
                    one_tailed_p_value2=p_value/2
                    if one_tailed_p_value2>alpha:
                        res2 = 'No'
                        best2 = '/'
                    else:
                        res2 = 'Yes'
                        if t_value<0:
                            best2 = 'file 2'
                        else:
                            best2 = 'file 1'
                    ###
                    ### t test 
                    t_value,p_value=stats.ttest_rel(self.KnowledgeGainData[2],self.KnowledgeGainData2[2])
                    one_tailed_p_value3=p_value/2
                    if one_tailed_p_value3>alpha:
                        res3 = 'No'
                        best3 = '/'
                    else:
                        res3 = 'Yes'
                        if t_value<0:
                            best3 = 'file 2'
                        else:
                            best3 = 'file 1'
                    ###
                    
                    #je veux tester si ils sont significment different et si oui si ils lequel est le meilleur
                    df = {'categories': ['quality', 'interpretation', 'critiques'], 'file 1': [self.KnowledgeGain[0][0], self.KnowledgeGain[0][1],self.KnowledgeGain[0][2]], 'file 2': [self.KnowledgeGain2[0][0],self.KnowledgeGain2[0][1],self.KnowledgeGain2[0][2]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                    tab = pd.DataFrame(data=df)
                    display (tab)
                    
            
            else:
                print('type of test: z-test')
                ###z test quality
                ztest_Score, p_value= ztest(x1=self.KnowledgeGainData[0], x2=self.KnowledgeGainData2[0], value=0)
                one_tailed_p_value=p_value
                if one_tailed_p_value<alpha:
                    res1 = 'No'
                    best1 = '/'
                else:
                    res1 = 'Yes'
                    if ztest_Score<0:
                        best1 = 'file 2'
                    else:
                        best1 = 'file 1'
                ###   
                ### z test interpretation
                ztest_Score, p_value= ztest(x1=self.KnowledgeGainData[1], x2=self.KnowledgeGainData2[1], value=0)
                one_tailed_p_value2=p_value
                if one_tailed_p_value2<alpha:
                    res2 = 'No'
                    best2 = '/'
                else:
                    res2 = 'Yes'
                    if ztest_Score<0:
                        best2 = 'file 2'
                    else:
                        best2 = 'file 1'
                ###
                ### z test critiques
                ztest_Score, p_value= ztest(x1=self.KnowledgeGainData[2], x2=self.KnowledgeGainData2[2], value=0)
                one_tailed_p_value3=p_value
                if one_tailed_p_value3<alpha:
                    res3 = 'No'
                    best3 = '/'
                else:
                    res3 = 'Yes'
                    if ztest_Score<0:
                        best3 = 'file 2'
                    else:
                        best3 = 'file 1'
                ###
                df = {'categories': ['quality', 'interpretation', 'critiques'], 'file 1': [self.KnowledgeGain[0][0], self.KnowledgeGain[0][1],self.KnowledgeGain[0][2]], 'file 2': [self.KnowledgeGain2[0][0],self.KnowledgeGain2[0][1],self.KnowledgeGain2[0][2]], 'p-value': [one_tailed_p_value, one_tailed_p_value2, one_tailed_p_value3], 'significant diff': [res1, res2, res3], 'best file': [best1, best2, best3]}
                tab = pd.DataFrame(data=df)
                display (tab)
                
                
            #pdf download
            if save=='pdf':
                print("loading pdf...")
                path=str(os.path.join(Path.home(), "Downloads", "Knowledge_Gain.pdf"))
                pathAct = str(os.path.join(self.to_mod, "Knowledge_Gain.pdf"))    
                dfi.export(tab, pathAct)
                doc = aw.Document()
                builder = aw.DocumentBuilder(doc)
                builder.insert_image(pathAct)
                doc.save(path)
                print("pdf downloaded !")

    #Knowledge gain
    def Knowledge_Gain_Qual_Analysis(self, save='display'):
        
        print('type of analysis: Qualitative')
        plt.rcParams["figure.figsize"] = (20,8)
        fig= plt.figure()
        spec4 = fig.add_gridspec(ncols=2, nrows=3)
        anno_opts = dict(xy=(0.5, 0.5), xycoords='axes fraction',va='center', ha='center')

        coments = list(zip(self.KnowledgeGainQual[0],self.KnowledgeGainQual[1], self.KnowledgeGainQual[2]))
        df = pd.DataFrame(coments, index =['quality of facts', 'interpretation', 'critiques'],columns =['Green', 'Yellow', 'Red'])
        
            
        #quality of facts
        ax1=fig.add_subplot(spec4[0, 0])
        ax1.pie([self.KnowledgeGainQual[0][0],self.KnowledgeGainQual[1][0], self.KnowledgeGainQual[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1.set_title('quality of facts file 1')
        #quality of facts
        ax1v2=fig.add_subplot(spec4[0, 1])
        ax1v2.pie([self.KnowledgeGainQual2[0][0],self.KnowledgeGainQual2[1][0], self.KnowledgeGainQual2[2][0]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax1v2.set_title('quality of facts file 2')
        #interpretation
        ax2=fig.add_subplot(spec4[1, 0])
        ax2.pie([self.KnowledgeGainQual[0][1],self.KnowledgeGainQual[1][1], self.KnowledgeGainQual[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2.set_title('interpretation file 1')
        #interpretation
        ax2v2=fig.add_subplot(spec4[1, 1])
        ax2v2.pie([self.KnowledgeGainQual2[0][1],self.KnowledgeGainQual2[1][1], self.KnowledgeGainQual2[2][1]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax2v2.set_title('interpretation file 2')      
        #critiques
        ax3=fig.add_subplot(spec4[2, 0])
        ax3.pie([self.KnowledgeGainQual[0][2],self.KnowledgeGainQual[1][2], self.KnowledgeGainQual[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3.set_title('critiques file 1')
        #critiques
        ax3v2=fig.add_subplot(spec4[2, 1])
        ax3v2.pie([self.KnowledgeGainQual2[0][2],self.KnowledgeGainQual2[1][2], self.KnowledgeGainQual2[2][2]],labels=['Positive','Neutral','Negative'], colors=['#1CCD00','#EED238','#DC2209'], autopct='%1.1f%%')
        ax3v2.set_title('critiques file 2')
        
        fig.subplots_adjust(bottom=4, top=6)
        
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
-format (String) : ‘tab’ to display the information in a table format or ‘graph’ to display the information in a graph format
-alpha (float): level of significance. Default=0.05


Software_Usability (format): Display results of software usability
[ex: MyFile.Software_Usability ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version
-format (String): ‘tab’ to display the information in a table format or ‘graph’ to display the information in a graph format
-alpha (float): level of significance. Default=0.05

Software_Usability_Coments (format): display comments on software usability
[ex: MyFile.Software_Usability_Coments ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version
-'WordCloud': display the information on a word cloud format

Searching_Learning (format): display information on the searching as learning questionnaire
[ex: MyFile.Searching_Learning ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version
-format (String) : ‘tab’ to display the information in a table format or ‘graph’ to display the information in a graph format
-alpha (float): level of significance. Default=0.05

Knowledge_Gain (format): display information on the knowledge gain questionnaire
[ex: MyFile.Knowledge_Gain ()]
Parameters: 
- save (String): ‘pdf’ to download the pdf version
-format (String) : ‘tab’ to display the information in a table format or ‘graph’ to display the information in a graph format
-alpha (float): level of significance. Default=0.05

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
        
    
    
        
    