import pandas as pd
import numpy as np
import openpyxl
import sys

##Function creation to schedule non-overlapping 15 minute breaks
def schedule_15(aim, index, shift):
    ##Creation of utility variables
    plus = True
    counter = .25
    ##While loop checks for the closest possible break to the goal
    while np.isin(poss_15, aim).any() == False and counter < 2:
        if plus == True:
            aim = aim + counter
            plus = False
        else:
            aim = aim - counter
            plus = True
        counter += .25
    ##Sets specified break to the closest possible break
    hoursdf.loc[index, shift] = aim
    ##Returns break time to delete it from the poss_15 list
    return aim

##Function creation to schedule non-overlapping 15 minute breaks
def schedule_30(aim, index, shift):
    ##See above
    plus = True
    ogAim = aim
    counter = .25
    while np.isin(poss_30, aim).any() == False and counter < 2:
        if plus == True:
            aim = aim + counter
            plus = False
        else:
            aim = aim - counter
            plus = True
        counter += .25
    hoursdf.loc[index, shift] = aim
    return aim

##This file takes one argument in the command line, being the path to the daily lineup
book = openpyxl.load_workbook(sys.argv[1], data_only=True)

##Opens worksheet with lineup
ws = book['MSA']

##Creates dataframe with lineup
df = pd.DataFrame(ws.values)

##Data cleaning
df = df.rename(columns={0: "na", 1: "Dept", 2: "Name", 3: "Shift"})
df = df.drop(columns=['na'])

df = df.dropna()

##Finds customer service and ops stock shifts only (Frontline shifts)
frontdf = df.loc[df['Dept'] == 'Customer Service']
stockdf = df.loc[df['Dept'] == 'Ops Stock']

##Combines the two
csdf = pd.concat([frontdf, stockdf])

##Split the shift start from end
newdf = csdf["Shift"].str.split("-", n = 1, expand = True)
csdf["Start"] = newdf[0]
csdf["End"] = newdf[1]
csdf.drop(columns =["Shift"], inplace = True)

##Creation of new columns with numerical shift start and end
csdf["Shift Start"] = ""
csdf["Shift End"] = ""

##Creates numerical representation of start and end time and puts into 24 hour format
for index, row in csdf.iterrows():
    temp = row["Start"].split(":")
    
    if row["Start"][-1] == "P" and int(temp[0]) != 12:
        hour = int(temp[0]) + 12
    else:
        hour = int(temp[0])
    if temp[1][:2] == "30":
        hour = hour + .5
    row["Shift Start"] = hour
    
    temp2 = row["End"].split(":")
    
    if row["End"][-1] == "P":
        hour = int(temp2[0]) + 12
    else:
        hour = int(temp2[0])
    if temp2[1][:2] == "30":
        hour = hour + .5
        
    row["Shift End"] = hour

##Calculates shift length from shift start and end
csdf["Shift Length"] = csdf["Shift End"] - csdf["Shift Start"]

##Creation of new dataframe which combines shifts that may be seperated
hoursdf = pd.DataFrame()
hoursdf = csdf.groupby("Name").agg({'Shift Start':'min','Shift End':'max','Shift Length': 'sum'}).reset_index()

##Creating empty columns for breaks
hoursdf['1st 15'] = 0
hoursdf['1st Lunch'] = 0
hoursdf['2nd 15'] = 0
hoursdf['2nd Lunch'] = 0
hoursdf['3rd 15'] = 0

##Creation of arrays holding possible breaks, breaks will be deleted as they are used 
poss_15 = np.arange(8, 21, .25)
poss_30 = np.arange(8, 21, .25)

##Iterates through each person and gives them applicable breaks based upon how long they are working

for index, row in hoursdf.iterrows():
    print(f'Processing...' + row['Name'])
    
    if row["Shift Length"] < 3.5:
        print('Sad, no breaks for ' + row['Name'])

    elif row["Shift Length"] <= 5:
        goal = row['Shift Start'] + (row['Shift Length']/2)
        fif = schedule_15(goal, index, '1st 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))   

    elif row["Shift Length"] <= 6:
        goal = row['Shift Start'] + 2
        fif = schedule_15(goal, index, '1st 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))
        
        goal_30 = row['Shift End'] - 2
        thi = schedule_30(goal_30, index, '1st Lunch')
        poss_30 = np.delete(poss_30, np.where(poss_30 == thi))

    elif row['Shift Length'] <= 10:
        goal_15 = row['Shift Start'] + 2
        fif = schedule_15(goal_15, index, '1st 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))
        
        goal_30 = row['Shift Start'] + (row['Shift Length']/2)
        thi = schedule_30(goal_30, index, '1st Lunch')
        poss_30 = np.delete(poss_30, np.where(poss_30 == thi))
        
        goal_15two = row['Shift End'] - 2
        fif = schedule_15(goal_15two, index, '2nd 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))
        
    elif row['Shift Length'] > 10:
        goal_15 = row['Shift Start'] + 2
        fif = schedule_15(goal_15, index, '1st 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))
        
        goal_30 = row['Shift Start'] + 4
        thi = schedule_30(goal_30, index, '1st Lunch')
        poss_30 = np.delete(poss_30, np.where(poss_30 == thi))
        
        goal_15two = row['Shift Start'] + (row['Shift Length']/2)
        fif = schedule_15(goal_15two, index, '2nd 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))
        
        goal_30two = row['Shift End'] - 4
        thi = schedule_30(goal_30two, index, '2nd Lunch')
        poss_30 = np.delete(poss_30, np.where(poss_30 == thi))
        
        goal_15three = row['Shift End'] - 2
        fif = schedule_15(goal_15three, index, '3rd 15')
        poss_15 = np.delete(poss_15, np.where(poss_15 == fif))

##Outputs break schedule
print(hoursdf)