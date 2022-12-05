import numpy as np
import pandas as pd
import matplotlib as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from scipy.stats import linregress
from module.conversion import Database
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

class HistoricData:
    def __init__(self, teams):
        self.teams = teams

    def get_data(self):
        results = pd.read_csv('dependencies/results.csv')
        results.head()

        winner = []
        for i in range (len(results['home_team'])):
            if results ['home_score'][i] > results['away_score'][i]:
                winner.append(results['home_team'][i])
            elif results['home_score'][i] < results ['away_score'][i]:
                winner.append(results['away_team'][i])
            else:
                winner.append('Draw')
        results['winning_team'] = winner

        #adding goal difference column
        results['goal_difference'] = np.absolute(results['home_score'] - results['away_score'])

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
        df_teams_1930 = df_teams[df_teams.match_year >= 1930]
        df_teams_1930.head()

        df_teams_1930 = df_teams.drop(['date', 'home_score', 'away_score', 'tournament', 'city', 'country',
                                    'goal_difference', 'match_year'], axis = 1)

        df_teams_1930.head()

        df_teams_1930 = df_teams_1930.reset_index(drop=True)
        df_teams_1930.loc[df_teams_1930.winning_team == df_teams_1930.home_team,'winning_team']=2
        df_teams_1930.loc[df_teams_1930.winning_team == 'Draw', 'winning_team']=1
        df_teams_1930.loc[df_teams_1930.winning_team == df_teams_1930.away_team, 'winning_team']=0

        df_teams_1930.head()

        return df_teams_1930

    def train_data(self, df_teams_1930):
        final = pd.get_dummies(df_teams_1930, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team'])

        X = final.drop(['winning_team'], axis=1)
        y = final["winning_team"]
        y = y.astype('int')

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        final.head()
        logreg = LogisticRegression(solver='lbfgs', max_iter=45000) #ensemble
        logreg.fit(X_train, y_train)
        score = logreg.score(X_train, y_train)
        score2 = logreg.score(X_test, y_test)


        print('Training set accuracy ', '%.3f'%(score))
        print('Test set accuracy ', '%.3f'%(score2))

        return final, logreg

    def get_fixtures(self, final):
        fixtures = pd.read_csv('dependencies/fixtures.csv')
        ranking = pd.read_csv('dependencies/fifa_rankings.csv', encoding = 'latin-1')
        # List for storing the group stage games
        pred_set = []

        # Create new columns with ranking position of each team
        fixtures.insert(1, 'first_position', fixtures['Home Team'].map(ranking.set_index('Team')['Position']))
        fixtures.insert(2, 'second_position', fixtures['Away Team'].map(ranking.set_index('Team')['Position']))

        # We only need the group stage games, so we have to slice the dataset
        fixtures = fixtures.iloc[:48, :]
        fixtures.tail()

        for index, row in fixtures.iterrows():
            if row['first_position'] < row['second_position']:
                pred_set.append({'home_team': row['Home Team'], 'away_team': row['Away Team'], 'winning_team': None})
            else:
                pred_set.append({'home_team': row['Away Team'], 'away_team': row['Home Team'], 'winning_team': None})
                
        pred_set = pd.DataFrame(pred_set)
        backup_pred_set = pred_set

        pred_set.head()

        pred_set = pd.get_dummies(pred_set, prefix=['home_team', 'away_team'], columns=['home_team', 'away_team'])

        # Add missing columns compared to the model's training dataset
        missing_cols = set(final[0].columns) - set(pred_set.columns)
        for c in missing_cols:
            pred_set[c] = 0
        pred_set = pred_set[final[0].columns]

        # Remove winning team column
        pred_set = pred_set.drop(['winning_team'], axis=1)

        pred_set.head()

        predictions = final[1].predict(pred_set)
        winners = []
        for i in range(fixtures.shape[0]):
            print(backup_pred_set.iloc[i, 1] + ' and ' + backup_pred_set.iloc[i, 0])
            if predictions[i] == 2:
                print('Winner: ' + backup_pred_set.iloc[i, 0] + ' chance: ' + '%.3f'%(final[1].predict_proba(pred_set)[i][2]))
                if backup_pred_set.iloc[i, 0] not in winners:
                    winners.append(backup_pred_set.iloc[i, 0])
            elif predictions[i] == 1:
                print('Draw')
            elif predictions[i] == 0:
                print('Winner: ' + backup_pred_set.iloc[i, 0] + ' chance: ' + '%.3f'%(final[1].predict_proba(pred_set)[i][2]))
                if backup_pred_set.iloc[i, 0] not in winners:
                    winners.append(backup_pred_set.iloc[i, 0])
            print('Probability of Draw: ', '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
            print('Probability of ' + backup_pred_set.iloc[i,1] + ' winning: ', '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
            print('')
            Database().insert_probability(backup_pred_set.iloc[i,0], '%.3f'%(final[1].predict_proba(pred_set)[i][2]), backup_pred_set.iloc[i, 1], '%.3f'%(final[1].predict_proba(pred_set)[i][1]))
        return winners, ranking
    
    def move_on_structure(self, winners, divide, table):
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
