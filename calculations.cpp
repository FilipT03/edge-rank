#include<iostream>
#include<fstream>
#include<map>
#include<cmath>
#include<ctime>
#include<pybind11/pybind11.h>
#include <unistd.h>

#define toStr(value) (string)py::str(value)
#define toFloat(value) (float)py::float_(value)

using namespace std;
namespace py = pybind11;

const float COMMENT_VALUE = 3, SHARE_VALUE = 8, FRIEND_VALUE = 30;
unordered_map<string,float> REACTION_VALUES = {
    {"hahas",  1.5f},
    {"sads",   1.2f},
    {"angrys", 1.2f},
    {"likes",  1   },
    {"loves",  2   },
    {"wows",   1.5f}};

struct status{
    string author;
    string datePublished;
};
struct comment{
    string statusId;
    string author;
    string datePublished;
};

unordered_map<string,status> statusesMap; // id is the statusId
unordered_map<string,comment> commentsMap;// id is the commentId

vector<map<string,float>> friendsAffinity; // same format as the python affinty graph.

py::list LoadSimple(string path){
    py::list result;
    
    string line;
    ifstream file (path);
    if (file.is_open())
    {
        getline(file,line);
        while (getline(file,line)){
            if(line.size() == 0)
                continue;
            for(int i=0;i<(int)line.size();i++){
                if(line[i] == ' ') continue;
                if(line[i] == '\n') continue;
                if(line[i] == '\t') continue;
                line = line.substr(i);
                break;
            }
            for(int i=(int)line.size()-1;i>=0;i--){
                if(line[i] == ' ') continue;
                if(line[i] == '\n') continue;
                if(line[i] == '\t') continue;
                line = line.substr(0, i+1);
                break;
            }
            py::list littleList;
            int last = 0;
            for (int i=0;i<(int)line.size();i++)
                if (line[i] == ','){
                    littleList.append(line.substr(last, i-last));
                    last = i+1;
                }
            littleList.append(line.substr(last, line.size()-last));    
            result.append(littleList);
        }
        file.close();
    }
    return result;
}

// 2021-12-26 18:47:01
time_t toTimeT(string date){
    setenv("TZ", "CET", 1);
    tzset();
    struct tm tm2;
    struct tm* timeinfo = &tm2;
    strptime(date.c_str(), "%Y-%m-%d %H:%M:%S", timeinfo);
    return mktime(timeinfo);
}
float timeRatio(string actionDate, int months = 36){
    int dif = difftime(time(0), toTimeT(actionDate));
    int baseDif = months * 2628000; // this is approximately one month in seconds
    
    float result; // time multiplier is smaller for older actions;
    if (months == 36) 
        result = max(0.05f, 1 - (float)dif / baseDif); // minimum 0.05 for affinity actions, over 3 years
    else
        result = max(0.001f, 1 - (float)dif / baseDif); // minimum 0.001 (1/1000) for popularity
    return result;
}
float timeRatio(py::detail::list_accessor actionDate, int months = 36){
    return timeRatio(toStr(actionDate), months);
}

