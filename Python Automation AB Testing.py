# # Python Automation for AB Test

##import Packages
import pandas as pd
import math
import scipy.stats
from matplotlib import pyplot as plt
import numpy as np

##import data
# your file needs to be in the right file path
df_test2 = pd.read_csv(r'MTA AB Test2.csv')
df_rev= pd.read_csv(r'MTA AB Test2 Rev.csv')

# ### Data Check & Transformation
# #### Inspect DF Statistics

df_test2.describe()

df_test2

# #### Session Count By Date

df_test2.drop_duplicates(['Date','SessionID']).groupby(['Date'])['SessionID'].count()
df_test2=df_test2[pd.to_datetime(df_test2['Date'])>pd.to_datetime('2019-06-14')]
df_test2

# garbage collect, clears memory space for local machine efficiency
import gc
gc.collect()

# ### Z-score Calculation

# list all the metrics
metrics=['Bounced','SawProduct','AddedToCart','ReachedCheckout','Converted']
df_Result=pd.DataFrame(df_test2.drop_duplicates(['SessionID','ControlGroup']).groupby('TestGroup')['SessionID'].count())
df_Result.head(10)

# add aggregated metrics using a for loop

for metric in metrics:
    a=df_test2[df_test2[metric]==1].drop_duplicates(['SessionID','ControlGroup']).groupby('TestGroup')['SessionID'].count()
    a.name=metric
    df_Result=df_Result.join(a)

df_Result

def z_test_calculator(df,denominator,numerator):

    control_denominator=df.loc[0,denominator]
    var_denominator=df.loc[1,denominator]
    control_numerator=df.loc[0,numerator]
    var_numerator=df.loc[1,numerator]    
    
    #Rate
    control_rate=control_numerator/control_denominator

    var_rate=var_numerator/var_denominator
    
    #STD
    control_sd=math.sqrt(control_rate*(1-control_rate)/control_denominator)
    var_sd=math.sqrt(var_rate*(1-var_rate)/var_numerator)
    
    #z score
    z_score=(control_rate-var_rate)/math.sqrt(pow(control_sd,2)+pow(var_sd,2))
    
    #p value
    p_value=scipy.stats.norm.sf(abs(z_score))
    
    #lift
    perc_lift=(var_rate-control_rate)/control_rate
    abs_lift=(var_rate-control_rate)
    
    return (p_value,perc_lift,abs_lift)

z_test_calculator(df_Result,'SessionID','Converted')

z_test_calculator(df_Result,'SessionID','ReachedCheckout')

# ### Format output

KPIs=[('SessionID','ReachedCheckout')
      ,('SessionID','Converted')]

dic_final={}

for index in df_Result.index:
    j=0 
    if index!=0:
        df_each_group=df_Result.loc[[0,index],]
        df_each_group.index=[1,0]
        
        df_final=pd.DataFrame()
        
        for i in KPIs:
            result=z_test_calculator(df_each_group,i[0],i[1])
            df_final.loc[j,'denominator']=i[0]
            df_final.loc[j,'numerator']=i[1]
            df_final.loc[j,'p_value']=result[0]
            df_final.loc[j,'perc_lift']=result[1]
            df_final.loc[j,'abs_lift']=result[2]
            j=j+1
        dic_final['Variation '+str(index)]=df_final

dic_final['Variation 1']

dic_final.keys()

# ### Export to Excel

writer = pd.ExcelWriter('Test2 Session Overall Results.xlsx')
for key in dic_final.keys():
    dic_final[key].to_excel(writer,sheet_name=key)
writer.save()

# ### Granularity
# Set a variable for CUsID

granularity='CusID'

df_Result=pd.DataFrame(df_test2.drop_duplicates([granularity,'ControlGroup']).groupby('TestGroup')[granularity].count())

for metric in metrics:
    a=df_test2[df_test2[metric]==1].drop_duplicates([granularity,'ControlGroup']).groupby('TestGroup')[granularity].count()
    a.name=metric
    df_Result=df_Result.join(a)

KPIs_cus=[(granularity,'Bounced'),
      (granularity,'Converted'),
      (granularity,'AddedToCart'),
      (granularity,'ReachedCheckout'),
      (granularity,'SawProduct'),
      ('SawProduct','Bounced'),
      ('SawProduct','AddedToCart'),
      ('AddedToCart','ReachedCheckout'),
      ('ReachedCheckout','Converted')]

for index in df_Result.index:
    j=0
    if index!=0:
        df_each_group=df_Result.loc[[0,index],]
        df_each_group.index=[1,0]
        
        df_final=pd.DataFrame() 
        
        for i in KPIs_cus:
            result=z_test_calculator(df_each_group,i[0],i[1])
            df_final.loc[j,'denominator']=i[0]
            df_final.loc[j,'numerator']=i[1]
            df_final.loc[j,'p_value']=result[0]
            df_final.loc[j,'perc_lift']=result[1]
            df_final.loc[j,'abs_lift']=result[2]
            j=j+1
        dic_final['Variation'+str(index)]=df_final

df_Result

dic_final

# ### Cuts by Vistor Type

cut='VisitorTypeID'
granularity='SessionID'

df_test_data=df_test2.copy()

