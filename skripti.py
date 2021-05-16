import json
import numpy as np
from scipy import stats

# RADIO BUTTON ID'S
# 3 kuinka hyvin läsnä
# 6 tekninen kontribuutio
# 7 noudattiko aikatauluja
# 9 prosessin noudattaminen
# 11 prosessin kehittäminen
# 13 ryhmätyö
# 14 miten innokkaasti osallistui eteenpäinviemiseen
# 16 asiakastyöskentely
# 17 arvosanaehdotus

RADIO_ID = 6

with open("vertaispalaute.json", "r", encoding="utf-8") as jfile:
    data = np.array(json.load(jfile))

    
class StudentAnswers:
    def __init__(self, group, answers1, answers2):
        self.group = group
        self.fullname = str(answers1.get('student').get('first_names')) + " " + str(answers1.get('student').get('last_name'))
        self.experience = get_dict_by_id(answers1.get('answer_sheet'), 1, "answer")
        self.days_used_weekly = get_dict_by_id(answers1.get('answer_sheet'), 4, "answer")
        self.first_self_assessment = get_dict_by_id(answers1.get('answer_sheet'), RADIO_ID, "peers").get(self.fullname)
        
        if answers2:
            self.second_self_assessment = get_dict_by_id(answers2.get('answer_sheet'), RADIO_ID, "peers").get(self.fullname)
        else:
            self.second_self_assessment = False
        
        get_dict_by_id(answers1.get('answer_sheet'), 17, "peers").pop(self.fullname)
        self.first_peer_assessment = get_dict_by_id(answers1.get('answer_sheet'), RADIO_ID, "peers")
        
        if answers2:
            get_dict_by_id(answers2.get('answer_sheet'), 17, "peers").pop(self.fullname)
            self.second_peer_assessment = get_dict_by_id(answers2.get('answer_sheet'), RADIO_ID, "peers")
        else:
            self.second_peer_assessment = False

def get_dict_by_id(sheet, idnum, key):
    for x in sheet:
        if 'id' in x and x['id'] == idnum:
            return x[key]
    raise Exception('Could not find wanted id!')
        
answers = []
        
for i in range(1, data.size):
    group = data[i].get('group')
    for j in range(len(data[i].get('round1Answers'))):
        
        ans1 = data[i].get('round1Answers')[j]
        
        if len(data[i].get('round1Answers')) == len(data[i].get('round2Answers')):
            ans2 = data[i].get('round2Answers')[j]
        else:
            ans2 = {}
            
        answers.append(StudentAnswers(group, ans1, ans2))


first_peer_assessments = {}
second_peer_assessments = {}

first_self_assessments = {}
second_self_assessments = {}

for ans in answers:
    dictname = ans.fullname + " #" + str(ans.group.get('id'))
    
    first_self_assessments[dictname] = ans.first_self_assessment
    
    if ans.second_self_assessment:
        second_self_assessments[dictname] = ans.second_self_assessment
    
    for x in ans.first_peer_assessment:
        grade = ans.first_peer_assessment[x]
        
        if grade == 0:
            continue
        
        peername = x + " #" + str(ans.group.get('id'))
        
        if peername in first_peer_assessments:
            first_peer_assessments[peername].append(grade)
        else:
            first_peer_assessments[peername] = [grade]
    
    if ans.second_peer_assessment:
        for y in ans.second_peer_assessment:
            grade = ans.second_peer_assessment[y]
            
            if grade == 0:
                continue
            
            peername = y + " #" + str(ans.group.get('id'))
        
            if peername in second_peer_assessments:
                second_peer_assessments[peername].append(grade)
            else:
                second_peer_assessments[peername] = [grade]


first_pa_reduced = []
second_pa_reduced = []

pa_avg = []

for name, pa in first_peer_assessments.items():
    first_pa_reduced.extend(pa)
    if name in first_self_assessments:
        pa_avg.append(np.average(pa))

for name, pa in second_peer_assessments.items():
    second_pa_reduced.extend(pa)
    if name in second_self_assessments:
        pa_avg.append(np.average(pa))
    
both_pa_reduced = []
both_sa_reduced = []

both_pa_reduced = first_pa_reduced + second_pa_reduced
both_sa_reduced = list(first_self_assessments.values()) + list(second_self_assessments.values())

#print(len(both_pa_reduced))
#print(len(both_sa_reduced))
#print(stats.tstd(both_pa_reduced))
#print(stats.tstd(both_sa_reduced))

print(np.average(both_pa_reduced) - np.average(both_sa_reduced))
print((np.average(both_pa_reduced - np.average(both_sa_reduced))) / np.sqrt(((len(both_pa_reduced) - 1) * (stats.tstd(both_pa_reduced) ** 2) + (len(both_sa_reduced) - 1) * (stats.tstd(both_sa_reduced) ** 2)) / (len(both_pa_reduced) + len(both_sa_reduced) - 2)))
print((np.average(both_sa_reduced - np.average(both_pa_reduced))) / np.sqrt(((len(both_sa_reduced) - 1) * (stats.tstd(both_sa_reduced) ** 2) + (len(both_pa_reduced) - 1) * (stats.tstd(both_pa_reduced) ** 2)) / (len(both_sa_reduced) + len(both_pa_reduced) - 2)))

#print(stats.ttest_ind(both_pa_reduced, both_sa_reduced, equal_var = False))
#print(stats.ttest_ind(pa_avg, both_sa_reduced, equal_var = False))

print("----")
print(stats.mannwhitneyu(both_pa_reduced, both_sa_reduced, alternative='less'))
print(stats.mannwhitneyu(both_pa_reduced, both_sa_reduced, alternative='greater'))
print(stats.mannwhitneyu(both_pa_reduced, both_sa_reduced, alternative='two-sided'))

#print("----")
#print(stats.wilcoxon(pa_avg, both_sa_reduced, alternative='less'))
#print(stats.wilcoxon(pa_avg, both_sa_reduced, alternative='greater'))
#print(stats.wilcoxon(pa_avg, both_sa_reduced, alternative='two-sided'))
#print(np.average(both_pa_reduced) - np.average(both_sa_reduced))

print("----")
print(stats.pearsonr(pa_avg, both_sa_reduced))

#xsum = 0
#xsize = 0

#for i in range(10000):
#    res = stats.pearsonr(both_sa_reduced, np.random.choice(both_pa_reduced, len(both_sa_reduced)))
#    #if res[1] < 0.05:
#    xsum += res[0]
#    xsize += 1
#print(xsum / xsize)
#print(xsize)

#print(stats.pearsonr(both_sa_reduced, np.random.choice(both_pa_reduced, len(both_sa_reduced))))
