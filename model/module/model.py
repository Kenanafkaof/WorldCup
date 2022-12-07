import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from scipy.stats import linregress
from module.conversion import Database
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

class HistoricData:
    def __init__(self, teams):
        #digest the teams 
        self.teams = teams

    def get_data(self):
        #passing in the fifa world cup results csv to be read via the pandas dataframe 
        results = pd.read_csv('dependencies/results.csv')
        results.head()

        #iteration in order to create home and away team for fixtures as well as points 
        winner = []
        for i in range (len(results['home_team'])):
            if results ['home_score'][i] > results['away_score'][i]:
                winner.append(results['home_team'][i])
            elif results['home_score'][i] < results ['away_score'][i]:
                winner.append(results['away_team'][i])
            else:
                winner.append('Draw')
        results['winning_team'] = winner

        results['goal_difference'] = np.absolute(results['home_score'] - results['away_score']) #takes the goal difference 

        results.head()
    
        df_teams_home = results[results['home_team'].isin(self.teams)]
        df_teams_away = results[results['away_team'].isin(self.teams)]
        df_teams = pd.concat((df_teams_home, df_teams_away))
        df_teams.drop_duplicates()
        df_teams.count()

        year = []
        for row in df_teams['date']:
            year.append(int(row[:4]))
        
        df_teams['match_year'] = year
        df_all_teams = df_teams[df_teams.match_year >= 1930]
        df_all_teams.head()

        df_all_teams = df_teams.drop(['date', 'home_score', 'away_score', 'tournament', 'city', 'country',
                                    'goal_difference', 'match_year'], axis = 1)

        df_all_teams.head()

        df_all_teams = df_all_teams.reset_index(drop=True)
        df_all_teams.loc[df_all_teams.winning_team == df_all_teams.home_team,'winning_team']=2    #sets the winning teams column to 2 for a win (points)
        df_all_teams.loc[df_all_teams.winning_team == 'Draw', 'winning_team'] = 1                 #sets a draw to only one point 
        df_all_teams.loc[df_all_teams.winning_team == df_all_teams.away_team, 'winning_team']=0   #sets a loss to 0 points for the team  

        df_all_teams.head()

        return df_all_teams     #returns the updated teams columns and df 

    def train_data(self, df_all_teams):
        final = pd.get_dummies(df_all_teams, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team']) #going to drop the column titles and generate data to implement into the training model

        X = final.drop(['winning_team'], axis=1)
        y = final["winning_team"]
        y = y.astype('int')

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)       #tested various random states and test sizes and this yielded the best results. Future research and testing could lead to different variables

        final.head()
        logreg = LogisticRegression(solver='lbfgs', max_iter=45000) #I chose to implement a LogisticRegression as it yielded the best results in regardings to the training set. This should also be further analyzed in future work. 
        logreg.fit(X_train, y_train)
        score = logreg.score(X_train, y_train)  #prints the scores of the model    
        score2 = logreg.score(X_test, y_test)   #prints the scores of the model

        return final, logreg

    def get_fixtures(self, final):
        #next, digesting the fixtures into the model based on the initial fixtures as well as the addition of the individual rankings of the team 
        fixtures = pd.read_csv('dependencies/fixtures.csv')
        ranking = pd.read_csv('dependencies/fifa_rankings.csv', encoding = 'latin-1')           #needed different encoding in order to parse this file 
        pred_set = []

        fixtures.insert(1, 'first_position', fixtures['Home Team'].map(ranking.set_index('Team')['Position']))      #insert into the df the first and second -> based on score put the corresponding position 
        fixtures.insert(2, 'second_position', fixtures['Away Team'].map(ranking.set_index('Team')['Position']))     

        fixtures = fixtures.iloc[:48, :]    #parse the data and split it 
        fixtures.tail()

        for index, row in fixtures.iterrows():                                      #iterate through and append into JSON data based on the score -> if away then move the column/row configuration and insert the data
            if row['first_position'] < row['second_position']:
                pred_set.append({'home_team': row['Home Team'], 'away_team': row['Away Team'], 'winning_team': None})
            else:
                pred_set.append({'home_team': row['Away Team'], 'away_team': row['Home Team'], 'winning_team': None})
                
        pred_set = pd.DataFrame(pred_set)       #create a new prediction cleaned up data set with the above iteration and insert the appended data
        backup_pred_set = pred_set

        pred_set.head()

        pred_set = pd.get_dummies(pred_set, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team'])      #configure test data 

        # Add missing columns compared to the model's training dataset
        missing_cols = set(final[0].columns) - set(pred_set.columns)
        for c in missing_cols:
            pred_set[c] = 0
        pred_set = pred_set[final[0].columns]

        # Remove winning team column
        pred_set = pred_set.drop(['winning_team'], axis=1)

        pred_set.head()
        #create the prediction iterations based on the scikit models -> use that to iterate through each fixture and predict 
        predictions = final[1].predict(pred_set)
        winners = []
        for i in range(fixtures.shape[0]):
            #print pairing 
            print(backup_pred_set.iloc[i, 1] + ' and ' + backup_pred_set.iloc[i, 0])
            #if the prediction is a win, then get the odds of the victory 
            if predictions[i] == 2:
                print('Winner: ' + backup_pred_set.iloc[i, 0] + ' chance: ' + '%.3f'%(final[1].predict_proba(pred_set)[i][2]))
                if backup_pred_set.iloc[i, 0] not in winners:
                    winners.append(backup_pred_set.iloc[i, 0])
            #draw is equal to 1 as stipulated prior 
            elif predictions[i] == 1:
                print('Draw')
            #predict the probability of a loss -> if the prediction is 0 
            elif predictions[i] == 0:
                print('Winner: ' + backup_pred_set.iloc[i, 0] + ' chance: ' + '%.3f'%(final[1].predict_proba(pred_set)[i][2]))
                if backup_pred_set.iloc[i, 0] not in winners:
                    winners.append(backup_pred_set.iloc[i, 0])
            print('Probability of Draw: ', '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
            print('Probability of ' + backup_pred_set.iloc[i,1] + ' winning: ', '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
            print('')
            #Insert the data into the database based on the prediction -> this is used for frontend 
            Database().insert_probability(backup_pred_set.iloc[i,0], '%.3f'%(final[1].predict_proba(pred_set)[i][2]), backup_pred_set.iloc[i, 1], '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
        return winners, ranking
    
    def move_on_structure(self, winners, divide, table):
        #take the teams and put them into the group moving structure in order to clean data and create new fixtures 
        group_finals = []
        k = 0
        l = 1
        data = len(winners)/divide
        for nation in range(int(data)):
            try:
                Database().insert_fixtures(winners[k], winners[l], table)
                together_group = winners[k], winners[l]
                group_finals.append(together_group)
                l += 2
                k += 2
            except IndexError:
                pass
        return group_finals

    def clean_and_predict(self, matches, final, logreg): 
        ranking = pd.read_csv('dependencies/fifa_rankings.csv', encoding = 'latin-1')  
        ranking.set_index('Team')['Position']
        new_set = pd.DataFrame(ranking)
        #Initialization of auxiliary list for data cleaning
        positions = []

        for match in matches:
            positions.append(new_set[new_set['Team']==match[0]].squeeze()['Position'])
            positions.append(new_set[new_set['Team']==match[1]].squeeze()['Position'])

        for row in matches:
            positions.append

        #Creating the DataFrame for prediction
        pred_set = []

        #initalizaing iterators for while loop
        i = 0
        j = 0

        # 'i' will be the iterator for the 'position' list, and 'j' for the list of matches (list of tuples)

        while i < len(positions):
            dict1 = {}

            # if position of first team is better, he will be the 'home' team, and vice-versa
            if positions[i] > positions[i + 1]:
                dict1.update({'home_team': matches[j][0], 'away_team': matches[j][1]})
            else:
                dict1.update({'home_team': matches[j][1], 'away_team': matches[j][0]})

            #Append updated dictionary to the list, that will later be converted into a DataFrame
            pred_set.append(dict1)
            i += 2
            j += 1

        #Covert list into DataFrame
        pred_set = pd.DataFrame(pred_set)
        backup_pred_set = pred_set

        #Get dummy variables and drop winning_team column
        pred_set = pd.get_dummies(pred_set, prefix = ['home_team', 'away_team'], columns = ['home_team', 'away_team'])

        #Add missing columns compared to the model's training dataset
        missing_cols2 = set(final.columns) - set(pred_set.columns)
        for c in missing_cols2:
            pred_set[c] = 0
        pred_set = pred_set[final.columns]

        #Remove winning team column
        pred_set = pred_set.drop(['winning_team'], axis=1)

        #Prediction
        predictions = logreg.predict(pred_set)
        winners = []
        
        for i in range(len(pred_set)):
            print(backup_pred_set.iloc[i,1] + ' and ' + backup_pred_set.iloc[i,0])
            if predictions[i] == 2:
                print('Winner: ' + backup_pred_set.iloc[i,1])
                if backup_pred_set.iloc[i, 1] not in winners:
                    winners.append(backup_pred_set.iloc[i, 1])

            elif predictions[i] == 1:
                print('Draw')
                if '%.3f'%(logreg.predict_proba(pred_set)[i][2]) > '%.3f'%(logreg.predict_proba(pred_set)[i][2]):
                    winners.append(backup_pred_set.iloc[i, 1])
                else:
                    winners.append(backup_pred_set.iloc[i, 0])
            elif predictions[i] == 0:
                print('Winner: ' + backup_pred_set.iloc[i, 1])
                if backup_pred_set.iloc[i, 1] not in winners:
                    winners.append(backup_pred_set.iloc[i, 1])
            print('Probability of ' + backup_pred_set.iloc[i,1] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set)[i][2]))
            print('Probability of Draw: ', '%.3f'%(logreg.predict_proba(pred_set)[i][1]))
            print('Probaility of ' + backup_pred_set.iloc[i, 0] + ' winning: ', '%.3f'%(logreg.predict_proba(pred_set)[i][0]))
            print('')
            Database().insert_probability(backup_pred_set.iloc[i,1], '%.3f'%(logreg.predict_proba(pred_set)[i][2]), backup_pred_set.iloc[i, 0], '%.3f'%(logreg.predict_proba(pred_set)[i][0]))
        
        return winners