for p in set(df_test_data[cut]):
    # isolate each cut for aggregation
    df_test2=df_test_data[df_test_data[cut]==p]
    
    df_Result=pd.DataFrame(df_test2.groupby('TestGroup')[granularity].count())
    metrics=['Bounced','SawProduct','AddedToCart','ReachedCheckout','Converted']
    
    # create for loops within the loop for cuts
    for metric in metrics:
        a=df_test2[df_test2[metric]==1].drop_duplicates([granularity,'ControlGroup']).groupby('TestGroup')[granularity].count()
        a.name=metric
        df_Result=df_Result.join(a)

    KPIs=[(granularity,'Bounced'),
          (granularity,'Converted'),
          (granularity,'AddedToCart'),
          (granularity,'ReachedCheckout'),
          (granularity,'SawProduct'),
          ('SawProduct','Bounced'),
          ('SawProduct','AddedToCart'),
          ('AddedToCart','ReachedCheckout'),
          ('ReachedCheckout','Converted')]
    
    for index in df_Result.index:
        j=0
        if index!=0:
            df_each_group=df_Result.loc[[0,index],]
            df_each_group.index=[1,0]

            df_final=pd.DataFrame()

            for i in KPIs:
                result=z_test_calculator(df_each_group,i[0],i[1])
                df_final.loc[j,'denominator']=i[0]
                df_final.loc[j,'numerator']=i[1]
                df_final.loc[j,'p_value']=result[0]
                df_final.loc[j,'perc_lift']=result[1]
                df_final.loc[j,'abs_lift']=result[2]
                j=j+1
            dic_final['Variation'+str(index)+'cut'+str(p)]=df_final

dic_final

writer=pd.ExcelWriter('output'+cut+'.xlsx')
for key in dic_final.keys():
    dic_final[key].to_excel(writer, sheet_name=key)
writer.save()

# ### Continuous Variable Significance
# #### Mann-Whitney U Test

Control_Rev=df_rev[df_rev['TestGroup']==0]['TotalRev'].array
Var1_Rev=df_rev[df_rev['TestGroup']==1]['TotalRev'].array

Control_Rev

Var1_Rev

import scipy.stats as stats

stats.mannwhitneyu(Control_Rev,Var1_Rev)

# ## Visualizations
# ### Outliers

x=df_rev.loc[df_rev['ControlGroup']==1,'TotalRev'].apply(lambda x: math.sqrt(abs(x)))
n_bins=50
fig,ax=plt.subplots(figsize=(8,4))
n,bins,patches=ax.hist(x, n_bins,density=True,histtype='step',cumulative=True,label='Cumulative')

ax.grid(True)
ax.legend(loc='right')
ax.set_title('Cumulative step histograms')
ax.set_xlabel('Squared Total Revenue')
ax.set_ylabel('Likelihood of occurrence')

plt.show()

# get the 95th percentile of each group
P1=np.percentile(Control_Rev,95)
P2=np.percentile(Var1_Rev,95)

P1

P2

np.percentile(Control_Rev,[5,95])

stats.mannwhitneyu(Control_Rev[Control_Rev<P1],Var1_Rev[Var1_Rev<P2])

df_Result.loc[0,'Rev']=sum(Control_Rev[Control_Rev<P1])
df_Result.loc[1,'Rev']=sum(Var1_Rev[Var1_Rev<P2])
df_Result.loc[0,'Rev_sq']=sum(Control_Rev[Control_Rev<P1]**2)
df_Result.loc[1,'Rev_sq']=sum(Var1_Rev[Var1_Rev<P2]**2)

df_Result

z_test_calculator_continuous(df_Result,Converted,Rev,Rev_sq)

dic_rev_final={}
for index in df_Result.index:
    j=0
    if index!=0:
        df_each_group=df_Result.loc[[0,index],]
        df_each_group.index=[1,0]
        df_final=pd.DataFrame()
        result=z_test_calculator_continuous(df_each_group,'Converted','Rev','Rev_sq')
        df_final.loc[j,'denominator']='Converted'
        df_final.loc[j,'numerator']='Rev'
        df_final.loc[j,'p_value']=result[0]
        df_final.loc[j,'perc_lift']=result[1]
        df_final.loc[j,'abs_lift']=result[2]
        j=j+1
        dic_rev_final['Variation '+str(index)]= df_final

dic_rev_final

# ### Significance

numerator='Converted'
denominator='ReachedCheckout'

df_test_data=df_test2.copy() 
denominator_dailydata=df_test_data[df_test_data[denominator]==1].groupby(['Date','TestGroup'])['SessionID'].count()
numerator_dailydata=df_test_data[df_test_data[numerator]==1].groupby(['Date','TestGroup'])['SessionID'].count()
numerator_dailydata.name=numerator
denominator_dailydata.name=denominator

type(numerator_dailydata)

denominator_aggdailydata=denominator_dailydata.reset_index()
numerator_aggdailydata=numerator_dailydata.reset_index()

denominator_aggdailydata

# get cumulative value as days progress
denominator_aggdailydata[denominator]=denominator_aggdailydata.groupby('TestGroup')[denominator].cumsum()
numerator_aggdailydata[numerator]=numerator_aggdailydata.groupby('TestGroup')[numerator].cumsum()

numerator_aggdailydata

df_cumsum=pd.DataFrame()

# loop through every unique date
for date in df_test_data.drop_duplicates('Date')['Date'].tolist():
    # get data for current loop date
    df=denominator_aggdailydata[denominator_aggdailydata['Date']==date].set_index('TestGroup',drop=True)
    df=df.merge(numerator_aggdailydata[numerator_aggdailydata['Date']==date].set_index('TestGroup',drop=True)
                ,on='Date',left_index=True,right_index=True)
    
    sig_result=z_test_calculator(df,denominator, numerator)
    df_cumsum.loc[date,'Sig_Level']=1-sig_result[0]
    df_cumsum.loc[date,'Lift']=sig_result[1]

df_cumsum

ax = df_cumsum.sort_index()['Sig_Level'].plot(figsize=(15,5))
ax.axhline(y=0.95,linewidth=1,color='r')

ax = df_cumsum.sort_index()['Sig_Level'].plot(figsize=(15,5))
