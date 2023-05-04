import requests
from bs4 import BeautifulSoup
import pandas as pd

def generalQuery(dbn):
       # exclude charters
    if dbn[:2] == '84':
        schoolData = ['Charter alert' , '', '', '', '', '', '', '']
        return(schoolData)
    else:    
        # navigate to a school register page on NYCENet by last 4 characters of DBN
        # retrieve percentage breakdown of that school's SWD population
        # remove % sign from each percentage and return the numbers as a list of strings
        # data updated bimonthly from ATS, according to site
        url = 'https://www.nycenet.edu/PublicApps/register.aspx?s=' + dbn[2:]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        relatedServices = soup.find(id="ContentPlaceHolder1_dlstRegister_lblRelatedServicePercent_0").get_text()
        lessThan20 = soup.find(id="ContentPlaceHolder1_dlstRegister_lblSpecedSinglePercent_0").get_text()
        twentyOneTo59 = soup.find(id="ContentPlaceHolder1_dlstRegister_lblSpecedMultiPercent_0").get_text()
        moreThan60 = soup.find(id="ContentPlaceHolder1_dlstRegister_lblSpecedFTIntegratedPercent_0").get_text()
        selfContained = soup.find(id="ContentPlaceHolder1_dlstRegister_lblSpecedFTSelfPercent_0").get_text()
    
        # moving on to InsideSchools
        # there are no ids associated with the desired strings, but there is a pattern of "stat-title" divs followed by "stat-value" divs. If the former matches the desired string, store the contents of the corresponding "stat-value" div.
        # data purports to be from 2018 DOE publications
    
        url = 'https://insideschools.org/school/' + dbn
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        a = soup.find_all("div", class_="stat-title")
        b = soup.find_all("div", class_="stat-value")
        for title in a:
            if title.string.strip() == "Free or reduced priced lunch":
                frpl = b[a.index(title)].string.strip()
                break
            else:
                frpl = 'Not found'
        for title in a:
            if title.string.strip() == "Average daily attendance":
                avgDaily = b[a.index(title)].string.strip()
                break
            else:
                avgDaily = 'Not found' 
        for title in a:
            if title.string.strip() == "How many students miss 18 or more days of school?":
                absentees = b[a.index(title)].string.strip()
                break
            else:
                absentees = 'Not found'    
        # combine scraped data into a list, remove trailing % signs, and return
    
        schoolData = [s[:-1] for s in [relatedServices, lessThan20, twentyOneTo59, moreThan60, selfContained, frpl, avgDaily, absentees]]
        return(schoolData)

print("Testing on CSS...")
print(generalQuery('05M362'))

# Import CSV file with DBNs of target schools. Initialize empty list that will become a dataframe later.
df = pd.read_csv('C:\\Users\\teacher\\Documents\\schoolsfromdaniel.csv')
schoolData = []

# For each DBN in the CSV file, search portals.  
for i in range(df.shape[0]):
    dbn = df.at[i, 'DBN']
    print('Seeking data for school', dbn)
    newData = generalQuery(dbn)
    print('Found data:', newData)
    schoolData.append(newData)

df2 = pd.DataFrame(schoolData, columns=['Related Services Only', 'Less Than 20%', '21-59%', 'More Than 60%', 'Self-Contained', 'FRPL', 'Daily Attendance %', '% Missing 18+ Days'])

dfFinal = pd.concat([df, df2], axis=1)

print(dfFinal)
print('Sending to CSV...')
dfFinal.to_csv('C:\\Users\\teacher\\Documents\\schoolsfromdaniel.csv', index=None)