py::dict GenerateAffinityGraph(py::list comments, py::list statuses, string sharesPath, string reactionsPath, string friendsPath, py::dict oldDict){
    py::list shares = LoadSimple(sharesPath);
    py::list reactions = LoadSimple(reactionsPath);
    py::list friends;
    if(friendsPath != "")
        friends = LoadSimple(friendsPath);

    py::dict result = oldDict;
    status tmpStatus;
    comment tmpComment;
    for(int i=0; i<(int)comments.size();i++){
        py::list comment = comments[i];
        tmpComment.statusId = py::str(comment[1]);
        tmpComment.author = py::str(comment[4]);
        tmpComment.datePublished = py::str(comment[5]);
        commentsMap[py::str(comment[0])] = tmpComment;
    }

    for(int i=0; i<(int)statuses.size();i++){
        py::list status = statuses[i];
        tmpStatus.author = py::str(status[5]);
        tmpStatus.datePublished = py::str(status[4]);
        statusesMap[py::str(status[0])] = tmpStatus;
    }

    for(auto item : commentsMap){
        py::dict userDict;
        if(result.contains(py::str(item.second.author)))
            userDict = result[py::str(item.second.author)];

        py::str statusAuthor = py::str(statusesMap[item.second.statusId].author);
        if(statusAuthor.equal(py::str(item.second.author)))
            continue;
        float oldValue = userDict.contains(statusAuthor) ? toFloat(userDict[statusAuthor]) : 0;
        userDict[statusAuthor] = oldValue + COMMENT_VALUE * timeRatio(item.second.datePublished);

        result[py::str(item.second.author)] = userDict;
    }

    for(int i=0; i<(int)shares.size();i++){
        py::list share = shares[i];
        py::dict userDict;

        if(result.contains(py::str(share[1])))
            userDict = result[py::str(share[1])];
        
        py::str statusAuthor = py::str(statusesMap[toStr(share[0])].author);
        if(statusAuthor.equal(py::str(share[1])))
            continue;
        float oldValue = userDict.contains(statusAuthor) ? toFloat(userDict[statusAuthor]) : 0;
        userDict[statusAuthor] = oldValue + SHARE_VALUE * timeRatio(share[2]);

        result[py::str(share[1])] = userDict;
    }

    for(int i=0; i<(int)reactions.size();i++){
        py::list reaction = reactions[i];
        py::dict userDict;

        if(result.contains(py::str(reaction[2])))
            userDict = result[py::str(reaction[2])];
        
        py::str statusAuthor = py::str(statusesMap[toStr(reaction[0])].author);
        if(statusAuthor.equal(py::str(reaction[2])))
            continue;
        float oldValue = userDict.contains(statusAuthor) ? toFloat(userDict[statusAuthor]) : 0;
        userDict[statusAuthor] = oldValue + REACTION_VALUES[toStr(reaction[1])] * timeRatio(reaction[3]);

        result[py::str(reaction[2])] = userDict;
    }

    if(friendsPath != "")
        for(int i=0; i<(int)friends.size();i++){
            py::list friendList = friends[i];
            py::dict userDict;
            if(result.contains(py::str(friendList[0])))
                userDict = result[py::str(friendList[0])];
            
            for(int j=2;j<(int)friendList.size();j++){   
                py::str newFriend = py::str(friendList[j]);
                if(newFriend.equal(py::str(friendList[0])))
                    continue;
                float oldValue = userDict.contains(newFriend) ? toFloat(userDict[newFriend]) : 0;
                userDict[newFriend] = oldValue + FRIEND_VALUE;
            }

            result[py::str(friendList[0])] = userDict;
        }
        
    return result;
}


py::dict GeneratePopularityMap(py::list statuses, py::dict oldMap){
    py::dict result = oldMap;
    for(int i=0; i<(int)statuses.size();i++){
        py::list status = statuses[i];
        float score = 0;
        score += toFloat(status[7])  * COMMENT_VALUE;
        score += toFloat(status[8])  * SHARE_VALUE;
        score += toFloat(status[9])  * REACTION_VALUES["likes"];
        score += toFloat(status[10]) * REACTION_VALUES["loves"];
        score += toFloat(status[11]) * REACTION_VALUES["wows"];
        score += toFloat(status[12]) * REACTION_VALUES["hahas"];
        score += toFloat(status[13]) * REACTION_VALUES["sads"];
        score += toFloat(status[14]) * REACTION_VALUES["angrys"];

        score *= timeRatio(status[4], 1);

        result[py::str(status[0])] = py::make_tuple(status[5], score);
    }
    return result;
}

/*map<string, int> encodeMap;
map<int, string> decodeMap;
int nextId = 1;

int toInt(string s){
    if(encodeMap[s] != 0)
        return encodeMap[s];
    else {
        encodeMap[s] = nextId++;
        return encodeMap[s];
    }
}
py::str toPyInt(string s){
    return py::str(s);
    //return py::int_(toInt(s));
}
py::str toPyInt(py::detail::list_accessor s){
    return py::str(s);
    //return py::int_(toInt((string)py::str(s)));
}
string toString(int id){
    return decodeMap[id];
}*/
/*
void process_mem_usage(double& vm_usage, double& resident_set)
{
    vm_usage     = 0.0;
    resident_set = 0.0;

    // the two fields we want
    unsigned long vsize;
    long rss;
    {
        std::string ignore;
        std::ifstream ifs("/proc/self/stat", std::ios_base::in);
        ifs >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore
                >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore >> ignore
                >> ignore >> ignore >> vsize >> rss;
    }

    long page_size_kb = sysconf(_SC_PAGE_SIZE) / 1024; // in case x86-64 is configured to use 2MB pages
    vm_usage = vsize / 1024.0;
    resident_set = rss * page_size_kb;
    
        // double vm, rss;
        // process_mem_usage(vm, rss);
        // cout<< "Generate"<<endl;
        // cout << fixed << "VM: " << vm << "; RSS: " << rss << endl;
    
}*/